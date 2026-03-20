import os
import psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, jsonify, abort
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "iwc-secret-2024")

# Initialize DB on startup
try:
    init_db()
except Exception as e:
    print(f"DB init warning: {e}")


def get_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"), sslmode="require")


def init_db():
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id SERIAL PRIMARY KEY,
                    sender TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    sent_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    replied BOOLEAN DEFAULT FALSE,
                    replied_at TIMESTAMP
                )
            """)
        conn.commit()


# ── API endpoints (used by desktop app) ─────────────────────────────────────

@app.route("/api/log", methods=["POST"])
def api_log():
    if request.headers.get("X-Secret") != ADMIN_SECRET:
        abort(403)
    data = request.json
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO emails (sender, client_name, to_address, subject, body, sent_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data["sender"], data["client_name"], data["to_address"],
                  data["subject"], data["body"], datetime.utcnow()))
        conn.commit()
    return jsonify({"status": "ok"})


@app.route("/api/check-replies", methods=["POST"])
def api_check_replies():
    if request.headers.get("X-Secret") != ADMIN_SECRET:
        abort(403)
    data = request.json
    email_id   = data["id"]
    replied_at = data["replied_at"]
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE emails SET replied = TRUE, replied_at = %s WHERE id = %s
            """, (replied_at, email_id))
        conn.commit()
    return jsonify({"status": "ok"})


@app.route("/api/pending")
def api_pending():
    if request.headers.get("X-Secret") != ADMIN_SECRET:
        abort(403)
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("""
                SELECT id, to_address, sent_at FROM emails
                WHERE replied = FALSE
            """)
            rows = cur.fetchall()
    return jsonify([dict(r) for r in rows])


# ── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/")
def dashboard():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS total FROM emails")
            total = cur.fetchone()["total"]

            cur.execute("SELECT COUNT(*) AS replied FROM emails WHERE replied = TRUE")
            replied = cur.fetchone()["replied"]

            cur.execute("""
                SELECT sender, COUNT(*) AS count FROM emails GROUP BY sender
            """)
            by_user = cur.fetchall()

            cur.execute("""
                SELECT sender, client_name, to_address, subject,
                       sent_at, replied, replied_at
                FROM emails ORDER BY sent_at DESC LIMIT 20
            """)
            recent = cur.fetchall()

            cur.execute("""
                SELECT DATE(sent_at) AS day, COUNT(*) AS count
                FROM emails
                GROUP BY day ORDER BY day DESC LIMIT 7
            """)
            daily = cur.fetchall()

    reply_rate = round((replied / total * 100) if total else 0, 1)

    stats = {
        "total": total,
        "replied": replied,
        "reply_rate": reply_rate,
        "by_user": [dict(r) for r in by_user],
        "recent": [dict(r) for r in recent],
        "daily": [dict(r) for r in daily],
    }
    return render_template("dashboard.html", stats=stats)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5050)))
