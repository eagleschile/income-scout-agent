#!/usr/bin/env python3
"""
Income-Scout Agent — runs 24/7 on Render/GitHub
Scans AI networks for income opportunities, reports via Telegram.
"""
import os
import time
import json
import requests
import schedule
from datetime import datetime
from dateutil import tz

# === CONFIG ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "")
RUNNING = True

# === TELEGRAM ALERTS ===
def telegram_alert(text: str):
    """Send alert to Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[ALERT] {text}")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[ERROR] Telegram: {e}")

# === PLATFORM SCANNERS ===

def scan_crowdgen():
    """Scan Crowdgen (Appen) for new AI projects."""
    try:
        resp = requests.get("https://app.crowdgen.com/en-us/projects/", timeout=15)
        # Parse for project cards — look for "Apply" links and rate info
        projects = []
        # The site is JS-rendered; using the public projects API if available
        # Fallback: check known project listing structure
        for line in resp.text.split('\n'):
            if 'rate' in line.lower() or 'hourly' in line.lower() or 'apply' in line.lower():
                projects.append(line.strip()[:200])

        if projects:
            msg = "🏗️ *Crowdgen — new AI projects found:*\n"
            for p in projects[:5]:
                msg += f"• {p[:150]}\n"
            telegram_alert(msg)
        else:
            telegram_alert("ℹ️ Crowdgen scan: no new high-rate projects found.")
    except Exception as e:
        telegram_alert(f"⚠️ Crowdgen scan error: {e}")

def scan_fetchai_marketplace():
    """Check Fetch.ai Agentverse for agents seeking services."""
    try:
        # Agentverse has a public API endpoint
        resp = requests.get(
            "https://api.agentverse.ai/agents",
            timeout=15
        )
        if resp.status_code == 200:
            data = resp.json()
            agents = data.get("agents", [])
            msg = "🤖 *Fetch.ai Agentverse — agents seeking services:*\n"
            count = 0
            for agent in agents[:10]:
                if any(kw in str(agent).lower() for kw in ["data", "scraping", "labeling", "moderation", "annotation"]):
                    msg += f"• {agent.get('name', 'unknown')} — {agent.get('description', 'no desc')[:80]}\n"
                    count += 1
            if count == 0:
                msg = "ℹ️ Fetch.ai scan: no matching agent requests found."
            telegram_alert(msg)
        else:
            telegram_alert(f"ℹ️ Fetch.ai API returned {resp.status_code}")
    except Exception as e:
        telegram_alert(f"⚠️ Fetch.ai scan error: {e}")

def scan_lionbridge():
    """Check Lionbridge AI for new projects."""
    try:
        resp = requests.get("https://www.lionbridge.com/join-our-community/", timeout=15)
        msg = "👷 *Lionbridge AI — new opportunities:*\n"
        if resp.status_code == 200:
            # Look for project listings or sign-up prompts
            text = resp.text.lower()
            if 'language' in text or 'data' in text or 'annotation' in text:
                msg += "New projects may be available. Check platform for details.\n"
            else:
                msg = "ℹ️ Lionbridge scan: no new projects announced."
        telegram_alert(msg)
    except Exception as e:
        telegram_alert(f"⚠️ Lionbridge scan error: {e}")

def scan_gitcoin_bounties():
    """Check Gitcoin for AI/data bounties."""
    try:
        resp = requests.get(
            "https://gitcoincore.com/api/v0.1/bounties/?status=open&keywords=AI",
            timeout=15
        )
        bounties = []
        if resp.status_code == 200:
            data = resp.json()
            bounties = data.get("bounties", [])[:5]

        if bounties:
            msg = "🎯 *Gitcoin — AI bounties found:*\n"
            for b in bounties:
                msg += f"• {b.get('title', 'unknown')} — {b.get('token_value', '?')} {b.get('token', '?')}\n"
            telegram_alert(msg)
        else:
            telegram_alert("ℹ️ Gitcoin scan: no AI bounties >0.1 ETH found.")
    except Exception as e:
        telegram_alert(f"⚠️ Gitcoin scan error: {e}")

# === DAILY REPORT ===
def daily_report():
    """Send daily earnings summary."""
    telegram_alert(
        "📊 *Income-Scout Daily Report*\n"
        f"Date: {datetime.now(tz=tz.gettz('UTC')).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        "✅ Scanned platforms:\n"
        "• Crowdgen: scanning...\n"
        "• Fetch.ai: scanning...\n"
        "• Gitcoin: scanning...\n"
        "• Lionbridge: scanning...\n\n"
        "💰 Earnings: $0 (first day — monitoring started)"
    )

# === SCHEDULE ===
def setup_schedule():
    """Configure cron-like schedule (mirrors Hermes cron)."""
    schedule.every(4).hours.do(scan_crowdgen)
    schedule.every(2).hours.do(scan_fetchai_marketplace)
    schedule.every(4).hours.do(scan_lionbridge)
    schedule.every().day.at("09:00").do(scan_gitcoin_bounties)
    schedule.every().day.at("20:00").do(daily_report)

    # Run an initial scan
    scan_crowdgen()
    scan_fetchai_marketplace()
    scan_gitcoin_bounties()

def main():
    """Main agent loop."""
    print("🚀 Income-Scout Agent started")
    telegram_alert("🤖 Income-Scout Agent deployed on Render! Scanning for AI opportunities...")

    setup_schedule()

    # Keep running
    while RUNNING:
        schedule.run_pending()
        time.sleep(60)  # check every minute

if __name__ == "__main__":
    main()
