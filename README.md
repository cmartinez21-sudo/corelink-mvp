# CoreLink MVP — Client Email Generator

CoreLink is your AI-powered follow-up email kit. Fill in your business details once, then generate on-brand client emails in seconds.

---

## What's in This Kit

| File | Purpose |
|------|---------|
| `SKILL.md` | Your business brain — fill this out first |
| `src/email_generator.py` | The email generator script |
| `.env` | Holds your Anthropic API key (private) |
| `output/` | Generated emails are saved here |

---

## Step 1 — Fill Out SKILL.md

Open `SKILL.md` and replace all the placeholder text with your real business info:

- Your business name, tone, and sign-off style
- Your products/services
- Who your customers are
- What a typical follow-up looks like

**This is the most important step.** The better you fill it out, the better your emails will sound.

---

## Step 2 — Set Up (One Time Only)

You need Python 3.8+ installed.

Open a terminal in the `corelink-mvp` folder and run:

```bash
pip install -r requirements.txt
```

Your API key is already saved in `.env`. You're ready to go.

---

## Step 3 — Generate an Email

In your terminal, run:

```bash
python src/email_generator.py
```

You'll be asked two questions:

1. **Client name** — Who is the email going to? (e.g. `Sarah at Peak Plumbing`)
2. **Scenario** — What's the situation? (e.g. `sent a quote 3 days ago, no reply`)

The AI will draft a follow-up email in your brand voice. You can save it to the `output/` folder or copy it directly.

---

## Example

```
=== CoreLink Email Generator ===

Client name: Mike Torres
Scenario: completed a kitchen renovation last week, want to ask for a review

Generating email...

==================================================
Subject: Quick note from [Your Business]

Hi Mike,

It was great working on your kitchen — hope you're loving the new space!

If you have a moment, we'd really appreciate a quick Google review. It helps
other homeowners find us and means a lot to our small team.

[Link to your Google review page]

Thanks again for trusting us with the project.

Warmly,
[Your Name]
==================================================

Save to file? (y/n):
```

---

## Tips

- **Be specific with the scenario** — "sent a quote Tuesday, client seemed interested but went quiet" gets a better email than just "follow up."
- **Edit before sending** — The AI gets you 90% there. Always read it over and add personal details.
- **Update SKILL.md anytime** — If you add a new service or change your tone, update the file and the AI adapts immediately.
- **Saved emails** — Find them in the `output/` folder, named by client.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `ANTHROPIC_API_KEY not set` | Check that `.env` exists and contains your key |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Email sounds too generic | Add more detail to `SKILL.md` — especially brand voice and customer description |

---

*Built with CoreLink MVP — powered by Claude (Anthropic)*
