# ============================================
#   KEL HQ — DATABASE
#   app/core/database.py
# ============================================

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/kel_hq.db')


def get_db():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Returns dict-like rows
    return conn


def init_db():
    """Create all tables if they don't exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_db()
    c    = conn.cursor()

    # ---- OWNER (you) ----
    # Only ONE owner account. You set your password here.
    c.execute('''
        CREATE TABLE IF NOT EXISTS owner (
            id       INTEGER PRIMARY KEY,
            username TEXT    NOT NULL DEFAULT 'kel',
            password TEXT    NOT NULL DEFAULT 'KEL-HQ-2026',
            name     TEXT    NOT NULL DEFAULT 'Kel Val Claude'
        )
    ''')

    # Insert default owner if table is empty
    c.execute('SELECT COUNT(*) FROM owner')
    if c.fetchone()[0] == 0:
        c.execute(
            'INSERT INTO owner (username, password, name) VALUES (?, ?, ?)',
            ('kel', 'KEL-HQ-2026', 'Kel Val Claude')
        )

    # ---- PROFILE (hero card data) ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id               INTEGER PRIMARY KEY,
            projects_built   INTEGER DEFAULT 12,
            partnerships     INTEGER DEFAULT 2,
            deals_closed     INTEGER DEFAULT 20,
            hours_saved      INTEGER DEFAULT 400,
            systems_built    INTEGER DEFAULT 8,
            bots_created     INTEGER DEFAULT 6,
            tasks_automated  INTEGER DEFAULT 1000,
            current_focus    TEXT    DEFAULT 'TIMELY AI, SILENCE API, HQ System'
        )
    ''')

    c.execute('SELECT COUNT(*) FROM profile')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO profile DEFAULT VALUES')

    # ---- AVAILABILITY ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS availability (
            id            INTEGER PRIMARY KEY,
            status        TEXT    DEFAULT 'available',
            next_opening  TEXT    DEFAULT '',
            last_updated  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('SELECT COUNT(*) FROM availability')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO availability DEFAULT VALUES')

    # ---- PROJECTS ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT    NOT NULL,
            description TEXT,
            category    TEXT,
            tags        TEXT,
            link        TEXT,
            complexity  TEXT    DEFAULT 'Medium',
            duration    TEXT,
            status      TEXT    DEFAULT 'live',
            created_at  TEXT    DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Seed default projects
    c.execute('SELECT COUNT(*) FROM projects')
    if c.fetchone()[0] == 0:
        defaults = [
            ('Crust Bakery',     'Modern bakery showcase with menu and order system.',  'Website',    'HTML,CSS,JS',        '../crust-bakery/index.html',    'Medium', '1 Day',  'live'),
            ('Volt Electronics', 'Full electronics marketplace with AI recommender.',   'E-Commerce', 'HTML,CSS,JS,AI',     '../volt-electronics/index.html','High',   '2 Days', 'live'),
            ('TIMELY AI',        'AI productivity SaaS with working chat assistant.',   'SaaS',       'HTML,CSS,JS,SaaS',   '../timely-ai/index.html',       'High',   '1 Day',  'live'),
        ]
        c.executemany(
            'INSERT INTO projects (title,description,category,tags,link,complexity,duration,status) VALUES (?,?,?,?,?,?,?,?)',
            defaults
        )

    # ---- APPOINTMENTS ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            contact     TEXT NOT NULL,
            service     TEXT,
            message     TEXT,
            status      TEXT DEFAULT 'pending',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- REVIEWS ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            role       TEXT,
            content    TEXT NOT NULL,
            rating     INTEGER DEFAULT 5,
            featured   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('SELECT COUNT(*) FROM reviews')
    if c.fetchone()[0] == 0:
        defaults = [
            ('Amara O.',  'Business Owner',    'Professional work from start to finish. Kel understood exactly what I needed.',          5, 1),
            ('Taiwo A.',  'Startup Founder',   'Fast delivery and clean architecture. My Telegram bot was done in 2 days.',              5, 0),
            ('David K.',  'Operations Lead',   'The automation system saves my team hours every week. Excellent communication.',          5, 0),
            ('Chidi E.',  'Agency Director',   'Clean code, fast turnaround, and a developer who thinks about your business goals.',     5, 0),
        ]
        c.executemany(
            'INSERT INTO reviews (name,role,content,rating,featured) VALUES (?,?,?,?,?)',
            defaults
        )

    # ---- PARTNERS ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS partners (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            type        TEXT DEFAULT 'Partner',
            description TEXT,
            url         TEXT,
            active      INTEGER DEFAULT 1
        )
    ''')

    c.execute('SELECT COUNT(*) FROM partners')
    if c.fetchone()[0] == 0:
        defaults = [
            ('SILENCE </> SYS', 'Ecosystem Partner',  'Core technology ecosystem powering digital systems and automation infrastructure.', '#', 1),
            ('SILENCE // FED',  'Strategic Partner',   'Strategic federation for collaborative development and ecosystem expansion.',         '#', 1),
        ]
        c.executemany(
            'INSERT INTO partners (name,type,description,url,active) VALUES (?,?,?,?,?)',
            defaults
        )

    # ---- ANALYTICS ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS analytics (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            value      TEXT,
            source     TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- ANNOUNCEMENTS ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS announcements (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            message    TEXT NOT NULL,
            type       TEXT DEFAULT 'info',
            active     INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # ---- ACTIVITY LOG ----
    c.execute('''
        CREATE TABLE IF NOT EXISTS activity_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            action     TEXT NOT NULL,
            detail     TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print('[KEL HQ] Database initialised ✓')


def upgrade_db():
    """Add new tables for v2 features."""
    conn = get_db()
    c    = conn.cursor()

    # SETTINGS — contact links, site text, all editable from Command Center
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key   TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Seed default contact links
    defaults = [
        ('contact_wa',       'https://wa.me/234XXXXXXXXXX'),
        ('contact_tg',       'https://t.me/kelvalclaude'),
        ('contact_channel',  'https://t.me/kelvalchannel'),
        ('contact_github',   'https://github.com/kelvalclaude'),
        ('contact_facebook', 'https://facebook.com/kelvalclaude'),
        ('contact_email',    'mailto:kelvalclaude@gmail.com'),
        ('hero_desc',        'Building Websites, Automation Systems, Platforms, and Digital Experiences.'),
        ('about_location',   'Nigeria'),
        ('about_experience', '2+ Years'),
        ('about_languages',  'English'),
        ('about_focus',      'Digital Ecosystems'),
        ('resume_url',       'assets/resume.pdf'),
    ]
    c.executemany(
        'INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)',
        defaults
    )

    # DEALS TABLE — track individual deals
    c.execute('''
        CREATE TABLE IF NOT EXISTS deals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            client      TEXT,
            value       TEXT,
            status      TEXT DEFAULT 'active',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # VISITORS — daily visit counts
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitors (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            date       TEXT DEFAULT (date('now')),
            count      INTEGER DEFAULT 1
        )
    ''')

    # VISITOR RATINGS TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS visitor_ratings (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            rating     INTEGER NOT NULL DEFAULT 5,
            comment    TEXT,
            approved   INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # NEW SETTINGS KEYS for profile editor + discord/x
    new_keys = [
        ('contact_discord',   ''),
        ('contact_x',         ''),
        ('profile_name',      'Kel Val Claude'),
        ('profile_handle',    '@kel_val_claude'),
        ('profile_title1',    'Developer'),
        ('profile_title2',    'System Architect'),
        ('profile_title3',    'Digital Builder'),
        ('profile_photo_url', 'assets/logo.png'),
    ]
    for key, val in new_keys:
        c.execute(
            'INSERT INTO settings (key,value) VALUES (?,?) ON CONFLICT(key) DO NOTHING',
            (key, val)
        )

    conn.commit()
    conn.close()
    print('[KEL HQ] Database upgraded to v2 ✓')
