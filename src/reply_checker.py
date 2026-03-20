import imaplib
import email
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from database import get_conn, mark_replied

load_dotenv(Path(__file__).parent.parent / ".env")


def check_replies():
    gmail_address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address or not app_password:
        return

    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(gmail_address, app_password)
        mail.select("inbox")

        with get_conn() as conn:
            pending = conn.execute("""
                SELECT id, to_address, sent_at FROM emails WHERE replied = 0
            """).fetchall()

        for row in pending:
            email_id, to_address, sent_at = row["id"], row["to_address"], row["sent_at"]
            sent_date = datetime.fromisoformat(sent_at)
            date_str = sent_date.strftime("%d-%b-%Y")

            # Search for emails FROM the client received after the send date
            _, data = mail.search(None,
                f'(FROM "{to_address}" SINCE "{date_str}")')

            msg_ids = data[0].split()
            if msg_ids:
                # Get date of first reply
                _, msg_data = mail.fetch(msg_ids[0], "(ENVELOPE)")
                replied_at = datetime.now().isoformat()
                mark_replied(email_id, replied_at)

        mail.logout()

    except Exception as e:
        print(f"Reply check error: {e}")


if __name__ == "__main__":
    check_replies()
    print("Reply check complete.")
