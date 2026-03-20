import os
import sys
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv
import anthropic
import tkinter as tk
from tkinter import messagebox, scrolledtext
from PIL import Image, ImageTk

sys.path.insert(0, str(Path(__file__).parent))
from database import init_db, log_email
from remote import log_email_remote

load_dotenv(Path(__file__).parent.parent / ".env")

SKILL_PATH = Path(__file__).parent.parent / "SKILL.md"
USERS  = ["Carlos Martinez", "John Doe", "Daisy Chain"]
ADMINS = ["Carlos Martinez"]

# Color palette
BG        = "#F4F6F9"
WHITE     = "#FFFFFF"
NAVY      = "#0D1B2A"
NAVY2     = "#1B2A3B"
ACCENT    = "#2563EB"
GREEN     = "#16A34A"
PURPLE    = "#6D28D9"
BORDER    = "#D1D5DB"
TEXT      = "#111827"
SUBTEXT   = "#6B7280"
STATUS_BG = "#E5E7EB"


def load_skill():
    return SKILL_PATH.read_text(encoding="utf-8")


def generate_email(client_name, scenario):
    api_key = os.getenv("ANTHROPIC_API_KEY")
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


def parse_subject(email_text):
    lines = email_text.strip().splitlines()
    for i, line in enumerate(lines):
        if line.lower().startswith("subject:"):
            return line[len("subject:"):].strip(), "\n".join(lines[i+1:]).strip()
    return lines[0].strip(), "\n".join(lines[1:]).strip()


def send_email_smtp(to_address, email_text):
    gmail_address = os.getenv("GMAIL_ADDRESS")
    app_password  = os.getenv("GMAIL_APP_PASSWORD")
    subject, body = parse_subject(email_text)

    msg = MIMEMultipart()
    msg["From"]    = gmail_address
    msg["To"]      = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password)
        server.sendmail(gmail_address, to_address, msg.as_string())

    return subject, body


# ── Reusable widget helpers ──────────────────────────────────────────────────

def field_label(parent, text, hint=None):
    tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"),
             bg=WHITE, fg=TEXT, anchor="w").pack(fill="x", pady=(8, 0))
    if hint:
        tk.Label(parent, text=hint, font=("Segoe UI", 8),
                 bg=WHITE, fg=SUBTEXT, anchor="w").pack(fill="x")


def styled_entry(parent):
    e = tk.Entry(parent, font=("Segoe UI", 10), relief="flat",
                 bg="#F9FAFB", fg=TEXT, insertbackground=TEXT,
                 highlightthickness=1, highlightbackground=BORDER,
                 highlightcolor=ACCENT)
    e.pack(fill="x", pady=(3, 0), ipady=6)
    return e


def styled_button(parent, text, bg, command, state="normal"):
    btn = tk.Button(parent, text=text, font=("Segoe UI", 10, "bold"),
                    bg=bg, fg=WHITE, activebackground=bg, activeforeground=WHITE,
                    relief="flat", cursor="hand2", pady=10,
                    bd=0, command=command, state=state)
    return btn


# ── Main App ─────────────────────────────────────────────────────────────────

class CoreLinkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CoreLink — IWC Email Generator")
        self.root.geometry("580x700")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        try:
            self.root.iconbitmap(Path(__file__).parent / "icon.ico")
        except Exception:
            pass

        init_db()
        self._build_ui()

    def _build_ui(self):
        # ── Status bar (bottom) ──────────────────────────────────────────────
        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self.root, textvariable=self.status_var,
                 font=("Segoe UI", 8), bg=STATUS_BG, fg=SUBTEXT,
                 anchor="w", padx=12, pady=5).pack(fill="x", side="bottom")

        # ── Action buttons (bottom) ──────────────────────────────────────────
        btn_bar = tk.Frame(self.root, bg=BG, padx=20, pady=10)
        btn_bar.pack(fill="x", side="bottom")

        self.send_btn = styled_button(btn_bar, "✉   Send Email", GREEN,
                                      self.on_send, state="disabled")
        self.send_btn.pack(side="left", fill="x", expand=True, padx=(0, 6))

        self.dash_btn = styled_button(btn_bar, "📊   Dashboard", PURPLE,
                                      self.open_dashboard)
        self.dash_btn.pack(side="left", fill="x", expand=True)

        # ── Header ───────────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=NAVY, pady=0)
        header.pack(fill="x", side="top")

        # Logo
        try:
            logo_img = Image.open(Path(__file__).parent / "logo.png")
            logo_img = logo_img.resize((160, 57), Image.LANCZOS)
            self._logo = ImageTk.PhotoImage(logo_img)
            tk.Label(header, image=self._logo, bg=NAVY,
                     padx=20, pady=12).pack(side="left")
        except Exception:
            tk.Label(header, text="IWC", font=("Segoe UI", 18, "bold"),
                     bg=NAVY, fg=WHITE, padx=20, pady=14).pack(side="left")

        # Title on right side of header
        title_frame = tk.Frame(header, bg=NAVY)
        title_frame.pack(side="right", padx=20, pady=12)
        tk.Label(title_frame, text="CoreLink", font=("Segoe UI", 14, "bold"),
                 bg=NAVY, fg=WHITE, anchor="e").pack(anchor="e")
        tk.Label(title_frame, text="AI Email Generator", font=("Segoe UI", 9),
                 bg=NAVY, fg="#90A4AE", anchor="e").pack(anchor="e")

        # Thin accent line under header
        tk.Frame(self.root, bg=ACCENT, height=3).pack(fill="x", side="top")

        # ── Scrollable middle area ───────────────────────────────────────────
        card = tk.Frame(self.root, bg=WHITE, padx=24, pady=4,
                        highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="both", expand=True, padx=16, pady=12, side="top")

        # Who are you
        field_label(card, "Who Are You?")
        self.user_var = tk.StringVar(value=USERS[0])
        self.user_var.trace_add("write", self._on_user_change)
        dd = tk.OptionMenu(card, self.user_var, *USERS)
        dd.config(font=("Segoe UI", 10), relief="flat", bg="#F9FAFB", fg=TEXT,
                  activebackground="#EFF6FF", bd=0,
                  highlightthickness=1, highlightbackground=BORDER,
                  highlightcolor=ACCENT, pady=6, anchor="w")
        dd["menu"].config(font=("Segoe UI", 10), bg=WHITE, fg=TEXT)
        dd.pack(fill="x", pady=(3, 0))

        # Divider
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=10)

        # Client name
        field_label(card, "Client Name")
        self.name_entry = styled_entry(card)

        # Scenario
        field_label(card, "Scenario",
                    "e.g.  'Sent a proposal Tuesday — no reply yet'")
        self.scenario_entry = tk.Text(card, font=("Segoe UI", 10), relief="flat",
                                      bg="#F9FAFB", fg=TEXT, height=2, wrap="word",
                                      highlightthickness=1, highlightbackground=BORDER,
                                      highlightcolor=ACCENT, padx=4, pady=4)
        self.scenario_entry.pack(fill="x", pady=(3, 0))

        # Send to
        field_label(card, "Recipient Email Address")
        self.to_entry = styled_entry(card)

        # Divider
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", pady=10)

        # Generate button
        self.generate_btn = styled_button(card, "⚡   Generate Email",
                                          ACCENT, self.on_generate)
        self.generate_btn.pack(fill="x")

        # Generated email label
        field_label(card, "Generated Email")
        self.email_box = scrolledtext.ScrolledText(
            card, font=("Segoe UI", 9), relief="flat",
            bg="#F9FAFB", fg=TEXT, height=7, wrap="word",
            state="disabled", highlightthickness=1,
            highlightbackground=BORDER, padx=6, pady=6)
        self.email_box.pack(fill="both", expand=True, pady=(3, 8))

    def _on_user_change(self, *_):
        is_admin = self.user_var.get() in ADMINS
        self.dash_btn.config(state="normal" if is_admin else "disabled",
                             bg=PURPLE if is_admin else BORDER,
                             fg=WHITE if is_admin else SUBTEXT)

    def set_status(self, msg):
        self.status_var.set(msg)
        self.root.update_idletasks()

    def on_generate(self):
        client_name = self.name_entry.get().strip()
        scenario    = self.scenario_entry.get("1.0", "end").strip()

        if not client_name:
            messagebox.showwarning("Missing Info", "Please enter a client name.")
            return
        if not scenario:
            messagebox.showwarning("Missing Info", "Please describe the scenario.")
            return

        self.generate_btn.config(state="disabled", text="Generating…")
        self.send_btn.config(state="disabled")
        self.set_status("Generating email with Claude AI…")

        def run():
            try:
                email_text = generate_email(client_name, scenario)
                self.current_email = email_text
                self.email_box.config(state="normal")
                self.email_box.delete("1.0", "end")
                self.email_box.insert("1.0", email_text)
                self.email_box.config(state="disabled")
                self.send_btn.config(state="normal")
                self.set_status("Email ready — review and send.")
            except Exception as e:
                messagebox.showerror("Error", str(e))
                self.set_status("Error generating email.")
            finally:
                self.generate_btn.config(state="normal",
                                         text="⚡   Generate Email")

        threading.Thread(target=run, daemon=True).start()

    def on_send(self):
        to_address  = self.to_entry.get().strip()
        client_name = self.name_entry.get().strip()
        sender      = self.user_var.get()
        email_text  = self.email_box.get("1.0", "end").strip()

        if not to_address:
            messagebox.showwarning("Missing Info",
                                   "Please enter a recipient email address.")
            return

        self.send_btn.config(state="disabled", text="Sending…")
        self.set_status(f"Sending to {to_address}…")

        def run():
            try:
                subject, body = send_email_smtp(to_address, email_text)
                log_email(sender, client_name, to_address, subject, body)
                log_email_remote(sender, client_name, to_address, subject, body)
                messagebox.showinfo("Sent!", f"Email sent to {to_address}.")
                self.set_status("Email sent and logged.")
            except Exception as e:
                messagebox.showerror("Send Failed", str(e))
                self.set_status("Failed to send.")
            finally:
                self.send_btn.config(state="normal", text="✉   Send Email")

        threading.Thread(target=run, daemon=True).start()

    def open_dashboard(self):
        import subprocess
        python    = str(Path(sys.executable).parent / "python.exe")
        dashboard = str(Path(__file__).parent / "dashboard.py")
        subprocess.Popen([python, dashboard])
        self.set_status("Dashboard opening in browser…")


if __name__ == "__main__":
    root = tk.Tk()
    app  = CoreLinkApp(root)
    root.mainloop()
