import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "data" / "corelink.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT NOT NULL,
                client_name TEXT NOT NULL,
                to_address TEXT NOT NULL,
                subject TEXT NOT NULL,
                body TEXT NOT NULL,
                sent_at TEXT NOT NULL,
                replied INTEGER DEFAULT 0,
                replied_at TEXT
            )
        """)
        conn.commit()


def log_email(sender, client_name, to_address, subject, body):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO emails (sender, client_name, to_address, subject, body, sent_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sender, client_name, to_address, subject, body,
              datetime.now().isoformat()))
        conn.commit()


def mark_replied(email_id, replied_at):
    with get_conn() as conn:
        conn.execute("""
            UPDATE emails SET replied = 1, replied_at = ?
            WHERE id = ?
        """, (replied_at, email_id))
        conn.commit()


def get_all_emails():
    with get_conn() as conn:
        return conn.execute("""
            SELECT * FROM emails ORDER BY sent_at DESC
        """).fetchall()


def get_stats():
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
        replied = conn.execute("SELECT COUNT(*) FROM emails WHERE replied = 1").fetchone()[0]
        by_user = conn.execute("""
            SELECT sender, COUNT(*) as count FROM emails GROUP BY sender
        """).fetchall()
        recent = conn.execute("""
            SELECT * FROM emails ORDER BY sent_at DESC LIMIT 10
        """).fetchall()
        daily = conn.execute("""
            SELECT DATE(sent_at) as day, COUNT(*) as count
            FROM emails
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        """).fetchall()
        return {
            "total": total,
            "replied": replied,
            "reply_rate": round((replied / total * 100) if total else 0, 1),
            "by_user": [dict(r) for r in by_user],
            "recent": [dict(r) for r in recent],
            "daily": [dict(r) for r in daily],
        }
