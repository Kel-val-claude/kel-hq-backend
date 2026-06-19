# ============================================
#   KEL HQ — AUTH ROUTES
#   app/routes/auth.py
#
#   /login  → owner login page + handler
#   /logout → clears session
# ============================================

from flask import Blueprint, request, session, jsonify, redirect, url_for, render_template_string
from app.core.database import get_db

auth_bp = Blueprint('auth', __name__)

# Simple inline login page (no extra template file needed)
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
  <title>KEL HQ — Command Center Access</title>
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <style>
    * { margin:0; padding:0; box-sizing:border-box; }
    body {
      background:#0A0A0A; color:#F0F0F0;
      font-family:'Inter',sans-serif;
      display:flex; align-items:center; justify-content:center;
      min-height:100vh;
    }
    .box {
      background:#111; border:1px solid rgba(212,175,55,0.2);
      border-radius:16px; padding:2.5rem; width:100%; max-width:360px;
      box-shadow:0 0 60px rgba(212,175,55,0.08);
    }
    .logo { font-size:1.4rem; font-weight:700; color:#D4AF37; margin-bottom:0.3rem; }
    .sub  { font-size:0.72rem; color:#555; margin-bottom:2rem; text-transform:uppercase; letter-spacing:0.1em; }
    label { font-size:0.75rem; color:#666; display:block; margin-bottom:0.35rem; }
    input {
      width:100%; background:#0A0A0A; border:1px solid rgba(255,255,255,0.08);
      border-radius:8px; padding:0.75rem 1rem; color:#F0F0F0;
      font-family:'Inter',sans-serif; font-size:0.88rem; outline:none;
      margin-bottom:1rem; transition:border-color 0.2s;
    }
    input:focus { border-color:rgba(212,175,55,0.4); }
    button {
      width:100%; background:#D4AF37; color:#0A0A0A; border:none;
      border-radius:8px; padding:0.85rem; font-weight:700; font-size:0.9rem;
      cursor:pointer; transition:background 0.2s;
    }
    button:hover { background:#c9a227; }
    .error { color:#E74C3C; font-size:0.78rem; margin-bottom:1rem; padding:0.5rem; background:rgba(231,76,60,0.08); border-radius:6px; border:1px solid rgba(231,76,60,0.2); }
    .back { display:block; text-align:center; margin-top:1.25rem; font-size:0.75rem; color:#444; text-decoration:none; }
    .back:hover { color:#D4AF37; }
  </style>
</head>
<body>
  <div class="box">
    <div class="logo">K.</div>
    <div class="sub">Command Center · Owner Access Only</div>
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    <form method="POST" action="/login">
      <label>Username</label>
      <input type="text" name="username" placeholder="Enter username" required autofocus />
      <label>Password</label>
      <input type="password" name="password" placeholder="Enter password" required />
      <button type="submit">Access Command Center →</button>
    </form>
    <a class="back" href="/">← Back to HQ</a>
  </div>
</body>
</html>
'''


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in? Go straight to Command Center
    if session.get('is_owner'):
        return redirect('/command-center')

    error = None

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        db    = get_db()
        owner = db.execute(
            'SELECT * FROM owner WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        db.close()

        if owner:
            # ✅ Correct credentials — set session
            session.permanent      = True
            session['is_owner']    = True
            session['owner_name']  = owner['name']
            return redirect('/command-center')
        else:
            # ❌ Wrong — show error, no hint about what's wrong
            error = 'Invalid credentials.'

    return render_template_string(LOGIN_PAGE, error=error)


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ---- API login (for fetch-based login if needed later) ----
@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data     = request.get_json() or {}
    username = data.get('username', '')
    password = data.get('password', '')

    db    = get_db()
    owner = db.execute(
        'SELECT * FROM owner WHERE username = ? AND password = ?',
        (username, password)
    ).fetchone()
    db.close()

    if owner:
        session['is_owner']   = True
        session['owner_name'] = owner['name']
        return jsonify({'success': True, 'name': owner['name']})

    return jsonify({'success': False, 'error': 'Invalid credentials.'}), 401


@auth_bp.route('/api/auth/status')
def auth_status():
    """Let frontend check if owner is logged in."""
    return jsonify({
        'is_owner': bool(session.get('is_owner')),
        'name':     session.get('owner_name', '')
    })
