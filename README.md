# Resumex — OpenClaw Skill

> **Manage your entire resume through Telegram or any AI chat interface.**
> Edit profile, add/edit/remove jobs, projects, skills, education, achievements —
> tailor to a job description — and get your resume link to Telegram. All via natural language.

---

## How It Works

| Responsibility | Who handles it |
|---|---|
| Store & retrieve resume data | ✅ **Resumex API** |
| AI rewriting (tailor, summarize, bullets) | ✅ **Your OpenClaw agent's LLM** |
| Sending Telegram messages | ✅ **Your Telegram bot token** |
| PDF generation | ✅ **You** — open portfolio link → Ctrl+P → Save as PDF |
| Resumex AI (Gemini) | Only on [resumex.dev](https://resumex.dev) in the browser |

**Resumex never calls any AI API on your behalf. It is a pure data API.**

---

## ⚡ Quick Start

### 1. Get your Resumex API Key
1. Sign in at [resumex.dev](https://resumex.dev)
2. Go to **Dashboard → Resumex API**
3. Click **Generate API Key** → copy the `rx_...` key

### 2. Get your Telegram credentials *(optional — for message delivery)*
- **Bot Token:** Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
- **Chat ID:** Message [@userinfobot](https://t.me/userinfobot) → it replies with your numeric ID

### 3. Set environment variables in OpenClaw
```
RESUMEX_API_KEY=rx_your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token        # optional
TELEGRAM_CHAT_ID=your_numeric_chat_id   # optional
```

### 4. Start chatting 🎉
Try:
- *"Show my resume"*
- *"Update my phone to +91 98765 43210"*
- *"Add Python and Docker to my skills"*
- *"Add a job: SWE at Google, Jan 2024–Present"*
- *"Remove my internship at XYZ Corp"*
- *"Tailor my resume for: [paste job description]"*
- *"Send me my resume on Telegram"*

---

## 📋 All Commands

### Profile
| Say... | Effect |
|---|---|
| *"Show my resume"* | Full resume summary |
| *"Update my [field] to [value]"* | Edit any profile field |
| *"Rewrite my summary as a senior backend engineer"* | AI rewrites summary, asks for confirmation before saving |

### Experience
| Say... | Effect |
|---|---|
| *"Add a job at [Company] as [Role]..."* | Add new experience entry |
| *"Update my role at [Company] — change [field]"* | Edit existing entry |
| *"Remove my job at [Company]"* | Delete entry (requires confirmation) |

### Education
| Say... | Effect |
|---|---|
| *"Add [Degree] at [University]..."* | Add education entry |
| *"Update my degree at [University]"* | Edit entry |
| *"Remove my [Degree] entry"* | Delete entry (requires confirmation) |

### Skills
| Say... | Effect |
|---|---|
| *"Add [skills] to my skills"* | Add to default Skills category |
| *"Add [skill] under [Category]"* | Add to named category |
| *"Remove [skill] from my skills"* | Delete a single skill |
| *"Delete the [Category] category"* | Delete entire skill group |

### Projects
| Say... | Effect |
|---|---|
| *"Add a project: [Name] — [description]"* | Add project |
| *"Update my [project name] project"* | Edit project |
| *"Remove the [project name] project"* | Delete project (requires confirmation) |

### Achievements
| Say... | Effect |
|---|---|
| *"Add achievement: [title]"* | Add achievement |
| *"Remove the [achievement] entry"* | Delete achievement (requires confirmation) |

### Tailoring & Delivery
| Say... | Effect |
|---|---|
| *"Tailor my resume for: [JD]"* | Agent AI rewrites summary + experience bullets to match JD |
| *"Send me my resume on Telegram"* | Formatted summary + PDF link sent to your Telegram |

---

## 🔧 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `RESUMEX_API_KEY` | ✅ Yes | Your personal Resumex data access key (`rx_...`) |
| `TELEGRAM_BOT_TOKEN` | Optional | Your Telegram bot token — for message delivery |
| `TELEGRAM_CHAT_ID` | Optional | Your personal Telegram chat ID — for message delivery |

---

## 🌐 API Endpoint

```
https://resumex.dev/api/v1/agent
```

Full reference: [resumex.dev/api-docs](https://resumex.dev/api-docs)

**Two update methods:**
- `PATCH {"patch": {...}}` — safe partial update, for profile fields and skills
- `POST {"workspace": <full_json>}` — full workspace replace, for arrays (experience, projects, etc.)

Always fetch fresh data immediately before a POST to avoid overwriting concurrent changes.

---

## 📄 PDF Workflow

Resumex does not generate PDFs server-side. The intended workflow:

1. Your agent sends your resume summary + portfolio link to Telegram via `send_pdf.py`
2. You open your portfolio (`https://yourname.resumex.dev`)
3. Press **Ctrl+P** (or ⌘+P on Mac) → **Save as PDF**

Alternatively: open [resumex.dev/app](https://resumex.dev/app) → click **Download PDF** in the top bar.

---

## 🛡️ Error Reference

| Error | Fix |
|---|---|
| `401 Invalid API Key` | Dashboard → Resumex API → Regenerate Key |
| `404 No resume found` | Open resumex.dev/app and save your profile first |
| `HTTP 500` + SQL hint | Admin must run `api_keys_setup.sql` in Supabase |
| Telegram message fails | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` |
| Data loss on POST | Always re-fetch workspace immediately before POST |

---

## 🔒 Security & Privacy

- `RESUMEX_API_KEY` is scoped to your account only — no one else can use it
- `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are stored in **your** OpenClaw environment — Resumex never sees them
- Resumex never calls OpenAI, Gemini, or any LLM via this skill
- All AI computation runs inside your OpenClaw agent
- Revoke API access anytime: **Dashboard → Resumex API → Revoke**

---

## License

MIT-0 — free to use, modify, and redistribute.
