import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "Data")
DB_PATH = os.path.abspath(os.path.join(DATA_DIR, "applications.db"))

def create_database():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        company TEXT,
        position TEXT,
        status TEXT,
        basis TEXT,
        date_added TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Subscriptions table for job-alert emails
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subscriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        query TEXT NOT NULL,
        location TEXT,
        paused INTEGER DEFAULT 0,
        last_notified TEXT,
        last_seen_job_url TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(subscriptions)")
    subscription_columns = [row[1] for row in cursor.fetchall()]
    if "location" not in subscription_columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN location TEXT")
    if "paused" not in subscription_columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN paused INTEGER DEFAULT 0")
    if "last_seen_job_url" not in subscription_columns:
        cursor.execute("ALTER TABLE subscriptions ADD COLUMN last_seen_job_url TEXT")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS emailed_urls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subscription_id INTEGER NOT NULL,
        url TEXT NOT NULL,
        UNIQUE(subscription_id, url)
    )
    """)
    
    # SMTP settings table (single-row configuration)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS smtp_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server TEXT,
        port INTEGER,
        username TEXT,
        password TEXT,
        use_tls INTEGER DEFAULT 1,
        from_email TEXT
    )
    """)

    cursor.execute("PRAGMA table_info(applications)")
    columns = [row[1] for row in cursor.fetchall()]
    if "basis" not in columns and "notes" in columns:
        cursor.execute("ALTER TABLE applications RENAME COLUMN notes TO basis")
    if "date_added" not in columns:
        cursor.execute("ALTER TABLE applications ADD COLUMN date_added TEXT")

    conn.commit()
    conn.close()


# ✅ CALL IT HERE (outside the function
create_database()

def add_to_database(company, position, status, basis):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO applications
    (company, position, status, basis, date_added)
    VALUES (?, ?, ?, ?, ?)
    """,
    (company, position, status, basis, date_time))

    conn.commit()
    conn.close()

def view_all():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    conn.close()


def get_all_applications():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM applications")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_application_summary():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM applications")
    total = cursor.fetchone()[0]

    cursor.execute(
        "SELECT status, COUNT(*) FROM applications GROUP BY status"
    )
    status_counts = dict(cursor.fetchall())

    conn.close()

    return {
        "total": total,
        "Applied": status_counts.get("Applied", 0),
        "Interview": status_counts.get("Interview", 0),
        "Offer": status_counts.get("Offer", 0),
        "Rejected": status_counts.get("Rejected", 0),
        "Active": status_counts.get("Active", 0)
    }


def add_subscription(email, query, location=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    normalized_location = (location or "").strip() or None
    existing = cursor.execute(
        "SELECT id FROM subscriptions WHERE email = ? AND query = ? AND COALESCE(location, '') = COALESCE(?, '') LIMIT 1",
        (email, query, normalized_location)
    ).fetchone()
    if existing:
        conn.close()
        return False

    cursor.execute(
        """
        INSERT INTO subscriptions (email, query, location, last_notified, last_seen_job_url)
        VALUES (?, ?, ?, NULL, NULL)
        """,
        (email, query, normalized_location)
    )
    conn.commit()
    conn.close()
    return True


def get_subscriptions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, query, location, last_notified, last_seen_job_url, COALESCE(paused, 0) FROM subscriptions")
    rows = cursor.fetchall()
    conn.close()
    return rows


def update_subscription(sub_id, email, query, location=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    normalized_location = (location or "").strip() or None
    cursor.execute(
        "UPDATE subscriptions SET email = ?, query = ?, location = ? WHERE id = ?",
        (email, query, normalized_location, sub_id)
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated


def set_subscription_paused(sub_id, paused):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subscriptions SET paused = ? WHERE id = ?",
        (1 if paused else 0, sub_id)
    )
    conn.commit()
    rows_updated = cursor.rowcount
    conn.close()
    return rows_updated


def get_subscription_sent_urls(sub_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT url FROM emailed_urls WHERE subscription_id = ?", (sub_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row[0] for row in rows}


def save_subscription_sent_urls(sub_id, urls):
    if not urls:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO emailed_urls (subscription_id, url) VALUES (?, ?)",
        [(sub_id, url) for url in urls if url]
    )
    conn.commit()
    conn.close()


def update_subscription_last_notified(sub_id, timestamp, last_seen_job_url=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE subscriptions SET last_notified = ?, last_seen_job_url = ? WHERE id = ?",
        (timestamp, last_seen_job_url, sub_id)
    )
    conn.commit()
    conn.close()


def delete_subscription(sub_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE id = ?", (sub_id,))
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_rows


def set_smtp_settings(server, port, username, password, use_tls, from_email):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM smtp_settings")
    cursor.execute(
        "INSERT INTO smtp_settings (server, port, username, password, use_tls, from_email) VALUES (?, ?, ?, ?, ?, ?)",
        (server, port, username, password, 1 if use_tls else 0, from_email)
    )
    conn.commit()
    conn.close()


def get_smtp_settings():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT server, port, username, password, use_tls, from_email FROM smtp_settings LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "server": row[0],
        "port": row[1],
        "username": row[2],
        "password": row[3],
        "use_tls": bool(row[4]),
        "from_email": row[5]
    }


def update_status(company_name, new_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE applications
        SET status = ?
        WHERE company = ?
        """,
        (new_status, company_name)
    )
    conn.commit()
    conn.close()


def update_application(application_id, company, position, status, basis):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE applications
        SET company = ?, position = ?, status = ?, basis = ?
        WHERE id = ?
        """,
        (company, position, status, basis, application_id)
    )
    conn.commit()
    conn.close()


def delete_application(application_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        DELETE FROM applications
        WHERE id = ?
        """,
        (application_id,)
    )
    deleted_rows = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_rows


def search_applications(search_term):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT * FROM applications
        WHERE company LIKE ?
        OR position LIKE ?
        OR status LIKE ?
        """,
        (
            f"%{search_term}%",
            f"%{search_term}%",
            f"%{search_term}%"
        )
    )
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

