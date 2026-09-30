"""Seller configuration, inventory reservations and private order records.

Hosted payments are manually verified; no card data or provider secrets are stored.
"""
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps
import hashlib
import hmac
import json
import re
import secrets
from urllib.parse import quote, urlsplit
from flask import abort, flash, redirect, render_template, request, session, url_for

SOCIALS = {'instagram': ('Instagram', ('instagram.com',)),
           'facebook': ('Facebook', ('facebook.com',)),
           'tiktok': ('TikTok', ('tiktok.com',)),
           'youtube': ('YouTube', ('youtube.com', 'youtu.be'))}
PROVIDERS = {'safepay': ('Safepay', ('getsafepay.com', 'safepay.pk', 'safepay.com.pk')),
             'paypal': ('PayPal', ('paypal.com', 'paypal.me'))}
POLICIES = {'shipping': 'Shipping & delivery', 'returns': 'Returns & refunds',
            'privacy': 'Privacy & cookies', 'terms': 'Terms of sale'}
DEFAULTS = dict(business_name='', business_address='', support_email='', whatsapp='',
    support_hours='', instagram='', facebook='', tiktok='', youtube='',
    announcement='Timeless style · Everyday you', shipping_fee=250, free_shipping_at=0,
    dispatch_note='', service_cities='', cod=True, transfer=False, transfer_details='',
    hosted=False, provider='safepay', merchant_eligible=False, accepting_orders=False,
    tax_note='', registration='', shipping='', returns='', privacy='', terms='', updated_at='')
STATUSES = ('pending', 'confirmed', 'dispatched', 'completed', 'cancelled')
PAYMENT_STATUSES = ('unpaid', 'paid', 'refunded')


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def safe_url(value, domains):
    """Only HTTPS links on exact provider domains or their subdomains."""
    try:
        u = urlsplit(value)
        host = (u.hostname or '').lower()
        return (u.scheme == 'https' and not u.username and not u.password and
                u.port in (None, 443) and len(value) <= 1000 and
                not any(c.isspace() or ord(c) < 32 for c in value) and
                any(host == d or host.endswith('.' + d) for d in domains))
    except ValueError:
        return False


def launch_gaps(s):
    gaps = []
    for key, label in [('business_name','Business name'),('business_address','Business contact address'),
                       ('whatsapp','WhatsApp number'),('support_email','Support email'),
                       ('dispatch_note','Delivery estimate'),('service_cities','Delivery cities'),
                       ('tax_note','Tax disclosure'), *POLICIES.items()]:
        if not s[key]: gaps.append(label)
    if not any(s[k] for k in ('cod','transfer','hosted')): gaps.append('At least one payment method')
    return gaps


def validate_settings(form):
    s = DEFAULTS.copy()
    bools = ('cod','transfer','hosted','merchant_eligible','accepting_orders')
    for k in s:
        if k in bools: s[k] = k in form
        elif k in ('shipping_fee','free_shipping_at'):
            try: s[k] = int(form.get(k, '0'))
            except ValueError: raise ValueError('Delivery amounts must be whole PKR.')
            if not 0 <= s[k] <= 1000000: raise ValueError('Delivery amounts must be between 0 and 1,000,000 PKR.')
        else:
            s[k] = form.get(k, '').strip()
            if len(s[k]) > (10000 if k in POLICIES else 2000): raise ValueError('A setting is too long.')
    s['whatsapp'] = re.sub(r'[\s+()-]', '', s['whatsapp'])
    if s['whatsapp'] and not re.fullmatch(r'[1-9]\d{9,14}', s['whatsapp']):
        raise ValueError('Use a WhatsApp number with country code, such as 923001234567.')
    if s['support_email'] and not re.fullmatch(r'[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+', s['support_email']):
        raise ValueError('Enter a valid support email address.')
    for k, (label, domains) in SOCIALS.items():
        if s[k] and not safe_url(s[k], domains): raise ValueError(f'Use an HTTPS {label} profile link on its official domain.')
    if s['provider'] not in PROVIDERS: raise ValueError('Choose a supported payment-link provider.')
    if s['transfer'] and not s['transfer_details']: raise ValueError('Add your merchant bank / Easypaisa / JazzCash payment instructions.')
    if s['hosted'] and not s['merchant_eligible']: raise ValueError('Confirm your merchant account is eligible and approved before enabling payment links.')
    if s['accepting_orders'] and launch_gaps(s): raise ValueError('Before opening orders, complete: ' + ', '.join(launch_gaps(s)))
    s['updated_at'] = now()
    return s


def install_commerce(app, db, admin_required, cart_lines, product):
    def settings():
        if not hasattr(request, '_shop_settings'):
            row = db().execute('SELECT data FROM shop_settings WHERE id=1').fetchone()
            s = DEFAULTS.copy()
            s['whatsapp'] = app.config['SELLER_PHONE']
            if row: s.update(json.loads(row['data']))
            request._shop_settings = s
        return request._shop_settings

    def shipping(total, s):
        return 0 if s['free_shipping_at'] and total >= s['free_shipping_at'] else s['shipping_fee']

    def quote_hash(lines, s):
        payload = json.dumps([[x['product']['id'], x['size'], x['quantity'], x['product']['price'], x['product']['name'], x['product']['fabric'], x['product']['description'], x['product']['details']] for x in lines], sort_keys=True)
        payload += json.dumps(s, sort_keys=True)
        return hmac.new(app.secret_key.encode(), payload.encode(), hashlib.sha256).hexdigest()

    def checkout_context(lines):
        s = settings()
        owner()
        subtotal = sum(x['subtotal'] for x in lines)
        session.setdefault('checkout_token', secrets.token_urlsafe(24))
        return dict(shipping=shipping(subtotal, s), grand_total=subtotal + shipping(subtotal, s),
                    checkout_token=session['checkout_token'], quote_hash=quote_hash(lines, s))

    @app.context_processor
    def shop_context():
        s = settings()
        return dict(shop=s, social_links=[(k, label, s[k]) for k, (label, _) in SOCIALS.items() if s[k]],
                    whatsapp_url=('https://wa.me/' + s['whatsapp'] + '?text=' + quote('Assalam-o-alaikum! I would like some help with Mahrukh.')) if s['whatsapp'] else '',
                    policy_names=POLICIES, provider_names={k:v[0] for k,v in PROVIDERS.items()},
                    seller_ready=bool(s['whatsapp']), shop_ready=s['accepting_orders'] and not launch_gaps(s))

    @app.route('/admin/settings', methods=['GET','POST'])
    @admin_required
    def shop_settings():
        s = settings()
        if request.method == 'POST':
            try:
                s = validate_settings(request.form)
                db().execute('INSERT INTO shop_settings(id,data) VALUES(1,?) ON CONFLICT(id) DO UPDATE SET data=excluded.data', (json.dumps(s),))
                db().commit()
                flash('Shop settings saved. Your storefront is updated immediately.', 'success')
                return redirect(url_for('shop_settings'), code=303)
            except ValueError as exc:
                flash(str(exc), 'error')
                # Keep the seller's draft, including unchecked boxes, after a validation error.
                s = {**DEFAULTS, **request.form.to_dict()}
                for k in ('cod','transfer','hosted','merchant_eligible','accepting_orders'): s[k] = k in request.form
        return render_template('settings.html', settings=s, gaps=launch_gaps(s), socials=SOCIALS)

    @app.get('/contact')
    def contact(): return render_template('contact.html')

    @app.get('/policies/<kind>')
    def policy(kind):
        if kind not in POLICIES: abort(404)
        return render_template('policy.html', kind=kind, title=POLICIES[kind], content=settings()[kind])

    def owner():
        session.setdefault('order_owner', secrets.token_urlsafe(32))
        return session['order_owner']

    def read_order(reference):
        row = db().execute('SELECT * FROM orders WHERE reference=?', (reference,)).fetchone()
        if not row or (not session.get('admin') and not hmac.compare_digest(row['owner'], session.get('order_owner',''))): abort(404)
        order = dict(row)
        for k in ('items','policies','merchant'): order[k] = json.loads(order[k])
        return order

    @app.post('/checkout')
    def checkout():
        s = settings()
        token = request.form.get('checkout_token','')
        if not token or not hmac.compare_digest(token, session.get('checkout_token','')): abort(400, 'Reload your bag before submitting this order.')
        # A duplicate POST returns the original receipt, even if the bag was cleared.
        old = db().execute('SELECT reference FROM orders WHERE request_id=? AND owner=?', (token, owner())).fetchone()
        if old: return redirect(url_for('order_detail', reference=old['reference']), code=303)
        if not s['accepting_orders'] or launch_gaps(s): abort(503, 'Ordering is paused. Please contact Mahrukh for help.')
        if request.form.get('agree') != 'yes': abort(400, 'Please read and accept the terms and privacy notice.')
        details = {k: ' '.join(request.form.get(k,'').split()) for k in ('name','city','contact','address')}
        if not all(details.values()) or any(len(v)>300 for v in details.values()): abort(400, 'Complete your name, phone, city and address (up to 300 characters each).')
        if not re.fullmatch(r'\+?[\d ()-]{7,30}', details['contact']): abort(400, 'Enter a valid contact phone number.')
        cities = [x.strip().casefold() for x in s['service_cities'].splitlines() if x.strip()]
        if details['city'].casefold() not in cities: abort(400, 'Please choose one of our listed delivery cities.')
        method = request.form.get('payment_method','')
        if method not in ('cod','transfer','hosted') or not s[method]: abort(400, 'Choose an available payment method.')
        connection = db()
        try:
            connection.execute('BEGIN IMMEDIATE')
            # Recheck after acquiring the writer lock: two simultaneous clicks create one order.
            old = connection.execute('SELECT reference FROM orders WHERE request_id=? AND owner=?', (token, owner())).fetchone()
            if old:
                connection.rollback()
                return redirect(url_for('order_detail', reference=old['reference']), code=303)
            lines = cart_lines()
            if not lines or len(lines) != len(session.get('cart',{})): abort(409, 'An item changed availability. Review your bag before ordering.')
            # Read current settings while locked; quotes cannot silently adopt new prices/policies.
            row = connection.execute('SELECT data FROM shop_settings WHERE id=1').fetchone()
            if row: s = {**DEFAULTS, **json.loads(row['data'])}
            if not hmac.compare_digest(request.form.get('quote_hash',''), quote_hash(lines,s)): abort(409, 'Product details, prices, delivery or shop details changed. Review your bag and submit again.')
            source = hmac.new(app.secret_key.encode(), (request.remote_addr or '').encode(), hashlib.sha256).hexdigest()
            recent = connection.execute("SELECT count(*) FROM orders WHERE source_hash=? AND created_at > strftime('%Y-%m-%dT%H:%M:%S', 'now', '-10 minutes')", (source,)).fetchone()[0]
            if recent >= 5: abort(429, 'Too many recent orders. Please wait ten minutes or contact the shop.')
            items = []
            for line in lines:
                p = line['product']
                changed = connection.execute('UPDATE inventory SET quantity=quantity-? WHERE product_id=? AND size=? AND quantity>=?', (line['quantity'],p['id'],line['size'],line['quantity'])).rowcount
                if not changed: abort(409, f"{p['name']} in {line['size']} is no longer available in that quantity. Please update your bag.")
                items.append(dict(id=p['id'],name=p['name'],size=line['size'],quantity=line['quantity'],price=p['price'],subtotal=line['subtotal'],fabric=p['fabric'],description=p['description'],details=p['details']))
            subtotal = sum(x['subtotal'] for x in items)
            delivery = shipping(subtotal,s)
            ref = 'MH-' + secrets.token_hex(6).upper()
            merchant = {k:s[k] for k in ('business_name','business_address','support_email','whatsapp','registration','tax_note','dispatch_note','transfer_details','provider')}
            connection.execute('''INSERT INTO orders(reference,request_id,owner,source_hash,name,contact,city,address,items,subtotal,shipping,total,payment_method,provider,policies,merchant,created_at,updated_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', (ref,token,owner(),source,details['name'],details['contact'],details['city'],details['address'],json.dumps(items),subtotal,delivery,subtotal+delivery,method,s['provider'],json.dumps({k:s[k] for k in POLICIES}),json.dumps(merchant),now(),now()))
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        session['cart'] = {}
        return redirect(url_for('order_detail', reference=ref), code=303)

    @app.get('/orders')
    def my_orders():
        rows = db().execute('SELECT reference,total,status,created_at FROM orders WHERE owner=? ORDER BY id DESC LIMIT 100', (session.get('order_owner',''),)).fetchall()
        return render_template('my_orders.html', orders=rows)

    @app.post('/orders/forget')
    def forget_orders():
        session.pop('order_owner', None)
        session.pop('checkout_token', None)
        flash('Order history access has been removed from this browser. The shop still keeps its order records. Contact Mahrukh if you need help with an existing order.', 'success')
        return redirect(url_for('my_orders'), code=303)

    @app.get('/order/<reference>')
    def order_detail(reference):
        order = read_order(reference)
        message = ['Assalam-o-alaikum! Please confirm my Mahrukh order ' + reference, '']
        message += [f"{x['name']} | {x['size']} | Qty {x['quantity']} | PKR {x['subtotal']:,}" for x in order['items']]
        message += ['', f"Total including delivery: PKR {order['total']:,}", 'Payment choice: ' + order['payment_method'], 'Name: ' + order['name']]
        link = 'https://wa.me/' + order['merchant']['whatsapp'] + '?text=' + quote('\n'.join(message))
        return render_template('order.html', order=order, order_whatsapp=link)

    @app.get('/admin/orders')
    @admin_required
    def admin_orders():
        status = request.args.get('status','')
        rows = db().execute('SELECT * FROM orders ' + ('WHERE status=? ' if status in STATUSES else '') + 'ORDER BY id DESC LIMIT 200', (status,) if status in STATUSES else ()).fetchall()
        return render_template('orders.html', orders=rows, statuses=STATUSES, selected_status=status)

    @app.route('/admin/order/<reference>', methods=['GET','POST'])
    @admin_required
    def admin_order(reference):
        if request.method == 'POST':
            connection = db()
            try:
                connection.execute('BEGIN IMMEDIATE')
                order = read_order(reference)
                if request.form.get('version') != str(order['version']): abort(409, 'This order was changed in another tab. Reload it before saving.')
                status = request.form.get('status','')
                payment = request.form.get('payment_status','')
                reference_note = request.form.get('payment_reference','').strip()[:300]
                tracking = request.form.get('tracking','').strip()[:300]
                pay_url = request.form.get('payment_url','').strip()
                invoice_currency, invoice_amount = order['invoice_currency'], order['invoice_amount']
                if status not in STATUSES or payment not in PAYMENT_STATUSES: raise ValueError('Choose valid order and payment statuses.')
                allowed = {'pending':('pending','confirmed','cancelled'), 'confirmed':('confirmed','dispatched','cancelled'), 'dispatched':('dispatched','completed'), 'completed':('completed',), 'cancelled':('cancelled',)}
                if status not in allowed[order['status']]: raise ValueError('That order status transition is not available. Contact the customer for a return after dispatch.')
                if payment != 'unpaid' and not reference_note: raise ValueError('Record the verified transaction or refund reference first.')
                if order['payment_status'] in ('paid','refunded') and payment == 'unpaid': raise ValueError('Record a refund instead of resetting a received payment.')
                if order['payment_status'] == 'refunded' and payment != 'refunded': raise ValueError('A refunded payment cannot be reopened.')
                if payment == 'refunded' and order['payment_status'] not in ('paid','refunded'): raise ValueError('Only a received payment can be refunded.')
                if status == 'dispatched' and order['status'] != 'dispatched' and order['payment_method'] != 'cod' and payment != 'paid': raise ValueError('Verify payment before dispatch.')
                if status == 'completed' and order['status'] != 'completed' and payment != 'paid': raise ValueError('Verify the payment or courier settlement before completing this order.')
                if pay_url:
                    if order['payment_method'] != 'hosted' or not safe_url(pay_url, PROVIDERS[order['provider']][1]): raise ValueError('Use an HTTPS payment link from this order’s selected provider.')
                    if request.form.get('link_verified') != 'yes': raise ValueError('Confirm that the hosted invoice matches this order, merchant, currency and total.')
                    if status not in ('confirmed','dispatched','completed'): raise ValueError('Confirm availability before attaching a payment link.')
                    invoice_currency, invoice_amount = 'PKR', str(order['total'])
                    if order['provider'] == 'paypal':
                        invoice_currency = request.form.get('invoice_currency','')
                        raw = request.form.get('invoice_amount','')
                        if invoice_currency not in ('USD','GBP','EUR') or not re.fullmatch(r'\d{1,8}(\.\d{1,2})?',raw):
                            raise ValueError('For PayPal, enter an agreed USD, GBP or EUR invoice amount with at most two decimals.')
                        amount = Decimal(raw)
                        if amount <= 0 or request.form.get('quote_agreed') != 'yes':
                            raise ValueError('Agree the foreign-currency quote with the customer before publishing a PayPal invoice.')
                        invoice_amount = format(amount,'.2f')
                if status == 'cancelled' and order['status'] != 'cancelled':
                    for x in order['items']:
                        connection.execute('UPDATE inventory SET quantity=quantity+? WHERE product_id=? AND size=?', (x['quantity'],x['id'],x['size']))
                    pay_url = ''
                connection.execute('UPDATE orders SET status=?,payment_status=?,payment_reference=?,tracking=?,payment_url=?,invoice_currency=?,invoice_amount=?,updated_at=?,version=version+1 WHERE reference=?', (status,payment,reference_note,tracking,pay_url,invoice_currency,invoice_amount,now(),reference))
                connection.execute('INSERT INTO order_events(reference,created_at,note) VALUES(?,?,?)', (reference,now(),f"{order['status']} → {status}; payment {order['payment_status']} → {payment}; seller update"))
                connection.commit()
                flash('Order updated. Payment status is based on your manual verification.', 'success')
                return redirect(url_for('admin_order', reference=reference), code=303)
            except ValueError as exc:
                connection.rollback()
                flash(str(exc), 'error')
            except Exception:
                connection.rollback()
                raise
        return render_template('admin_order.html', order=read_order(reference), statuses=STATUSES, payment_statuses=PAYMENT_STATUSES,
            events=db().execute('SELECT * FROM order_events WHERE reference=? ORDER BY id DESC', (reference,)).fetchall())

    return settings, checkout_context
