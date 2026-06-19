# ============================================
#   KEL HQ — LOCAL DEV ENTRY POINT
#   Usage: python run.py
#   (Production uses gunicorn app.main:app instead)
# ============================================

import os
from app.main import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"""
╔══════════════════════════════════════╗
║   KEL VAL CLAUDE — DIGITAL HQ        ║
║   Backend Server Starting...         ║
╠══════════════════════════════════════╣
║   Frontend  →  http://localhost:{port} ║
║   Command   →  http://localhost:{port}/command-center
║   Login     →  http://localhost:{port}/login
╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=port, debug=True)
