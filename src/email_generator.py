import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
import anthropic

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"


def load_skill():
    if not SKILL_PATH.exists():
        print("ERROR: SKILL.md not found. Run this from the corelink-mvp folder.")
        sys.exit(1)
    return SKILL_PATH.read_text(encoding="utf-8")


def generate_email(client_name: str, scenario: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set. Check your .env file.")
        sys.exit(1)

    skill_context = load_skill()
    client = anthropic.Anthropic(api_key=api_key)

    system_prompt = f"""You are an expert email copywriter for small businesses.
You write follow-up emails that sound human, warm, and on-brand.
Never use generic filler phrases like "I hope this email finds you well."
Keep emails short — under 150 words unless the scenario demands more.
Always end with the sign-off style specified in SKILL.md.

Here is the client's business context (SKILL.md):

{skill_context}
"""

    user_prompt = f"""Write a follow-up email for this client and scenario:

Client name: {client_name}
Scenario: {scenario}

Output ONLY the email — subject line first, then a blank line, then the body.
No commentary, no explanations."""

    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return response.content[0].text


def parse_subject(email_text: str):
    lines = email_text.strip().splitlines()
    subject = ""
    body_lines = []
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            subject = line[len("subject:"):].strip()
            body_lines = lines[i + 1:]
            break
    else:
        # First line is subject even without "Subject:" prefix
        subject = lines[0].strip()
        body_lines = lines[1:]

    body = "\n".join(body_lines).strip()
    return subject, body


def send_email(to_address: str, email_text: str):
    gmail_address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address or not app_password:
        print("ERROR: Gmail credentials not set in .env file.")
        sys.exit(1)

    subject, body = parse_subject(email_text)

    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    print(f"\nSending to {to_address}...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, to_address, msg.as_string())

    print(f"Email sent to {to_address}.")


def main():
    print("=== CoreLink Email Generator ===\n")

    client_name = input("Client name: ").strip()
    if not client_name:
        print("ERROR: Client name cannot be empty.")
        sys.exit(1)

    print("Scenario (e.g. 'sent a quote 3 days ago, no reply'):")
    scenario = input("> ").strip()
    if not scenario:
        print("ERROR: Scenario cannot be empty.")
        sys.exit(1)

    print("\nGenerating email...\n")
    email = generate_email(client_name, scenario)

    print("=" * 50)
    print(email)
    print("=" * 50)

    action = input("\nWhat do you want to do?\n  [s] Send now\n  [f] Save to file\n  [n] Nothing\n> ").strip().lower()

    if action == "s":
        to_address = input("Send to (email address): ").strip()
        if to_address:
            send_email(to_address, email)
        else:
            print("No address entered. Email not sent.")

    elif action == "f":
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        safe_name = client_name.replace(" ", "_").lower()
        output_file = output_dir / f"email_{safe_name}.txt"
        output_file.write_text(email, encoding="utf-8")
        print(f"Saved to: {output_file}")


if __name__ == "__main__":
    main()
