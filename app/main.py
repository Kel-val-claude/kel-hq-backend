# ============================================
#   KEL HQ — MAIN APP (v2)
# ============================================

from flask import Flask
from flask_cors import CORS
from app.core.database import init_db, upgrade_db
from app.routes.public  import public_bp
from app.routes.auth    import auth_bp
from app.routes.command import command_bp
from app.routes.api     import api_bp

def create_app():
    app = Flask(__name__, template_folder='../templates')
    import os
    app.secret_key = os.environ.get('SECRET_KEY', 'KEL-HQ-SECRET-CHANGE-THIS-IN-PRODUCTION')

    # Session config — critical for mobile browsers to keep login
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE']   = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_NAME']     = 'kel_hq_session'
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 days

    CORS(app, supports_credentials=True, origins=[
        'http://localhost:5000',
        'http://127.0.0.1:5000',
        'https://fancy-dolphin-0b2a62.netlify.app',
        os.environ.get('FRONTEND_URL', '')
    ])

    init_db()
    upgrade_db()  # v2 tables

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(command_bp)
    app.register_blueprint(api_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
