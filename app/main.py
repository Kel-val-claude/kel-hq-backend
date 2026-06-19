# ============================================
#   KEL HQ — MAIN APP (Production)
# ============================================

import os
from flask import Flask
from flask_cors import CORS
from app.core.database import init_db, upgrade_db
from app.routes.public  import public_bp
from app.routes.auth    import auth_bp
from app.routes.command import command_bp
from app.routes.api     import api_bp

def create_app():
    app = Flask(__name__, template_folder='../templates')

    # SECRET_KEY from environment in production, fallback for local dev
    app.secret_key = os.environ.get('SECRET_KEY', 'KEL-HQ-DEV-SECRET-CHANGE-ME')

    # Session config — works for both local http and Render's https
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE']   = os.environ.get('RENDER', '') != ''  # True on Render (HTTPS)
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_NAME']     = 'kel_hq_session'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

    CORS(app, supports_credentials=True)

    init_db()
    upgrade_db()

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(command_bp)
    app.register_blueprint(api_bp)

    return app


# Module-level app object — required for gunicorn to find it
# (gunicorn command: gunicorn app.main:app)
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_DEBUG', '') == '1')
