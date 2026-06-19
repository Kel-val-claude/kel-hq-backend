# ============================================
#   KEL HQ — PUBLIC API ROUTES
#   app/routes/api.py
#
#   These are READ-ONLY endpoints.
#   Anyone (visitor OR owner) can call these.
#   Your frontend JS fetches from these.
# ============================================

from flask import Blueprint, jsonify, request, session
from app.core.database import get_db

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ---- PROFILE ----
@api_bp.route('/profile')
def get_profile():
    db   = get_db()
    row  = db.execute('SELECT * FROM profile WHERE id=1').fetchone()
    db.close()
    return jsonify({
        'projects_built':  row['projects_built'],
        'partnerships':    row['partnerships'],
        'deals_closed':    row['deals_closed'],
        'hours_saved':     row['hours_saved'],
        'systems_built':   row['systems_built'],
        'bots_created':    row['bots_created'],
        'tasks_automated': row['tasks_automated'],
        'current_focus':   row['current_focus'],
    })


# ---- AVAILABILITY ----
@api_bp.route('/status')
def get_status():
    db  = get_db()
    row = db.execute('SELECT * FROM availability WHERE id=1').fetchone()
    db.close()
    return jsonify({
        'status':       row['status'],
        'next_opening': row['next_opening'],
        'last_updated': row['last_updated'],
    })


# ---- PROJECTS ----
@api_bp.route('/projects')
def get_projects():
    db   = get_db()
    rows = db.execute(
        "SELECT * FROM projects WHERE status='live' ORDER BY id"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ---- REVIEWS ----
@api_bp.route('/reviews')
def get_reviews():
    db   = get_db()
    rows = db.execute(
        'SELECT * FROM reviews ORDER BY featured DESC, id'
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ---- PARTNERS ----
@api_bp.route('/partners')
def get_partners():
    db   = get_db()
    rows = db.execute(
        "SELECT * FROM partners WHERE active=1 ORDER BY id"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ---- ANNOUNCEMENTS (active banners) ----
@api_bp.route('/announcements')
def get_announcements():
    db   = get_db()
    rows = db.execute(
        "SELECT * FROM announcements WHERE active=1 ORDER BY id DESC LIMIT 3"
    ).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])


# ---- ANALYTICS (visitor sends clicks here) ----
@api_bp.route('/analytics/click', methods=['POST'])
def log_click():
    data = request.get_json() or {}
    evt  = data.get('type', 'unknown')
    src  = data.get('source', 'frontend')

    db = get_db()
    db.execute(
        'INSERT INTO analytics (event_type, value, source) VALUES (?, ?, ?)',
        ('click', evt, src)
    )
    db.commit()
    db.close()
    return jsonify({'ok': True})


@api_bp.route('/analytics/view', methods=['POST'])
def log_view():
    data    = request.get_json() or {}
    project = data.get('project', 'unknown')

    db = get_db()
    db.execute(
        'INSERT INTO analytics (event_type, value, source) VALUES (?, ?, ?)',
        ('view', project, 'portfolio')
    )
    db.commit()
    db.close()
    return jsonify({'ok': True})


# ---- SUBMIT APPOINTMENT (visitors book here) ----
@api_bp.route('/appointments/book', methods=['POST'])
def book_appointment():
    data = request.get_json() or {}

    name    = data.get('name', '').strip()
    contact = data.get('contact', '').strip()
    service = data.get('service', '').strip()
    message = data.get('message', '').strip()

    if not name or not contact:
        return jsonify({'error': 'Name and contact are required.'}), 400

    db = get_db()
    db.execute(
        'INSERT INTO appointments (name,contact,service,message) VALUES (?,?,?,?)',
        (name, contact, service, message)
    )
    db.execute(
        'INSERT INTO activity_log (action, detail) VALUES (?, ?)',
        ('New Appointment', f'From: {name} — {service}')
    )
    db.commit()
    db.close()

    return jsonify({'ok': True, 'message': 'Appointment request received!'})


# ---- SETTINGS (contact links etc) ----
@api_bp.route('/settings')
def get_settings():
    db   = get_db()
    rows = db.execute('SELECT key, value FROM settings').fetchall()
    db.close()
    return jsonify({r['key']: r['value'] for r in rows})


# ---- VISITOR TRACKING ----
@api_bp.route('/analytics/visit', methods=['POST'])
def log_visit():
    db = get_db()
    # Upsert today's visitor count
    today = db.execute("SELECT id, count FROM visitors WHERE date = date('now')").fetchone()
    if today:
        db.execute('UPDATE visitors SET count = count + 1 WHERE id = ?', (today['id'],))
    else:
        db.execute('INSERT INTO visitors (count) VALUES (1)')
    db.commit()
    db.close()
    return jsonify({'ok': True})


# ---- VISITOR STATS (public summary) ----
@api_bp.route('/analytics/summary')
def analytics_summary():
    db = get_db()
    total_visits = db.execute('SELECT SUM(count) as total FROM visitors').fetchone()['total'] or 0
    today_visits = db.execute("SELECT count FROM visitors WHERE date = date('now')").fetchone()
    total_clicks = db.execute("SELECT COUNT(*) as c FROM analytics WHERE event_type='click'").fetchone()['c']
    db.close()
    return jsonify({
        'total_visits': total_visits,
        'today_visits': today_visits['count'] if today_visits else 0,
        'total_clicks': total_clicks,
    })


# ---- VISITOR RATING SUBMISSION ----
@api_bp.route('/ratings/submit', methods=['POST'])
def submit_rating():
    data    = request.get_json() or {}
    name    = data.get('name', '').strip()
    rating  = int(data.get('rating', 0))
    comment = data.get('comment', '').strip()

    if not name:
        return jsonify({'error': 'Name required'}), 400
    if not 1 <= rating <= 5:
        return jsonify({'error': 'Rating must be 1-5'}), 400

    db = get_db()
    try:
        db.execute(
            'INSERT INTO visitor_ratings (name, rating, comment) VALUES (?,?,?)',
            (name, rating, comment)
        )
        db.execute(
            'INSERT INTO activity_log (action, detail) VALUES (?,?)',
            ('Rating Received', f'{name} gave {rating}★')
        )
        db.commit()
    except Exception as e:
        db.close()
        return jsonify({'error': str(e)}), 500
    db.close()
    return jsonify({'ok': True})
