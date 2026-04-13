# Resumex — OpenClaw Skill

> **Manage your entire resume through Telegram or any AI chat interface.**  
> Edit profile, add jobs, tailor to JDs, and get your resume PDF — all via natural language.

---

## ⚙️ Architecture (Important)

Understanding what Resumex does vs. what *your agent* does:

| What | Who does it |
|---|---|
| Store and retrieve resume data | ✅ **Resumex API** |
| AI rewriting (tailor, summarize, bullets) | ✅ **Your OpenClaw agent's LLM** |
| PDF generation | ✅ **Your side** (browser print or Puppeteer) |
| Sending Telegram messages/files | ✅ **Your Telegram bot token** |
| Resumex AI (Gemini) | Only when you use resumex.dev in the browser |

**Resumex never calls any AI API on your behalf when using this skill.** It is a pure data API.

---

## ⚡ Quick Start

### 1. Get your Resumex API Key
1. Sign in at [resumex.dev](https://resumex.dev)
2. Go to **Dashboard → Resumex API** card
3. Click **"Generate API Key"** → copy it (`rx_...`)

### 2. Set environment variables
In your OpenClaw agent settings:
```
RESUMEX_API_KEY=rx_your_key_here
TELEGRAM_BOT_TOKEN=your_bot_token   # optional, for PDF/message sending
```

> To get a Telegram bot token: open Telegram → message [@BotFather](https://t.me/BotFather) → /newbot → copy the token.

### 3. Start chatting 🎉
Open Telegram (or any connected channel) and try:
- *"Show my resume"*
- *"Update my phone to +91 9876543210"*
- *"Add Python and Docker to my skills"*
- *"Tailor my resume for: [paste job description]"*
- *"Send me my resume as a PDF"*

---

## 📋 All Commands

| What you say | What happens |
|---|---|
| "Show my resume" / "What's my profile?" | Displays your full resume summary |
| "Update my [field] to [value]" | Updates any profile field |
| "Add a job at [company] as [role]..." | Adds new work experience |
| "Add [degree] at [university]..." | Adds new education entry |
| "Add [skills] to my skills" | Adds skills (optionally to a named category) |
| "Tailor my resume for: [JD]" | **Your agent's AI** rewrites summary + experience |
| "Send me my resume as PDF" / "Get PDF" | Sends formatted resume + portfolio link to Telegram |

---

## 🔧 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `RESUMEX_API_KEY` | ✅ Yes | Your personal Resumex data access key |
| `TELEGRAM_BOT_TOKEN` | Optional | **Your** Telegram bot token for message delivery |

---

## 🌐 API Endpoint

All data operations hit:
```
https://resumex.dev/api/v1/agent
```

See [resumex.dev/api-docs](https://resumex.dev/api-docs) for the full reference.

---

## 🔒 Security & Privacy

- `RESUMEX_API_KEY` is scoped to your account only — nobody else can use it
- `TELEGRAM_BOT_TOKEN` is stored in **your** OpenClaw environment — Resumex never sees it
- Resumex never calls OpenAI, Gemini, or any LLM on your behalf through this skill
- Revoke API access anytime: Dashboard → Resumex API → Revoke

---

## License

MIT-0 — free to use, modify, and redistribute.
