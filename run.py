# ============================================
#   KEL HQ — RUN SERVER
#   Usage: python run.py
# ============================================

from app.main import create_app

app = create_app()

if __name__ == '__main__':
    print("""
╔══════════════════════════════════════╗
║   KEL VAL CLAUDE — DIGITAL HQ       ║
║   Backend Server Starting...        ║
╠══════════════════════════════════════╣
║   Frontend  →  http://localhost:5000 ║
║   Command   →  http://localhost:5000/command-center
║   Login     →  http://localhost:5000/login
╚══════════════════════════════════════╝
    """)
    app.run(debug=True, port=5000)
