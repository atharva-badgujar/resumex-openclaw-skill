---
name: resumex
version: 2.0.0
description: >
  Manage your Resumex resume directly from Telegram or any OpenClaw-connected chat.
  Read, add, edit, and delete experience, education, skills, projects, achievements,
  and profile details — all through natural conversation. Tailor your resume to a job
  description using your own AI. Send your resume summary to Telegram. All AI processing
  runs on your agent; Resumex is a pure data API.
author: Resumex
license: MIT
metadata:
  openclaw: {"requires":{"env":["RESUMEX_API_KEY"],"bins":["python3","curl"]},"user-invocable":true,"tags":["resume","career","pdf","telegram","productivity"]}
---

# Resumex — Resume Manager Skill

Connect your [Resumex](https://resumex.dev) account and manage your entire resume through
natural conversation — in Telegram, or any OpenClaw-connected channel.

> **Architecture in one line:**
> Resumex stores your data. Your agent's LLM does all the thinking. Your Telegram bot delivers messages.

---

## 🔑 One-Time Setup (2 minutes)

**Step 1 — Get your API key:**
1. Sign in at [resumex.dev](https://resumex.dev)
2. Go to **Dashboard → Resumex API**
3. Click **Generate API Key** → copy the `rx_...` key

**Step 2 — Set environment variables in your OpenClaw agent:**
```
RESUMEX_API_KEY=rx_your_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token     # optional — needed for Telegram delivery
TELEGRAM_CHAT_ID=your_chat_id                  # optional — your personal Telegram chat ID
```

> **Get your Telegram Bot Token:** Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token.
> **Get your Chat ID:** Message [@userinfobot](https://t.me/userinfobot) on Telegram → it replies with your chat ID.
> **API reference:** [resumex.dev/api-docs](https://resumex.dev/api-docs)

---

## 💬 What You Can Say

Write naturally — no special syntax required:

### Profile
| Say... | Effect |
|---|---|
| *"Show my resume"* | Display full resume summary |
| *"What's my profile?"* | Show personal info section |
| *"Update my phone to +91 98765 43210"* | Edit phone field |
| *"Change my location to Pune, India"* | Edit location |
| *"Update my LinkedIn URL"* | Edit LinkedIn |
| *"Rewrite my summary for a senior backend role"* | AI rewrites summary, saves it |

### Experience
| Say... | Effect |
|---|---|
| *"Add a job: SWE at Google, Jan 2024–Present"* | Add new experience entry |
| *"Update my role at Infosys — change end date to Dec 2023"* | Edit existing experience |
| *"Remove my internship at XYZ"* | Delete experience entry |
| *"Show my experience"* | List all work history |

### Education
| Say... | Effect |
|---|---|
| *"Add B.Tech CS at SPPU, 2019–2023, CGPA 8.5"* | Add education entry |
| *"Update my degree at SPPU — fix the end year to 2024"* | Edit education entry |
| *"Remove my 10th standard entry"* | Delete education entry |

### Skills
| Say... | Effect |
|---|---|
| *"Add Python, Docker, Redis to my skills"* | Add to default Skills category |
| *"Add React under Frameworks"* | Add to named category |
| *"Remove Docker from my skills"* | Delete a specific skill |
| *"Delete the Frameworks category"* | Delete entire skill group |

### Projects
| Say... | Effect |
|---|---|
| *"Add a project: RAG Chatbot — built with LangChain..."* | Add project entry |
| *"Update my RAG Chatbot project description"* | Edit project |
| *"Remove the Code Cleaner project"* | Delete project entry |

### Achievements
| Say... | Effect |
|---|---|
| *"Add achievement: Winner at Smart India Hackathon 2024"* | Add achievement entry |
| *"Remove the football achievement"* | Delete achievement entry |

### Tailoring & Delivery
| Say... | Effect |
|---|---|
| *"Tailor my resume for: [paste JD]"* | AI rewrites summary + experience bullets to match JD |
| *"Send me my resume on Telegram"* | Sends formatted resume summary to your Telegram |

---

## 🔧 Tool Reference

All API calls go to `https://resumex.dev/api/v1/agent` with header `Authorization: Bearer $RESUMEX_API_KEY`.

**Two safe update methods:**
- **PATCH** `{"patch": {...}}` → updates only specified fields. Use for profile fields and skills. Always prefer PATCH over POST when possible.
- **POST** `{"workspace": <full_json>}` → replaces the entire workspace. Required when modifying arrays (experience, education, projects, achievements). Always fetch fresh data immediately before a POST.

---

### `resumex_get` — Fetch resume

```bash
curl -s -X GET https://resumex.dev/api/v1/agent \
  -H "Authorization: Bearer $RESUMEX_API_KEY"
```

**Parse the response:**
```
workspace = response.data
activeResume = workspace.resumes.find(r => r.id === workspace.activeResumeId)
resumeData = activeResume.data
```

`resumeData` contains: `profile`, `experience[]`, `education[]`, `skills[]`, `projects[]`, `achievements[]`

Display to user as clean Markdown, grouped by section.

---

### `resumex_update_profile` — Edit profile fields

**Editable fields:** `fullName`, `email`, `phone`, `location`, `website`, `linkedin`, `github`, `summary`

1. PATCH only the changed field(s) — never touch others:
```bash
curl -s -X PATCH https://resumex.dev/api/v1/agent \
  -H "Authorization: Bearer $RESUMEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patch": {"profile": {"phone": "+91 98765 43210"}}}'
```
2. Confirm: `✅ Phone updated to +91 98765 43210.`

---

### `resumex_rewrite_summary` — AI-rewrite profile summary

1. Fetch resume with `resumex_get`.
2. Using your LLM, rewrite `resumeData.profile.summary` for the requested role/tone.
   - 2–3 sentences, active voice, role-specific keywords, no generic buzzwords.
3. Show the user the new summary and ask for confirmation before saving.
4. On confirmation, PATCH:
```bash
curl -s -X PATCH https://resumex.dev/api/v1/agent \
  -H "Authorization: Bearer $RESUMEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patch": {"profile": {"summary": "<rewritten summary>"}}}'
```
5. Confirm: `✅ Summary updated.`

---

### `resumex_add_experience` — Add work experience

1. Extract from user: company, role, location, startDate, endDate, description/bullets.
2. If no description given, use your LLM to generate 2–3 impact-oriented bullet points for the role.
3. Build the entry:
```json
{
  "id": "exp-<unix_timestamp_ms>",
  "company": "Google",
  "role": "Software Engineer",
  "location": "Bangalore, India",
  "startDate": "Jan 2024",
  "endDate": "Present",
  "description": "• Built X achieving Y\n• Led Z resulting in W"
}
```
4. Fetch workspace. **Prepend** the new entry to `resumeData.experience[]`.
5. POST the full modified workspace back:
```bash
curl -s -X POST https://resumex.dev/api/v1/agent \
  -H "Authorization: Bearer $RESUMEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"workspace": <FULL_WORKSPACE_JSON>}'
```
6. Confirm: `✅ Added Software Engineer at Google.`

---

### `resumex_edit_experience` — Edit an existing experience entry

1. Fetch workspace. Find the experience entry by company name or role (case-insensitive match).
2. If multiple matches, ask user to clarify which one.
3. Apply only the user's requested changes to that entry (e.g., fix dates, update bullets).
4. POST the full modified workspace back.
5. Confirm what changed: `✅ Updated end date for Google → Dec 2024.`

---

### `resumex_delete_experience` — Remove an experience entry

1. Fetch workspace. Find the entry by company/role name.
2. If multiple matches, ask user to clarify.
3. **Show the entry to the user and ask for confirmation before deleting.**
4. On confirmation, remove the entry from `resumeData.experience[]`.
5. POST the full modified workspace back.
6. Confirm: `✅ Removed [Role] at [Company].`

---

### `resumex_add_education` — Add education

1. Extract: institution, degree, field, startDate, endDate, score, scoreType (CGPA or Percentage).
2. Build:
```json
{
  "id": "edu-<unix_timestamp_ms>",
  "institution": "Savitribai Phule Pune University",
  "degree": "B.Tech Computer Science",
  "startDate": "2019",
  "endDate": "2023",
  "score": "8.5",
  "scoreType": "CGPA"
}
```
3. Fetch workspace. Prepend to `resumeData.education[]`. POST full workspace.
4. Confirm: `✅ Added B.Tech CS at SPPU.`

---

### `resumex_edit_education` — Edit an education entry

1. Fetch workspace. Find entry by institution or degree name.
2. Apply only the requested changes.
3. POST full modified workspace. Confirm what changed.

---

### `resumex_delete_education` — Remove an education entry

1. Fetch workspace. Find entry. Show it to user and confirm before deleting.
2. Remove from `resumeData.education[]`. POST full workspace.
3. Confirm: `✅ Removed [Degree] from [Institution].`

---

### `resumex_add_skill` — Add skills

1. Extract skill names and optional category from user message. Default category: `"Skills"`.
2. Fetch workspace. Check `resumeData.skills[]` (each item: `{id, category, skills: string[]}`).
3. **If category exists** (case-insensitive): merge new skills in, deduplicating.
4. **If category does not exist**: create `{ "id": "sk-<timestamp>", "category": "...", "skills": [...] }` and append.
5. PATCH only the skills array:
```bash
curl -s -X PATCH https://resumex.dev/api/v1/agent \
  -H "Authorization: Bearer $RESUMEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"patch": {"skills": <UPDATED_SKILLS_ARRAY>}}'
```
6. Confirm: `✅ Added Python, Docker to Skills.`

---

### `resumex_delete_skill` — Remove a skill or skill category

1. Fetch workspace.
2. **Remove single skill:** Find the category containing the skill (case-insensitive). Remove the skill from the `skills[]` array. If the category becomes empty, remove the whole category object.
3. **Remove category:** Remove the entire category object from `resumeData.skills[]`.
4. PATCH the updated skills array back.
5. Confirm: `✅ Removed Docker from Skills.` or `✅ Deleted Frameworks category.`

---

### `resumex_add_project` — Add a project

1. Extract: name, description, tags/technologies, link (optional).
2. Build:
```json
{
  "id": "proj-<unix_timestamp_ms>",
  "name": "RAG-Based Smart Attendance Chatbot",
  "description": "Built a Chat with your Data system using RAG to automate attendance queries, reducing admin time by 40%.",
  "tags": ["RAG", "NLP", "Python"],
  "link": "https://github.com/..."
}
```
3. Fetch workspace. Prepend to `resumeData.projects[]`. POST full workspace.
4. Confirm: `✅ Added project: RAG-Based Smart Attendance Chatbot.`

---

### `resumex_edit_project` — Edit a project

1. Fetch workspace. Find project by name (case-insensitive).
2. Apply only the user's requested changes. POST full workspace.
3. Confirm what changed.

---

### `resumex_delete_project` — Remove a project

1. Fetch workspace. Find project by name. Show it and ask for confirmation.
2. Remove from `resumeData.projects[]`. POST full workspace.
3. Confirm: `✅ Removed project: [Name].`

---

### `resumex_add_achievement` — Add an achievement

1. Extract: title, description (optional), year (optional).
2. Build:
```json
{
  "id": "ach-<unix_timestamp_ms>",
  "title": "Winner — Smart India Hackathon 2024",
  "description": "National-level hackathon with 500+ competing teams.",
  "year": "2024"
}
```
3. Fetch workspace. Append to `resumeData.achievements[]`. POST full workspace.
4. Confirm: `✅ Added achievement: Winner — Smart India Hackathon 2024.`

---

### `resumex_delete_achievement` — Remove an achievement

1. Fetch workspace. Find achievement by title. Show it and confirm before deleting.
2. Remove from `resumeData.achievements[]`. POST full workspace.
3. Confirm: `✅ Removed achievement: [Title].`

---

### `resumex_tailor` — Tailor resume to a job description

> All AI reasoning happens in your agent. Resumex only stores the final result.

1. If the user hasn't pasted a JD, ask: *"Please paste the job description you'd like to tailor for."*
2. Fetch resume with `resumex_get`.
3. **Using your LLM** (not Resumex), do:
   - **Rewrite summary:** 2–3 sentences aligned to the JD's key stack/domain. Active voice, no filler phrases.
   - **Rewrite experience bullets:** Surface JD keywords and impact phrases. **Do not fabricate or add facts** — only re-emphasize what's already there.
   - **Review skills:** Identify skills mentioned in the JD that the user doesn't have listed. Surface them as suggestions and ask before adding.
4. Show a **before/after diff of the summary** to the user. Ask if they want to review full experience changes too.
5. On confirmation, PATCH:
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
6. Confirm: `✅ Resume tailored for [Job Title] at [Company].`

---

### `resumex_send_telegram` — Send resume to Telegram

1. Fetch resume with `resumex_get`.
2. Format a clean resume summary message (see `send_pdf.py` for formatter logic).
3. Run the helper script:
```bash
python3 {baseDir}/send_pdf.py \
  --api-key "$RESUMEX_API_KEY" \
  --chat-id "$TELEGRAM_CHAT_ID" \
  --bot-token "$TELEGRAM_BOT_TOKEN"
```
4. If `TELEGRAM_BOT_TOKEN` or `TELEGRAM_CHAT_ID` are not set, print the formatted resume to stdout and tell the user:
   > *"Here's your resume summary. To get the full PDF, open [resumex.dev/app](https://resumex.dev/app) → click Download PDF or press Ctrl+P → Save as PDF."*

**Note:** Resumex does not generate PDFs server-side. The PDF workflow is:
`Resumex data → your agent → Telegram message + portfolio link → user opens link → Ctrl+P → PDF`

---

## ⚠️ Important Rules for the Agent

1. **Always fetch fresh data immediately before any POST.** Never reuse a workspace fetched earlier in the conversation — the user may have made changes via the web app in between.
2. **Prefer PATCH over POST** for profile fields and skills. Only use POST (full workspace) when modifying arrays.
3. **Always confirm before deleting anything.** Show the item to be deleted and require explicit user confirmation.
4. **Never fabricate data.** When tailoring, only rephrase what already exists.
5. **Match entries by fuzzy name** when the user refers to a company/role — e.g. "my Google job" should match `"company": "Google"`.
6. **When multiple entries match**, list them and ask the user to clarify before proceeding.

---

## 🛡️ Error Handling

| Error | Cause | Fix |
|---|---|---|
| `401 Invalid API Key` | Key wrong or revoked | Dashboard → Resumex API → Regenerate Key |
| `404 No resume found` | No active resume exists | Open resumex.dev/app and save your profile first |
| `HTTP 500` with SQL hint | Admin setup incomplete | Admin must run `api_keys_setup.sql` in Supabase |
| Telegram send fails | Bad token or chat ID | Verify `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` env vars |
| POST overwrites data | Stale workspace used | Always re-fetch before POST — see Rule #1 above |

---

## 🔒 Security

- `RESUMEX_API_KEY` is scoped to your account only.
- `TELEGRAM_BOT_TOKEN` lives in your OpenClaw environment — Resumex never sees it.
- `TELEGRAM_CHAT_ID` lives in your OpenClaw environment — Resumex never sees it.
- All AI work runs locally in your agent. Resumex only stores what you explicitly send.
- Revoke agent access anytime: **Dashboard → Resumex API → Revoke Key.**
- Edits appear live at [resumex.dev](https://resumex.dev) immediately after saving.
