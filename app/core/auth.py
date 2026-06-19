# ============================================
#   KEL HQ — AUTH GUARD (fixed)
#   app/core/auth.py
# ============================================

from functools import wraps
from flask import session, jsonify, redirect, url_for, request


def owner_required(f):
    """
    Protects Command Center routes.
    - If not logged in + JSON request → 401
    - If not logged in + page request → redirect to /login
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('is_owner'):
            # Detect if it's an API/fetch call vs a normal page load
            is_api = (
                request.path.startswith('/api/') or
                request.headers.get('Content-Type') == 'application/json' or
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '')
            )
            if is_api:
                return jsonify({'error': 'Unauthorised. Owner login required.'}), 401
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated


def log_activity(conn, action, detail=''):
    """Log owner actions to activity feed."""
    conn.execute(
        'INSERT INTO activity_log (action, detail) VALUES (?, ?)',
        (action, detail)
    )
