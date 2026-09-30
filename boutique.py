"""Small boutique conveniences without customer accounts or additional services."""
import re
from urllib.parse import quote, urlsplit
from flask import abort, flash, jsonify, redirect, render_template, request, session, url_for

from catalog import QUESTIONS


def install_boutique(app, db, product, settings):
    def saved_ids():
        if not hasattr(request, '_saved_ids'):
            raw = session.get('saved', [])
            valid = []
            for pid in raw[:24] if isinstance(raw, list) else []:
                if type(pid) is int and pid not in valid and db().execute('SELECT 1 FROM products WHERE id=? AND active=1', (pid,)).fetchone():
                    valid.append(pid)
            if valid != raw: session['saved'] = valid
            request._saved_ids = valid
        return request._saved_ids

    def card(pid):
        p = product(pid)
        p['stock_total'] = sum(p['stock'].get(size, 0) for size in p['sizes'])
        return p

    def related(item):
        rows = db().execute('SELECT id FROM products WHERE active=1 AND id<>? ORDER BY (category=?) DESC, id DESC LIMIT 3', (item['id'], item['category'])).fetchall()
        return [card(row['id']) for row in rows]

    @app.context_processor
    def boutique_context():
        return dict(saved_ids=saved_ids(), enquiry_topics=QUESTIONS)

    @app.get('/saved')
    def saved():
        return render_template('saved.html', products=[card(pid) for pid in saved_ids()])

    @app.post('/saved/<int:pid>')
    def save_piece(pid):
        p = product(pid)
        if not p['active']: abort(404)
        ids = saved_ids().copy()
        action = request.form.get('action')
        if action not in ('save', 'remove'): abort(400, 'Choose save or remove.')
        if action == 'save' and pid not in ids:
            if len(ids) >= 24: abort(409, 'Your saved collection has 24 pieces. Remove one to make room.')
            ids.append(pid)
        elif action == 'remove' and pid in ids:
            ids.remove(pid)
        session['saved'] = ids
        request._saved_ids = ids
        if request.headers.get('X-Mahrukh-Saved') == '1':
            return jsonify(saved=pid in ids, count=len(ids))
        flash('Saved for another look.' if pid in ids else 'Removed from your saved pieces.', 'success')
        target = request.form.get('return_to', '')
        try:
            parsed = urlsplit(target)
        except ValueError:
            target = url_for('saved')
            parsed = urlsplit(target)
        # Only same-store catalog, saved and product locations; never an open redirect.
        if parsed.scheme or parsed.netloc or not re.fullmatch(r'/(?:saved|product/\d+)?', parsed.path) or any(ord(c)<32 or c=='\\' for c in target):
            target = url_for('saved')
        return redirect(target, code=303)

    @app.post('/saved/clear')
    def clear_saved():
        session.pop('saved', None)
        flash('Your saved collection has been cleared from this browser.', 'success')
        return redirect(url_for('saved'), code=303)

    @app.get('/product/<int:pid>/ask')
    def enquire(pid):
        p = product(pid)
        if not p['active']: abort(404)
        topic = request.args.get('topic', 'fit')
        size = request.args.get('size', '')
        if topic not in QUESTIONS or (size and size not in p['sizes']): abort(400, 'Choose a listed question and size.')
        phone = settings()['whatsapp']
        if not phone: return redirect(url_for('contact'))
        # The visitor still reviews and sends the draft in WhatsApp.
        message = f"Assalam-o-alaikum! I would like some help with {p['name']} (Mahrukh product {pid}).\n{QUESTIONS[topic][1]}"
        if size: message += '\nSize I am considering: ' + size
        return redirect('https://wa.me/' + phone + '?text=' + quote(message))

    return related
