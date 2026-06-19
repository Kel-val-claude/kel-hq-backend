# KEL VAL CLAUDE — DIGITAL HQ BACKEND
## Setup & Run Guide

---

### FOLDER STRUCTURE

```
kel-hq-backend/          ← Backend (Flask/Python)
│
├── run.py               ← START HERE
├── requirements.txt
│
├── app/
│   ├── main.py          ← Flask app factory
│   ├── core/
│   │   ├── database.py  ← SQLite setup + all tables
│   │   └── auth.py      ← Owner protection decorator
│   └── routes/
│       ├── auth.py      ← /login  /logout
│       ├── api.py       ← /api/*  (public, visitors can read)
│       ├── command.py   ← /command-center/* (OWNER ONLY)
│       └── public.py    ← serves your frontend HTML
│
└── database/
    └── kel_hq.db        ← Created automatically on first run

kel-hq/                  ← Frontend (your HTML/CSS/JS)
├── index.html
├── css/style.css
└── js/script.js
```

---

### SETUP (first time)

```bash
# 1. Go into the backend folder
cd kel-hq-backend

# 2. Install Python packages
pip install -r requirements.txt

# 3. Run the server
python run.py
```

---

### ACCESS

| URL | Who |
|-----|-----|
| `http://localhost:5000/` | Everyone (your HQ homepage) |
| `http://localhost:5000/login` | Owner login page |
| `http://localhost:5000/command-center` | Owner only (redirects to login if not logged in) |
| `http://localhost:5000/api/*` | Public API (read-only data) |

---

### DEFAULT LOGIN

```
Username: kel
Password: KEL-HQ-2026
```

**Change this in:** `app/core/database.py` → `init_db()` function
(Update the INSERT statement with your own password)

---

### HOW OWNER vs VISITOR WORKS

```
VISITOR hits /command-center
        ↓
Flask checks session → is_owner = False
        ↓
Redirected to /login
        ↓
Wrong password → error shown, no access
Correct password → session set → Command Center opens

OWNER logs in
        ↓
session['is_owner'] = True
        ↓
Full access to:
  - View all appointments
  - Approve / cancel appointments
  - Add / delete projects
  - Add / delete reviews
  - Control availability (Available / Booked)
  - Push announcements to homepage
  - Update profile stats
  - View analytics
  - See activity log
```

---

### CONNECTING FRONTEND TO BACKEND

In your `kel-hq/js/script.js`, the API calls are already stubbed.

Change them from:
```js
console.log('[KEL HQ] Contact click:', label)
```

To:
```js
fetch('/api/analytics/click', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ type: label })
})
```

And for dynamic data (availability, profile stats, projects):
```js
// Load availability status
fetch('/api/status')
  .then(r => r.json())
  .then(data => {
    // data.status = 'available' or 'booked'
    // data.next_opening = 'July 3rd, 2026'
    setAvailability(data.status, data.next_opening)
  })
```

---

### CHANGE YOUR PASSWORD

Open `app/core/database.py` and find this line:

```python
('kel', 'KEL-HQ-2026', 'Kel Val Claude')
```

Change `KEL-HQ-2026` to your own password.

Then delete `database/kel_hq.db` and run `python run.py` again.
The database will recreate with your new password.

---

### PHASE 2 UPGRADES (coming next)

- [ ] Wire frontend to pull live data from `/api/*`
- [ ] Availability section reads from backend automatically
- [ ] Profile stats update live from Command Center
- [ ] Portfolio cards loaded dynamically from database
- [ ] WebSocket live activity feed

---

**Built by Kel Val Claude · Powered by SILENCE//SYS**
