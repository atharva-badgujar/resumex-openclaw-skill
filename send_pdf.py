#!/usr/bin/env python3
"""
Resumex → Telegram PDF Sender
Part of the Resumex OpenClaw Skill.

This script fetches resume data via the Resumex API and sends a
formatted resume summary + PDF download link to a Telegram chat.

Usage:
    python3 send_pdf.py \
        --api-key rx_your_key \
        --chat-id 123456789 \
        [--bot-token YOUR_TELEGRAM_BOT_TOKEN]

The RESUMEX_API_KEY env var is used as fallback if --api-key is not set.
The TELEGRAM_BOT_TOKEN env var is used as fallback if --bot-token is not set.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
import tempfile

RESUMEX_API = "https://resumex.dev/api/v1/agent"
TELEGRAM_API = "https://api.telegram.org/bot{token}"


def fetch_resume(api_key: str) -> dict:
    """Fetch the active resume workspace via the Resumex API."""
    req = urllib.request.Request(
        RESUMEX_API,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode())
            if not payload.get("success"):
                raise RuntimeError(f"API error: {payload.get('error', 'Unknown')}")
            return payload["data"]
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise RuntimeError(f"HTTP {e.code}: {body}")


def get_active_resume(workspace: dict) -> dict:
    """Extract the active resume data from the workspace."""
    active_id = workspace.get("activeResumeId")
    for resume in workspace.get("resumes", []):
        if resume.get("id") == active_id:
            return resume.get("data", {})
    # fallback to first resume
    resumes = workspace.get("resumes", [])
    if resumes:
        return resumes[0].get("data", {})
    raise RuntimeError("No resume data found in workspace.")


def format_resume_message(data: dict) -> str:
    """Format a human-readable summary of the resume for Telegram."""
    profile = data.get("profile", {})
    name = profile.get("fullName", "User") or "User"
    title_line = f"📄 *{name}'s Resume*"

    lines = [title_line, ""]

    # Profile
    if profile.get("email"):
        lines.append(f"📧 {profile['email']}")
    if profile.get("phone"):
        lines.append(f"📱 {profile['phone']}")
    if profile.get("location"):
        lines.append(f"📍 {profile['location']}")
    if profile.get("linkedin"):
        lines.append(f"🔗 {profile['linkedin']}")
    if profile.get("github"):
        lines.append(f"🐙 {profile['github']}")

    # Summary
    if profile.get("summary"):
        lines.append("")
        lines.append("*Summary*")
        lines.append(profile["summary"][:300] + ("..." if len(profile.get("summary", "")) > 300 else ""))

    # Experience
    exp = data.get("experience", [])
    if exp:
        lines.append("")
        lines.append(f"*Experience* ({len(exp)} role{'s' if len(exp) != 1 else ''})")
        for e in exp[:3]:  # Show top 3
            lines.append(f"  • {e.get('role', '')} @ {e.get('company', '')} ({e.get('startDate', '')} – {e.get('endDate', '')})")
        if len(exp) > 3:
            lines.append(f"  _...and {len(exp) - 3} more_")

    # Education
    edu = data.get("education", [])
    if edu:
        lines.append("")
        lines.append("*Education*")
        for e in edu[:2]:
            lines.append(f"  • {e.get('degree', '')} — {e.get('institution', '')} ({e.get('endDate', '')})")

    # Skills
    skills = data.get("skills", [])
    if skills:
        lines.append("")
        lines.append("*Skills*")
        for sg in skills[:4]:
            skill_list = ", ".join(sg.get("skills", [])[:6])
            lines.append(f"  *{sg.get('category', '')}:* {skill_list}")

    # Portfolio link
    subdomain = data.get("subdomain")
    lines.append("")
    if subdomain:
        lines.append(f"🌐 Portfolio: https://{subdomain}.resumex.dev")
    lines.append("📥 Edit at: https://resumex.dev/app")
    lines.append("")
    lines.append("_To download PDF: Open the portfolio link and press Ctrl+P → Save as PDF_")

    return "\n".join(lines)


def send_telegram_message(bot_token: str, chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
    """Send a text message to a Telegram chat."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = json.dumps({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False,
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read().decode())
            return result.get("ok", False)
    except urllib.error.HTTPError as e:
        print(f"[Error] Telegram sendMessage failed: {e.read().decode()}", file=sys.stderr)
        return False


def send_telegram_document_url(bot_token: str, chat_id: str, document_url: str, caption: str) -> bool:
    """Send a document to Telegram by URL (Telegram downloads it server-side)."""
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    data = json.dumps({
        "chat_id": chat_id,
        "document": document_url,
        "caption": caption,
        "parse_mode": "Markdown",
    }).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result.get("ok", False)
    except urllib.error.HTTPError as e:
        print(f"[Warn] sendDocument by URL failed: {e.read().decode()}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Send Resumex resume to Telegram")
    parser.add_argument("--api-key", default=os.environ.get("RESUMEX_API_KEY"), help="Resumex API Key")
    parser.add_argument("--chat-id", required=True, help="Telegram Chat ID to send the resume to")
    parser.add_argument("--bot-token", default=os.environ.get("TELEGRAM_BOT_TOKEN"), help="Telegram Bot Token")
    parser.add_argument("--name", default="", help="User's name for the filename")
    args = parser.parse_args()

    api_key = args.api_key
    chat_id = args.chat_id
    bot_token = args.bot_token

    if not api_key:
        print("❌ No RESUMEX_API_KEY provided. Set it as an env var or pass --api-key.", file=sys.stderr)
        sys.exit(1)

    # Step 1: Fetch resume
    print("[Resumex] Fetching resume data...", file=sys.stderr)
    try:
        workspace = fetch_resume(api_key)
        resume_data = get_active_resume(workspace)
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        sys.exit(1)

    # Step 2: Format and send text summary
    message = format_resume_message(resume_data)
    print("[Resumex] Resume data fetched.", file=sys.stderr)
    print(message)  # Always print for the agent to read

    # Step 3: If bot token available, send via Telegram
    if bot_token:
        print(f"[Telegram] Sending summary to chat {chat_id}...", file=sys.stderr)
        ok = send_telegram_message(bot_token, chat_id, message)
        if ok:
            print("[Telegram] ✅ Summary sent!", file=sys.stderr)
        else:
            print("[Telegram] ⚠️  Message send failed — check bot token and chat ID.", file=sys.stderr)

        # Step 4: Try sending PDF as a document
        subdomain = resume_data.get("subdomain")
        pdf_sent = False

        if subdomain:
            # If user has a published portfolio, use the print URL as a "document"
            portfolio_url = f"https://{subdomain}.resumex.dev"
            caption = (
                f"📄 *{resume_data.get('profile', {}).get('fullName', 'Resume')}*\n"
                f"Your resume portfolio: {portfolio_url}\n"
                f"_Open and press Ctrl+P → Save as PDF to download_"
            )
            pdf_sent = send_telegram_document_url(bot_token, chat_id, portfolio_url, caption)

        if not pdf_sent:
            # Send the api-docs link as a fallback message
            fallback = (
                "📎 *Get Your Resume PDF:*\n"
                "1. Open https://resumex.dev/app\n"
                "2. Click the *Download* button in the top bar\n"
                "   OR press Ctrl+P → Save as PDF\n\n"
                "_Your resume is always up to date!_"
            )
            send_telegram_message(bot_token, chat_id, fallback)
            print("[Telegram] Sent PDF download instructions.", file=sys.stderr)
    else:
        print("[Info] No TELEGRAM_BOT_TOKEN set — printed resume to stdout for the agent.", file=sys.stderr)


if __name__ == "__main__":
    main()
