"""Mahrukh: an independent, local-first Flask storefront."""
from functools import wraps
from pathlib import Path
from datetime import timedelta
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from urllib.parse import quote, urlsplit
from flask import Flask, abort, flash, g, jsonify, redirect, render_template, request, session, url_for, send_from_directory
from werkzeug.security import check_password_hash
from commerce import install_commerce, launch_gaps
from boutique import install_boutique
from catalog import OCCASIONS, FABRICS, MEASUREMENTS, empty_details, decode_details, form_details, validate_details, missing_facts, decode_translations, form_translations, validate_translations, missing_translations
from i18n import install_i18n, t

ROOT = Path(__file__).resolve().parent
CATEGORIES = ['Unstitched', 'Stitched / Pret', 'Luxury Formals', 'Abayas', 'Festive Wear']
SIZES = ['XS', 'S', 'M', 'L', 'XL', '2XL', '3XL', 'Custom Unstitched']
ART = ['emerald-pret', 'rose-unstitched', 'midnight-abaya', 'ruby-lehenga', 'ivory-formal', 'indigo-pret', 'saffron-festive', 'plum-formal']


def create_app(test_config=None):
    app = Flask(__name__)
    instance = Path(os.environ.get('MAHRUKH_INSTANCE', str(ROOT / 'instance'))).resolve()
    config_path = instance / 'config.json'
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    app.config.update(SECRET_KEY=config.get('secret_key'), ADMIN_HASH=config.get('admin_hash', ''),
                      SELLER_PHONE=config.get('seller_phone', ''), DATABASE=str(instance / 'mahrukh.sqlite3'),
                      SESSION_COOKIE_NAME='mahrukh_session', SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE='Lax', PERMANENT_SESSION_LIFETIME=timedelta(days=30),
                      MAX_CONTENT_LENGTH=25 * 1024 * 1024, MAX_FORM_MEMORY_SIZE=128 * 1024, MAX_FORM_PARTS=100,
                      SESSION_COOKIE_SECURE=os.environ.get('MAHRUKH_SECURE_COOKIES') == '1',
                      TRUSTED_HOSTS=[h.strip() for h in os.environ.get('MAHRUKH_TRUSTED_HOSTS','').split(',') if h.strip()] or None)
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY'] or not app.config['ADMIN_HASH']:
        raise RuntimeError('Run python setup.py first to configure Mahrukh.')
    Path(app.config['DATABASE']).parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    install_i18n(app)

    def db():
        if 'db' not in g:
            g.db = sqlite3.connect(app.config['DATABASE'], timeout=10)
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(error):
        connection = g.pop('db', None)
        if connection:
            connection.close()

    with app.app_context():
        db().executescript((ROOT / 'schema.sql').read_text())
        # Keep legacy artwork-only samples editable, but out of the live catalog.
        db().execute("UPDATE products SET active=0 WHERE images LIKE '%/static/art/%'")
        db().commit()

    def csrf():
        if 'csrf' not in session:
            session['csrf'] = secrets.token_urlsafe(32)
        return session['csrf']

    @app.before_request
    def protect_forms():
        # Urdu policy characters expand when URL-encoded. Keep customer forms
        # small while accepting the editor's four documented 10k-text limits.
        form_limit = 1024 * 1024 if request.path == '/admin/settings' else 128 * 1024
        if request.path == '/admin/settings':
            request.max_form_memory_size = form_limit
        if request.method == 'POST' and not request.path.startswith('/admin/product/') and request.content_length and request.content_length > form_limit:
            abort(413)
        if session.get('admin') and time.time() - session.get('admin_since',0) > 4 * 3600:
            session.pop('admin',None)
        if request.method == 'POST':
            supplied = request.form.get('csrf_token', '')
            if not supplied or not hmac.compare_digest(supplied, session.get('csrf', '')):
                abort(400, t('This form expired. Reload the page and try again.'))

    @app.after_request
    def headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' https:; style-src 'self'; script-src 'self'; connect-src 'self'; base-uri 'none'; object-src 'none'; frame-ancestors 'none'; form-action 'self'"
        response.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
        if request.endpoint != 'static':
            response.headers['Cache-Control'] = 'no-store'
        return response

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get('admin') or time.time() - session.get('admin_since',0) > 4 * 3600:
                session.pop('admin',None)
                return redirect(url_for('login'))
            return view(*args, **kwargs)
        return wrapped

    def product(pid):
        row = db().execute('SELECT * FROM products WHERE id=?', (pid,)).fetchone()
        if row is None:
            abort(404)
        item = dict(row)
        item['sizes'] = json.loads(item['sizes'])
        item['images'] = json.loads(item['images'])
        item['stock'] = {r['size']:r['quantity'] for r in db().execute('SELECT size,quantity FROM inventory WHERE product_id=?', (pid,))}
        facts = db().execute('SELECT data FROM product_details WHERE product_id=?', (pid,)).fetchone()
        item['details'] = decode_details(facts['data'] if facts else None)
        translated = db().execute('SELECT data FROM product_translations WHERE product_id=?', (pid,)).fetchone()
        item['translations'] = decode_translations(translated['data'] if translated else None)
        item['details']['translations'] = item['translations']
        item['edit_version'] = hmac.new(app.secret_key.encode(), json.dumps(item, sort_keys=True).encode(), hashlib.sha256).hexdigest()
        return item

    def cart_lines():
        lines = []
        for key, entry in session.get('cart', {}).items():
            row = db().execute('SELECT id FROM products WHERE id=? AND active=1', (entry['id'],)).fetchone()
            if not row:
                continue
            item = product(row['id'])
            if entry['size'] not in item['sizes']:
                continue
            lines.append(dict(key=key, product=item, size=entry['size'], quantity=entry['quantity'],
                              subtotal=item['price'] * entry['quantity']))
        return lines

    @app.context_processor
    def context():
        lines = cart_lines()
        return dict(categories=CATEGORIES, sizes=SIZES, art=ART, csrf_token=csrf,
                    occasions=OCCASIONS, fabrics=FABRICS, measurement_labels=MEASUREMENTS,
                    cart_count=sum(x['quantity'] for x in lines),
                    seller_ready=bool(settings()['whatsapp']))

    settings, checkout_context = install_commerce(app, db, admin_required, cart_lines, product)

    related_pieces = install_boutique(app, db, product, settings)

    app.jinja_env.filters['pkr'] = lambda value: f'PKR {value:,.0f}'

    @app.get('/health')
    def health():
        db().execute('SELECT 1').fetchone()
        return {'ok': True, 'service': 'mahrukh'}

    @app.get('/')
    def index():
        query = request.args.get('q', '').strip()[:100]
        category = request.args.get('category', '')
        sort = request.args.get('sort', 'featured')
        sort = sort if sort in ('featured', 'price-low', 'price-high') else 'featured'
        order = {'featured': 'products.id DESC', 'price-low': 'price ASC, products.id DESC', 'price-high': 'price DESC, products.id DESC'}[sort]
        category = category if category in CATEGORIES else ''
        occasion = request.args.get('occasion', '')
        occasion = occasion if occasion in OCCASIONS else ''
        fabric_family = request.args.get('fabric_family', '')
        fabric_family = fabric_family if fabric_family in FABRICS else ''
        size = request.args.get('size', '')
        size = size if size in SIZES else ''
        budget = request.args.get('budget', '')
        if budget and (not budget.isascii() or not budget.isdigit() or len(budget)>8 or not 1 <= int(budget) <= 10000000):
            abort(400, t('Enter a maximum price from PKR 1 to 10,000,000.'))
        clauses, params = ['active=1'], []
        if query:
            clauses.append("(name LIKE ? OR fabric LIKE ? OR description LIKE ? OR EXISTS (SELECT 1 FROM json_tree(facts.data) WHERE type='text' AND value LIKE ?) OR EXISTS (SELECT 1 FROM json_tree(translated.data) WHERE type='text' AND value LIKE ?))")
            params.extend([f'%{query}%'] * 5)
        if category:
            clauses.append('category=?'); params.append(category)
        if occasion:
            clauses.append("EXISTS (SELECT 1 FROM json_each(facts.data, '$.occasions') WHERE value=?)"); params.append(occasion)
        if fabric_family:
            clauses.append("json_extract(facts.data, '$.fabric_family')=?"); params.append(fabric_family)
        if budget:
            clauses.append('price<=?'); params.append(int(budget))
        if size:
            clauses.append('EXISTS (SELECT 1 FROM inventory WHERE product_id=products.id AND size=? AND quantity>0 AND size IN (SELECT value FROM json_each(products.sizes)))'); params.append(size)
        rows = db().execute('SELECT products.*, facts.data AS details_json, translated.data AS translations_json, (SELECT coalesce(sum(quantity),0) FROM inventory WHERE product_id=products.id AND size IN (SELECT value FROM json_each(products.sizes))) AS stock_total FROM products LEFT JOIN product_details AS facts ON facts.product_id=products.id LEFT JOIN product_translations AS translated ON translated.product_id=products.id WHERE ' + ' AND '.join(clauses) + ' ORDER BY ' + order, params).fetchall()
        filter_values = dict(q=query, category=category, occasion=occasion, fabric_family=fabric_family, size=size, budget=budget, sort=sort)
        chips = []
        for key, label in [('q', query), ('category', t(category)), ('occasion', t(OCCASIONS.get(occasion,''))), ('fabric_family', t(fabric_family)), ('size', size), ('budget', t('Up to PKR {amount}', amount=f'{int(budget):,}') if budget else '')]:
            if filter_values[key]:
                remaining = {k:v for k,v in filter_values.items() if k!=key and v}
                chips.append(dict(label=label, url=url_for('index', **remaining)+'#collection'))
        products = []
        for row in rows:
            translated = decode_translations(row['translations_json'])
            details = decode_details(row['details_json'])
            details['translations'] = translated
            products.append(dict(row, images=json.loads(row['images']), details=details, translations=translated))
        return render_template('index.html', chips=chips, products=products,
                               query=query, selected=category, sort=sort, filters=dict(occasion=occasion, fabric_family=fabric_family, size=size, budget=budget), filtered=bool(query or category or occasion or fabric_family or size or budget))

    @app.get('/our-roots')
    def roots():
        return render_template('roots.html')

    @app.get('/fabric-and-fit')
    def fit_guide():
        return render_template('fit_guide.html')

    @app.get('/product/<int:pid>')
    def detail(pid):
        item = product(pid)
        if not item['active']:
            abort(404)
        selected_size = request.args.get('size', '')
        selected_size = selected_size if selected_size in item['sizes'] else ''
        return render_template('product.html', item=item, related=related_pieces(item), selected_size=selected_size, available_sizes=[s for s in item['sizes'] if item['stock'].get(s,0)>0])

    @app.route('/cart', methods=['GET', 'POST'])
    def cart():
        if request.method == 'POST':
            items = session.get('cart', {}).copy()
            action = request.form.get('action', 'add')
            if action == 'clear':
                items = {}
            else:
                try:
                    pid = int(request.form.get('id', '0'))
                    quantity = int(request.form.get('quantity', '1'))
                except ValueError:
                    abort(400, t('Invalid item or quantity.'))
                size = request.form.get('size', '')
                key = f'{pid}:{size}'
                if action == 'remove' or (action == 'update' and quantity == 0):
                    items.pop(key, None)
                else:
                    item = product(pid)
                    if not item['active'] or size not in item['sizes'] or not 1 <= quantity <= 10:
                        abort(400, t('Choose an available size and a quantity from 1 to 10.'))
                    if action not in ('add', 'update'):
                        abort(400)
                    new_quantity = quantity + (items.get(key, {}).get('quantity', 0) if action == 'add' else 0)
                    if new_quantity > 10 or (key not in items and len(items) >= 20):
                        abort(400, t('Limit: 10 per size and 20 different selections per bag.'))
                    if new_quantity > item['stock'].get(size,0):
                        abort(409, t('That quantity is not available in this size. Please choose another size or contact us.'))
                    items[key] = dict(id=pid, size=size, quantity=new_quantity)
            session['cart'] = items
            session['checkout_token'] = secrets.token_urlsafe(24)
            if request.headers.get('X-Mahrukh-Drawer') != '1':
                return redirect(url_for('cart'), code=303)
        lines = cart_lines()
        cart_notice = ''
        current = session.get('cart', {})
        valid_keys = {line['key'] for line in lines}
        if len(valid_keys) != len(current):
            session['cart'] = {key:entry for key,entry in current.items() if key in valid_keys}
            session['checkout_token'] = secrets.token_urlsafe(24)
            cart_notice = t('Unavailable selections were removed from your bag. Please review the updated total.')
        template = 'cart_contents.html' if request.headers.get('X-Mahrukh-Drawer') == '1' else 'cart.html'
        response = app.make_response(render_template(template, lines=lines, cart_notice=cart_notice, total=sum(x['subtotal'] for x in lines), **checkout_context(lines)))
        response.headers['X-Cart-Count'] = str(sum(x['quantity'] for x in lines))
        return response

    @app.route('/admin/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            # Persistent, process-independent throttle for this single-seller local app.
            now = int(time.time())
            row = db().execute('SELECT failures, blocked_until FROM login_limit WHERE id=1').fetchone()
            if row['blocked_until'] > now:
                abort(429, 'Too many attempts. Wait five minutes before trying again.')
            if check_password_hash(app.config['ADMIN_HASH'], request.form.get('password', '')):
                db().execute('UPDATE login_limit SET failures=0, blocked_until=0 WHERE id=1')
                db().commit()
                cart = session.get('cart',{})
                order_owner = session.get('order_owner')
                saved = session.get('saved', [])
                session.clear()
                session['cart'] = cart
                session['saved'] = saved
                if order_owner: session['order_owner'] = order_owner
                session['admin'] = True
                session['admin_since'] = int(time.time())
                session.permanent = True
                return redirect(url_for('admin'), code=303)
            failures = (0 if row['blocked_until'] else row['failures']) + 1
            db().execute('UPDATE login_limit SET failures=?, blocked_until=? WHERE id=1',
                         (failures, now + 300 if failures >= 5 else 0))
            db().commit()
            flash('Incorrect password.', 'error')
        return render_template('login.html')

    @app.post('/admin/logout')
    @admin_required
    def logout():
        session.pop('admin', None)
        session.pop('admin_since', None)
        session.pop('csrf', None)
        session.permanent = False
        return redirect(url_for('index'), code=303)

    @app.get('/admin')
    @admin_required
    def admin():
        return render_template('admin.html', gaps=launch_gaps(settings()), pending=db().execute("SELECT count(*) FROM orders WHERE status='pending'").fetchone()[0], products=db().execute('SELECT * FROM products ORDER BY id DESC').fetchall())

    @app.get('/admin/insights')
    @admin_required
    def insights():
        rows = [product(r['id']) for r in db().execute('SELECT id FROM products WHERE active=1 ORDER BY id DESC')]
        checks = [dict(item=p, missing=missing_facts(p)) for p in rows]
        counts = dict(db().execute('SELECT status,count(*) FROM orders GROUP BY status').fetchall())
        paid = db().execute("SELECT coalesce(sum(total),0) FROM orders WHERE payment_status='paid'").fetchone()[0]
        return render_template('insights.html', checks=checks, counts=counts, paid=paid, ready=sum(not c['missing'] for c in checks))

    @app.route('/admin/product/new', methods=['GET', 'POST'])
    @app.route('/admin/product/<int:pid>', methods=['GET', 'POST'])
    @admin_required
    def edit(pid=None):
        item = product(pid) if pid is not None else dict(name='', category=CATEGORIES[0], price='', compare_price='',
                    fabric='', description='', sizes=['Custom Unstitched'], images=[], active=1, illustration=0, stock={}, details=empty_details(), translations={})
        if request.method == 'POST':
            try:
                db().execute('BEGIN IMMEDIATE')
                if pid is not None and not hmac.compare_digest(request.form.get('edit_version',''), product(pid)['edit_version']):
                    abort(409, 'This product or its stock changed. Reload the editor before saving to avoid overwriting a newer order or edit.')
                price = int(request.form.get('price', ''))
                compare = int(request.form.get('compare_price') or 0)
                if not 1 <= price <= 10_000_000 or compare < 0 or compare > 10_000_000 or (compare and compare <= price):
                    raise ValueError('Prices must be whole PKR; original price must exceed the selling price.')
                chosen_sizes = request.form.getlist('sizes')
                images = [x.strip() for x in request.form.get('images', '').splitlines() if x.strip()]
                uploaded = []
                for upload in request.files.getlist('photos'):
                    if not upload.filename: continue
                    data = upload.read(4 * 1024 * 1024 + 1)
                    ext = 'jpg' if data.startswith(b'\xff\xd8\xff') else ('png' if data.startswith(b'\x89PNG\r\n\x1a\n') else ('webp' if data[:4] == b'RIFF' and data[8:12] == b'WEBP' else ''))
                    if not ext or len(data) > 4 * 1024 * 1024:
                        raise ValueError('Upload JPG, PNG or WebP photographs up to 4 MB each.')
                    name_on_disk = secrets.token_hex(16) + '.' + ext
                    uploaded.append((name_on_disk, data))
                    images.append('/media/' + name_on_disk)
                if not images or len(images) > 6:
                    raise ValueError('Provide between one and six image paths.')
                for image in images:
                    parsed = urlsplit(image)
                    remote = parsed.scheme == 'https' and parsed.netloc and not parsed.username and not parsed.password
                    local = bool(re.fullmatch(r'/media/[a-f0-9]{32}\.(jpg|png|webp)', image)) and ((Path(app.config['DATABASE']).parent / 'uploads' / image.split('/')[-1]).is_file() or any(n == image.split('/')[-1] for n, _ in uploaded))
                    if not local and (not remote or parsed.path.lower().endswith('.svg') or len(image) > 1000):
                        raise ValueError('Use an HTTPS product image URL for an actual photograph, not a decorative SVG.')
                category = request.form.get('category', '')
                name = request.form.get('name', '').strip()
                fabric = request.form.get('fabric', '').strip()
                description = request.form.get('description', '').strip()
                if category not in CATEGORIES or not chosen_sizes or any(s not in SIZES for s in chosen_sizes):
                    raise ValueError('Choose a category and at least one valid size.')
                if not name or len(name) > 100 or not fabric or len(fabric) > 200 or len(description) > 3000:
                    raise ValueError('Provide a name (1–100 characters), fabric (1–200), and description (up to 3000).')
                stock = {size: int(request.form.get('stock_' + size) or 0) for size in chosen_sizes}
                if any(q < 0 or q > 100000 for q in stock.values()): raise ValueError('Stock must be from 0 to 100,000 per size.')
                details = validate_details(form_details(request.form, chosen_sizes), chosen_sizes)
                translations = validate_translations(form_translations(request.form, item['translations']))
                folder = Path(app.config['DATABASE']).parent / 'uploads'
                folder.mkdir(exist_ok=True, mode=0o700)
                for filename, data in uploaded:
                    (folder / filename).write_bytes(data)
                    (folder / filename).chmod(0o600)
                values = (name, category, price, compare, fabric, description, json.dumps(chosen_sizes), json.dumps(images),
                          int('active' in request.form), 0)
                if pid is None:
                    cursor = db().execute('INSERT INTO products (name,category,price,compare_price,fabric,description,sizes,images,active,illustration) VALUES (?,?,?,?,?,?,?,?,?,?)', values)
                    pid = cursor.lastrowid
                else:
                    db().execute('UPDATE products SET name=?,category=?,price=?,compare_price=?,fabric=?,description=?,sizes=?,images=?,active=?,illustration=? WHERE id=?', (*values, pid))
                db().execute('INSERT INTO product_details(product_id,data) VALUES(?,?) ON CONFLICT(product_id) DO UPDATE SET data=excluded.data', (pid, json.dumps(details)))
                db().execute('INSERT INTO product_translations(product_id,data) VALUES(?,?) ON CONFLICT(product_id) DO UPDATE SET data=excluded.data', (pid, json.dumps(translations, ensure_ascii=False)))
                db().executemany('INSERT INTO inventory(product_id,size,quantity) VALUES(?,?,?) ON CONFLICT(product_id,size) DO UPDATE SET quantity=excluded.quantity', [(pid,size,q) for size,q in stock.items()])
                db().commit()
                flash('Product saved.', 'success')
                return redirect(url_for('admin'), code=303)
            except (ValueError, TypeError) as exc:
                db().rollback()
                flash(str(exc), 'error')
                item = dict(request.form, sizes=request.form.getlist('sizes'), images=request.form.get('images', '').splitlines(), active='active' in request.form, illustration='illustration' in request.form, stock={s:request.form.get('stock_' + s,0) for s in SIZES}, edit_version=request.form.get('edit_version',''), details=form_details(request.form, request.form.getlist('sizes')), translations=form_translations(request.form, item['translations']))
        return render_template('edit.html', item=item, pid=pid, translation_gaps=missing_translations(item))

    @app.post('/admin/product/<int:pid>/delete')
    @admin_required
    def delete(pid):
        db().execute('DELETE FROM products WHERE id=?', (pid,))
        db().execute('DELETE FROM inventory WHERE product_id=?', (pid,))
        db().execute('DELETE FROM product_details WHERE product_id=?', (pid,))
        db().execute('DELETE FROM product_translations WHERE product_id=?', (pid,))
        db().commit()
        flash('Product deleted.', 'success')
        return redirect(url_for('admin'), code=303)

    @app.get('/media/<filename>')
    def media(filename):
        if not re.fullmatch(r'[a-f0-9]{32}\.(jpg|png|webp)', filename): abort(404)
        return send_from_directory(Path(app.config['DATABASE']).parent / 'uploads', filename)

    for status in (400, 404, 409, 413, 429, 503):
        app.register_error_handler(status, lambda error: (render_template('error.html', error=error), error.code))
    return app
