import os
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent / ".env")

RAILWAY_URL = os.getenv("RAILWAY_URL", "").rstrip("/")
SECRET      = os.getenv("ADMIN_SECRET", "iwc-secret-2024")
HEADERS     = {"X-Secret": SECRET, "Content-Type": "application/json"}


def log_email_remote(sender, client_name, to_address, subject, body):
    if not RAILWAY_URL:
        return
    try:
        requests.post(f"{RAILWAY_URL}/api/log", json={
            "sender": sender,
            "client_name": client_name,
            "to_address": to_address,
            "subject": subject,
            "body": body,
        }, headers=HEADERS, timeout=8)
    except Exception as e:
        print(f"Remote log failed: {e}")


def get_pending_remote():
    if not RAILWAY_URL:
        return []
    try:
        r = requests.get(f"{RAILWAY_URL}/api/pending",
                         headers=HEADERS, timeout=8)
        return r.json()
    except Exception:
        return []


def mark_replied_remote(email_id, replied_at):
    if not RAILWAY_URL:
        return
    try:
        requests.post(f"{RAILWAY_URL}/api/check-replies", json={
            "id": email_id,
            "replied_at": replied_at,
        }, headers=HEADERS, timeout=8)
    except Exception as e:
        print(f"Remote reply update failed: {e}")
