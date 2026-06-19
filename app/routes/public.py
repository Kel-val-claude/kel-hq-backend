# ============================================
#   KEL HQ — PUBLIC ROUTES
#   app/routes/public.py
#   Serves the frontend (now bundled inside the
#   backend's deploy root so Render picks it up)
# ============================================

from flask import Blueprint, send_from_directory
import os

public_bp = Blueprint('public', __name__)

# frontend/ now lives directly inside kel-hq-backend-v2/
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), '../../frontend')

@public_bp.route('/')
def index():
    return send_from_directory(FRONTEND_PATH, 'index.html')

@public_bp.route('/css/<path:filename>')
def css(filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'css'), filename)

@public_bp.route('/js/<path:filename>')
def js(filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'js'), filename)

@public_bp.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'assets'), filename)

@public_bp.route('/portfolio/<project>/<path:filename>')
def portfolio_assets(project, filename):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'portfolio', project), filename)

@public_bp.route('/portfolio/<project>/')
def portfolio_index(project):
    return send_from_directory(os.path.join(FRONTEND_PATH, 'portfolio', project), 'index.html')
