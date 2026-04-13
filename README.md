# Resumex — OpenClaw Skill

> **Manage your entire resume through Telegram or any AI chat interface.**  
> Edit profile, add jobs, tailor to JDs, and get your resume PDF — all via natural language.

---

## ⚡ Quick Start

### 1. Get your Resumex API Key
1. Sign in at [resumex.dev](https://resumex.dev)
2. Go to **Dashboard → Resumex API card**
3. Click **"Generate API Key"**
4. Copy the key (looks like `rx_abc123...`)

### 2. Install the Skill
In OpenClaw, install this skill and set your environment variable:
```
RESUMEX_API_KEY=rx_your_key_here
```

### 3. Start chatting 🎉
Open Telegram (or any connected channel) and try:
- *"Show my resume"*
- *"Update my phone to +91 9876543210"*
- *"Add Python and Docker to my skills"*
- *"Send me my resume as PDF"*

---

## 📋 All Commands

| What you say | What happens |
|---|---|
| "Show my resume" / "What's my profile?" | Displays your full resume summary |
| "Update my [field] to [value]" | Updates any profile field |
| "Add a job at [company] as [role]..." | Adds new work experience |
| "Add [degree] at [university]..." | Adds new education entry |
| "Add [skills] to my skills" | Adds skills to default or named category |
| "Tailor my resume for: [JD]" | AI rewrites summary + experience for the job |
| "Send me my resume as PDF" / "Get PDF" | Sends a formatted resume + download link |

---

## 🔧 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `RESUMEX_API_KEY` | ✅ Yes | Your personal Resumex API key |
| `TELEGRAM_BOT_TOKEN` | Optional | Your Telegram bot token (for direct file sending) |

---

## 🌐 API Endpoint

All operations hit:
```
https://resumex.dev/api/v1/agent
```

See [resumex.dev/api-docs](https://resumex.dev/api-docs) for the full reference.

---

## 🔒 Security

- Your API key is scoped to your account only
- Revoke it anytime from Dashboard → Resumex API → Revoke
- The skill never stores credentials — they live in your OpenClaw environment

---

## License

MIT-0 — free to use, modify, and redistribute.
