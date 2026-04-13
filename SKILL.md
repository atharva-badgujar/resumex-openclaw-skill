---
name: resumex
version: 1.1.0
description: >
  Manage your Resumex resume directly from Telegram or any OpenClaw-connected chat.
  Read your resume, update profile details, add experience and skills, tailor to a job
  description using YOUR AI, and send your resume as a PDF — all through natural conversation.
  Resumex only stores your data. All AI processing and PDF generation runs on your agent.
author: Resumex
license: MIT
metadata:
  openclaw: {"requires":{"env":["RESUMEX_API_KEY"],"bins":["python3","curl"]},"user-invocable":true,"tags":["resume","career","pdf","telegram","productivity"]}
---

# Resumex — Resume Manager Skill

Connect your [Resumex](https://resumex.dev) account to your AI agent and control your resume entirely through chat.

> **How it works:**
> - **Resumex API** → pure data storage and retrieval. No AI, no PDF rendering.
> - **Your AI (this agent)** → does all the intelligence: tailoring, rewriting, formatting decisions.
> - **Your Telegram bot** → sends the PDF file. Resumex never touches your Telegram.
> - **PDF generation** → happens on your machine/agent, not on Resumex servers.

---

## 🔑 Setup (one time, 2 minutes)

**Step 1 — Get your Resumex API Key:**
1. Sign in at [resumex.dev](https://resumex.dev)
2. Go to **Dashboard → Resumex API** card
3. Click **"Generate API Key"** → copy the key (`rx_...`)

**Step 2 — Set environment variables in your OpenClaw agent:**
```
RESUMEX_API_KEY=rx_your_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token   # optional, for PDF sending
```

**Step 3 — Start chatting.** That's it.

> For your Telegram Bot Token: create a bot with [@BotFather](https://t.me/BotFather) on Telegram, copy the token it gives you.
> The API docs are at [resumex.dev/api-docs](https://resumex.dev/api-docs).

---

## 💬 What You Can Say

Just write naturally — no special commands:

| Say... | Effect |
|---|---|
| *"Show my resume"* | Displays your full resume summary |
| *"What are my skills?"* | Lists all skill categories |
| *"Show my experience"* | Lists all work history |
| *"Update my phone to +91 98765 43210"* | Edits your phone field |
| *"Change my location to Bangalore, India"* | Edits your location |
| *"Update my LinkedIn to linkedin.com/in/you"* | Edits LinkedIn URL |
| *"Rewrite my summary as a senior backend engineer"* | Your AI rewrites it, saves it |
| *"Add a job: SWE at Google, Jan 2024 to Present"* | Adds work experience |
| *"Add B.Tech CS at SPPU, 2019–2023, CGPA 8.5"* | Adds education |
| *"Add Python, Docker, and Redis to my skills"* | Adds to default Skills category |
| *"Add React under Frameworks"* | Adds to a named category |
| *"Tailor my resume for: [paste JD]"* | **Your AI** rewrites summary + experience for the job |
| *"Send me my resume as a PDF"* | Sends formatted resume + download link to Telegram |

---

## How It Works — Tool Reference

All data operations hit `https://resumex.dev/api/v1/agent` using your `RESUMEX_API_KEY`.
**No AI calls are made to Resumex servers.** Your agent's LLM handles all reasoning.

---

### Tool: `resumex_get`
Fetch the current resume data.

**Steps:**
1. Call the Resumex API:
   ```bash
   curl -s -X GET https://resumex.dev/api/v1/agent \
     -H "Authorization: Bearer $RESUMEX_API_KEY"
   ```
2. Parse the JSON. `response.data` is the full workspace.
3. Find the active resume: the entry in `data.resumes[]` where `id == data.activeResumeId`.
4. The active resume's content is at `activeResume.data`.
5. Present it to the user in clean Markdown.

---

### Tool: `resumex_update_profile`
Update any field(s) in the profile section.

**Steps:**
1. Call `resumex_get` to get the current workspace JSON.
2. In your working copy, locate the active resume and update `activeResume.data.profile` with the requested field(s).
   - Updatable fields: `fullName`, `email`, `phone`, `location`, `website`, `linkedin`, `github`, `summary`
   - Only change the fields the user asked about. Leave all others untouched.
3. PATCH back only the changed profile fields (minimal, safe update):
   ```bash
   curl -s -X PATCH https://resumex.dev/api/v1/agent \
     -H "Authorization: Bearer $RESUMEX_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"patch": {"profile": {"phone": "+91 98765 43210"}}}'
   ```
4. Confirm what changed (e.g. "✅ Phone updated to +91 98765 43210").

---

### Tool: `resumex_add_experience`
Add a new work experience entry.

**Steps:**
1. Extract the details from the user's message: company, role, location, start date, end date, and any description they provide.
2. Generate bullet points for the `description` field if the user didn't provide them — use your AI to write 2–3 impactful achievement-oriented bullets based on the role.
3. Build the new entry:
   ```json
   {
     "id": "exp-<current unix timestamp>",
     "company": "<Company Name>",
     "role": "<Job Title>",
     "location": "<City, Country or Remote>",
     "startDate": "<e.g. Jan 2024>",
     "endDate": "<e.g. Present>",
     "description": "• Built X that achieved Y\n• Led Z resulting in W"
   }
   ```
4. Fetch the current workspace. Prepend this entry to `activeResume.data.experience`.
5. POST the entire modified workspace back:
   ```bash
   curl -s -X POST https://resumex.dev/api/v1/agent \
     -H "Authorization: Bearer $RESUMEX_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"workspace": <FULL_WORKSPACE_JSON>}'
   ```
6. Confirm: "✅ Added [Role] at [Company]."

---

### Tool: `resumex_add_education`
Add a new education entry.

**Steps:**
1. Extract: institution, degree, field of study, start year, end year, score (CGPA or percent).
2. Build the entry:
   ```json
   {
     "id": "edu-<timestamp>",
     "institution": "<University Name>",
     "degree": "<e.g. B.Tech Computer Science>",
     "startDate": "<e.g. 2019>",
     "endDate": "<e.g. 2023>",
     "score": "<e.g. 8.5>",
     "scoreType": "<CGPA or Percentage>"
   }
   ```
3. Fetch the workspace. Prepend to `activeResume.data.education`. POST back the full workspace.
4. Confirm: "✅ Added [Degree] from [University]."

---

### Tool: `resumex_add_skill`
Add skills to a category.

**Steps:**
1. Parse the user's message to extract skill names and optional category.
   - Default category: `"Skills"` if none specified.
2. Fetch the workspace. Look at `activeResume.data.skills` (array of `{id, category, skills: string[]}`).
3. **If category exists** (case-insensitive match): merge new skills into `skills[]`, deduplicating.
4. **If category doesn't exist**: create `{ "id": "sk-<timestamp>", "category": "<Name>", "skills": [...] }` and append.
5. PATCH only the skills array:
   ```bash
   curl -s -X PATCH https://resumex.dev/api/v1/agent \
     -H "Authorization: Bearer $RESUMEX_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"patch": {"skills": <UPDATED_SKILLS_ARRAY>}}'
   ```
6. Confirm: "✅ Added [skills] to [Category]."

---

### Tool: `resumex_tailor`
Tailor the resume to a job description — **using your AI, not Resumex servers**.

**Steps:**
1. Ask the user: "Please paste the job description you want to tailor for." (if not already provided)
2. Fetch the resume with `resumex_get`.
3. **Using your own LLM reasoning**, do the following (Resumex is not involved in this step):
   - Rewrite `activeResume.data.profile.summary`: 2–3 sentences, aligns with the job's key stack/domain, active voice, no generic buzzwords.
   - For each entry in `activeResume.data.experience`: reword `description` bullet points to surface keywords and impact phrases from the JD. Do NOT fabricate or add facts — only re-emphasize what's already there.
   - Review `activeResume.data.skills`: suggest any skills mentioned in the JD that the user should add (ask before adding).
4. PATCH only the fields you changed:
   ```bash
   curl -s -X PATCH https://resumex.dev/api/v1/agent \
     -H "Authorization: Bearer $RESUMEX_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "patch": {
         "profile": {"summary": "<rewritten>"},
         "experience": [<rewritten experience array>]
       }
     }'
   ```
5. Show a before/after of the summary. Ask if the user wants to review the full experience changes too.

> **Note:** All AI computation happens locally in your agent. Resumex.dev only stores the final result.

---

### Tool: `resumex_send_pdf`
Send the user's resume to Telegram as a formatted message and PDF link.

**⚠️ Important:** Resumex does not generate PDFs. Your agent and Telegram bot handle delivery. We only provide the resume data.

**Steps:**
1. Fetch the resume with `resumex_get`.
2. Extract the profile info and format a clean Telegram message yourself (your agent does this).
3. Run the helper script using your bot token:
   ```bash
   python3 {baseDir}/send_pdf.py \
     --api-key "$RESUMEX_API_KEY" \
     --chat-id "<TELEGRAM_CHAT_ID>" \
     --bot-token "$TELEGRAM_BOT_TOKEN"
   ```
   The script:
   - Fetches resume data from Resumex (data only, no AI)
   - Formats it as a Telegram message **entirely client-side**
   - Sends the message using **your** `TELEGRAM_BOT_TOKEN`
   - Sends a portfolio link if available (for browser PDF printing)
   
4. If `TELEGRAM_BOT_TOKEN` is not set, print the formatted resume to stdout and tell the user:
   > "Here's your resume data. To get a PDF: open https://resumex.dev/app → press Ctrl+P → Save as PDF."

> **No PDF is generated on Resumex servers.** The PDF workflow is:
> Data from Resumex → your agent → Telegram → user opens portfolio link → user does Print → PDF.

---

## 🛡️ Error Handling

| Error | Fix |
|---|---|
| `"Invalid API Key"` | Go to Dashboard → Resumex API → Regenerate Key |
| `"No resume found"` | Open resumex.dev/app and save your profile first |
| `HTTP 500` + hint about `api_keys_setup.sql` | Admin needs to run the SQL setup in Supabase |
| Telegram send fails | Check `TELEGRAM_BOT_TOKEN` is set and the bot has permission to message you |

---

## 📎 Notes

- `RESUMEX_API_KEY` is your personal data access key — scope is your account only.
- `TELEGRAM_BOT_TOKEN` is **your own bot token** — Resumex never has access to it.
- All AI work (tailoring, bullet generation, formatting) runs on your OpenClaw agent.
- Resumex only receives and stores the final data you send via POST/PATCH.
- Edits appear live at [resumex.dev](https://resumex.dev) immediately after saving.
- To revoke agent access: Dashboard → Resumex API → Revoke Key.
