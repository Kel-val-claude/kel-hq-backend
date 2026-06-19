# ============================================
#   KEL HQ — PUBLIC ROUTES
#   app/routes/public.py
# ============================================

from flask import Blueprint, send_from_directory, redirect
import os

public_bp = Blueprint('public', __name__)

# Serve the frontend index.html at root
FRONTEND_PATH = os.path.join(os.path.dirname(__file__), '../../../kel-hq')

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
