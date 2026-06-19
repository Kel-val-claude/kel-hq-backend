# ============================================
#   KEL HQ — DATABASE (Production-ready)
#   app/core/database.py
#
#   Uses SQLAlchemy Core so the SAME code works with:
#   - SQLite locally (DATABASE_URL not set)
#   - Postgres on Render (DATABASE_URL set automatically)
# ============================================

import os
from sqlalchemy import create_engine, text

# ---- DATABASE URL ----
# Render sets DATABASE_URL automatically when you attach a Postgres DB.
# Locally, this falls back to a SQLite file.
DATABASE_URL = os.environ.get('DATABASE_URL', '')

if DATABASE_URL:
    # Render's Postgres URLs start with postgres:// but SQLAlchemy needs postgresql://
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    IS_POSTGRES = True
else:
    # Local fallback — SQLite file
    db_path = os.path.join(os.path.dirname(__file__), '../../database/kel_hq.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    DATABASE_URL = f'sqlite:///{db_path}'
    IS_POSTGRES = False

engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class RowWrapper:
    """Makes SQLAlchemy Row support dict(row) and row['key'] like sqlite3.Row did."""
    def __init__(self, row):
        self._row = row
        self._mapping = row._mapping

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._row[key]
        return self._mapping[key]

    def keys(self):
        return self._mapping.keys()

    def __iter__(self):
        return iter(self._mapping.keys())

    def items(self):
        return self._mapping.items()


class ResultWrapper:
    """Wraps SQLAlchemy CursorResult so .fetchall()/.fetchone() return dict-friendly rows."""
    def __init__(self, result):
        self._result = result

    def fetchall(self):
        return [RowWrapper(r) for r in self._result.fetchall()]

    def fetchone(self):
        r = self._result.fetchone()
        return RowWrapper(r) if r is not None else None


class DBConnection:
    """
    Thin wrapper so the rest of the app can keep using
    db.execute(...).fetchall() / .fetchone() like before,
    instead of rewriting every route to raw SQLAlchemy syntax.
    """
    def __init__(self, conn):
        self._conn = conn

    def execute(self, query, params=None):
        # Convert sqlite-style "?" placeholders to SQLAlchemy ":paramN" style
        if params is not None and '?' in query:
            if isinstance(params, (list, tuple)):
                parts = query.split('?')
                new_query = ''
                bind = {}
                for i, part in enumerate(parts[:-1]):
                    key = f'p{i}'
                    new_query += part + f':{key}'
                    bind[key] = params[i]
                new_query += parts[-1]
                query = new_query
                params = bind
        result = self._conn.execute(text(query), params or {})
        return ResultWrapper(result)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def executemany(self, query, seq_of_params):
        for params in seq_of_params:
            self.execute(query, params)


def get_db():
    """Get a database connection. Drop-in replacement for the old sqlite3 version."""
    conn = engine.connect()
    return DBConnection(conn)


def _pk():
    """Returns the correct PK syntax for the active database."""
    if IS_POSTGRES:
        return 'SERIAL PRIMARY KEY'
    return 'INTEGER PRIMARY KEY AUTOINCREMENT'


def init_db():
    """Create all tables if they don't exist."""
    db = get_db()
    pk = _pk()

    # ---- OWNER ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS owner (
            id       {pk},
            username TEXT NOT NULL DEFAULT 'kel',
            password TEXT NOT NULL DEFAULT 'KEL-HQ-2026',
            name     TEXT NOT NULL DEFAULT 'Kel Val Claude'
        )
    ''')
    count = db.execute('SELECT COUNT(*) as c FROM owner').fetchone()
    if count[0] == 0:
        db.execute(
            'INSERT INTO owner (username, password, name) VALUES (?, ?, ?)',
            ('kel', 'KEL-HQ-2026', 'Kel Val Claude')
        )

    # ---- PROFILE ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS profile (
            id               {pk},
            projects_built   INTEGER DEFAULT 12,
            partnerships     INTEGER DEFAULT 2,
            deals_closed     INTEGER DEFAULT 20,
            hours_saved      INTEGER DEFAULT 400,
            systems_built    INTEGER DEFAULT 8,
            bots_created     INTEGER DEFAULT 6,
            tasks_automated  INTEGER DEFAULT 1000,
            current_focus    TEXT DEFAULT 'TIMELY AI, SILENCE API, HQ System'
        )
    ''')
    count = db.execute('SELECT COUNT(*) as c FROM profile').fetchone()
    if count[0] == 0:
        if IS_POSTGRES:
            db.execute('INSERT INTO profile (id) VALUES (1)')
        else:
            db.execute('INSERT INTO profile (id) VALUES (1)')

    # ---- AVAILABILITY ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS availability (
            id           {pk},
            status       TEXT DEFAULT 'available',
            next_opening TEXT DEFAULT '',
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    count = db.execute('SELECT COUNT(*) as c FROM availability').fetchone()
    if count[0] == 0:
        db.execute('INSERT INTO availability (id) VALUES (1)')

    # ---- PROJECTS ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS projects (
            id          {pk},
            title       TEXT NOT NULL,
            description TEXT,
            category    TEXT,
            tags        TEXT,
            link        TEXT,
            complexity  TEXT DEFAULT 'Medium',
            duration    TEXT,
            status      TEXT DEFAULT 'live',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    count = db.execute('SELECT COUNT(*) as c FROM projects').fetchone()
    if count[0] == 0:
        defaults = [
            ('Crust Bakery',     'Modern bakery showcase with menu and order system.',  'Website',    'HTML,CSS,JS',        '#',                          'Medium', '1 Day',  'live'),
            ('Volt Electronics', 'Full electronics marketplace with AI recommender.',   'E-Commerce', 'HTML,CSS,JS,AI',     '#',                          'High',   '2 Days', 'live'),
            ('TIMELY AI',        'AI productivity SaaS with working chat assistant.',   'SaaS',       'HTML,CSS,JS,SaaS',   '/portfolio/timely-ai/',     'High',   '1 Day',  'live'),
        ]
        db.executemany(
            'INSERT INTO projects (title,description,category,tags,link,complexity,duration,status) VALUES (?,?,?,?,?,?,?,?)',
            defaults
        )

    # ---- APPOINTMENTS ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS appointments (
            id         {pk},
            name       TEXT NOT NULL,
            contact    TEXT NOT NULL,
            service    TEXT,
            message    TEXT,
            status     TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- REVIEWS ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS reviews (
            id         {pk},
            name       TEXT NOT NULL,
            role       TEXT,
            content    TEXT NOT NULL,
            rating     INTEGER DEFAULT 5,
            featured   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    count = db.execute('SELECT COUNT(*) as c FROM reviews').fetchone()
    if count[0] == 0:
        defaults = [
            ('Amara O.', 'Business Owner',  'Professional work from start to finish. Kel understood exactly what I needed.', 5, 1),
            ('Taiwo A.', 'Startup Founder', 'Fast delivery and clean architecture. My Telegram bot was done in 2 days.',     5, 0),
            ('David K.', 'Operations Lead', 'The automation system saves my team hours every week. Excellent communication.',5, 0),
            ('Chidi E.', 'Agency Director', 'Clean code, fast turnaround, and a developer who thinks about your goals.',     5, 0),
        ]
        db.executemany(
            'INSERT INTO reviews (name,role,content,rating,featured) VALUES (?,?,?,?,?)',
            defaults
        )

    # ---- PARTNERS ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS partners (
            id          {pk},
            name        TEXT NOT NULL,
            type        TEXT DEFAULT 'Partner',
            description TEXT,
            url         TEXT,
            active      INTEGER DEFAULT 1
        )
    ''')
    count = db.execute('SELECT COUNT(*) as c FROM partners').fetchone()
    if count[0] == 0:
        defaults = [
            ('SILENCE </> SYS', 'Ecosystem Partner', 'Core technology ecosystem powering digital systems and automation infrastructure.', '#', 1),
            ('SILENCE // FED',  'Strategic Partner',  'Strategic federation for collaborative development and ecosystem expansion.',         '#', 1),
        ]
        db.executemany(
            'INSERT INTO partners (name,type,description,url,active) VALUES (?,?,?,?,?)',
            defaults
        )

    # ---- ANALYTICS ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS analytics (
            id         {pk},
            event_type TEXT NOT NULL,
            value      TEXT,
            source     TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- ANNOUNCEMENTS ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS announcements (
            id         {pk},
            message    TEXT NOT NULL,
            type       TEXT DEFAULT 'info',
            active     INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- ACTIVITY LOG ----
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS activity_log (
            id         {pk},
            action     TEXT NOT NULL,
            detail     TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    db.commit()
    db.close()
    print('[KEL HQ] Database initialised ✓', '(Postgres)' if IS_POSTGRES else '(SQLite)')


def upgrade_db():
    """Add v2 + v7 tables and settings."""
    db = get_db()
    pk = _pk()

    # SETTINGS
    db.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    defaults = [
        ('contact_wa',        'https://wa.me/234XXXXXXXXXX'),
        ('contact_tg',        'https://t.me/kelvalclaude'),
        ('contact_channel',   'https://t.me/kelvalchannel'),
        ('contact_github',    'https://github.com/kelvalclaude'),
        ('contact_facebook',  'https://facebook.com/kelvalclaude'),
        ('contact_email',     'mailto:kelvalclaude@gmail.com'),
        ('contact_discord',   ''),
        ('contact_x',         ''),
        ('hero_desc',         'Building Websites, Automation Systems, Platforms, and Digital Experiences.'),
        ('about_location',    'Nigeria'),
        ('about_experience',  '2+ Years'),
        ('about_languages',   'English'),
        ('about_focus',       'Digital Ecosystems'),
        ('resume_url',        'assets/resume.pdf'),
        ('profile_name',      'Kel Val Claude'),
        ('profile_handle',    '@kel_val_claude'),
        ('profile_title1',    'Developer'),
        ('profile_title2',    'System Architect'),
        ('profile_title3',    'Digital Builder'),
        ('profile_photo_url', 'assets/logo.png'),
    ]
    for key, val in defaults:
        existing = db.execute('SELECT value FROM settings WHERE key=?', (key,)).fetchone()
        if not existing:
            db.execute('INSERT INTO settings (key,value) VALUES (?,?)', (key, val))

    # DEALS
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS deals (
            id         {pk},
            title      TEXT NOT NULL,
            client     TEXT,
            value      TEXT,
            status     TEXT DEFAULT 'active',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # VISITORS
    if IS_POSTGRES:
        db.execute(f'''
            CREATE TABLE IF NOT EXISTS visitors (
                id    {pk},
                date  TEXT DEFAULT CURRENT_DATE,
                count INTEGER DEFAULT 1
            )
        ''')
    else:
        db.execute(f'''
            CREATE TABLE IF NOT EXISTS visitors (
                id    {pk},
                date  TEXT DEFAULT (date('now')),
                count INTEGER DEFAULT 1
            )
        ''')

    # VISITOR RATINGS
    db.execute(f'''
        CREATE TABLE IF NOT EXISTS visitor_ratings (
            id         {pk},
            name       TEXT NOT NULL,
            rating     INTEGER NOT NULL DEFAULT 5,
            comment    TEXT,
            approved   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    db.commit()
    db.close()
    print('[KEL HQ] Database upgraded ✓')
