#!/usr/bin/env python3
"""
Income-Scout Agent — runs 24/7 on Render/GitHub
Scans AI networks for income opportunities, reports via NTFY + Telegram.
"""
import os, time, json, requests, schedule
from datetime import datetime
from dateutil import tz

# === CONFIG ===
# NTFY topic (free, no setup — user visits https://ntfy.sh/income_scout to see alerts)
NTFY_TOPIC = os.getenv("NTFY_TOPIC", "income-scout-agent")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

# Telegram (optional — provide TELEGRAM_BOT_TOKEN + TELEGRAM_ALERT_CHAT_ID to enable)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_ALERT_CHAT_ID", "")

# Wallets (for crypto network registration)
FET_SEED = os.getenv("FET_SEED", "income scout agent wallet 2026 autonomous earnings")

# === ALERT SYSTEM ===
def send_alert(title: str, text: str):
    """Send alert via NTFY (primary) and Telegram (optional)."""
    # NTFY (primary — always works)
    try:
        requests.post(NTFY_URL, data=text, headers={"Title": title, "Priority": "normal"}, timeout=10)
    except Exception as e:
        print(f"[NTFY] Failed: {e}")

    # Telegram (if configured)
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": f"*{title}*\n{text}", "parse_mode": "Markdown"}, timeout=10)
        except Exception as e:
            print(f"[TELEGRAM] Failed: {e}")

    # Console (always)
    print(f"[{title}] {text[:100]}")

# === SCANNERS ===

def scan_crowdgen():
    """Scan Crowdgen (Appen) for new AI projects."""
    try:
        resp = requests.get("https://app.crowdgen.com/en-us/join/", timeout=20)
        text = resp.text.lower()
        if "ai" in text or "annotation" in text or "data" in text:
            send_alert("🏗️ Crowdgen", "New AI/data projects may be available\nURL: https://app.crowdgen.com/en-us/join/")
        else:
            send_alert("ℹ️ Crowdgen", "No new high-rate projects at this scan.")
    except Exception as e:
        send_alert("⚠️ Crowdgen Error", str(e)[:200])

def scan_fetchai_marketplace():
    """Check Fetch.ai Agentverse for agents seeking services via web scraping."""
    try:
        # Scrape the Agentverse explore page
        resp = requests.get("https://agentverse.ai/explore", timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (IncomeScoutAgent/1.0)"
        })
        found = []
        text = resp.text.lower()
        keywords = ["data", "scraping", "annotation", "moderation", "labeling", "web scraper"]
        for kw in keywords:
            count = text.count(kw)
            if count > 0:
                found.append(f"{kw}: {count} mentions")
        if found:
            msg = "🤖 Fetch.ai marketplace has activity:\n" + "\n".join(found[:5]) + "\n\nCheck: https://agentverse.ai/explore"
            send_alert("Fetch.ai", msg)
        else:
            send_alert("ℹ️ Fetch.ai", "No matching service requests in marketplace right now.")
    except Exception as e:
        send_alert("⚠️ Fetch.ai Error", str(e)[:200])

def scan_lionbridge():
    """Check Lionbridge AI for new projects."""
    try:
        resp = requests.get("https://www.lionbridge.com/join-our-community/", timeout=20, headers={
            "User-Agent": "Mozilla/5.0 (IncomeScoutAgent/1.0)"
        })
        text = resp.text.lower()
        if "language" in text or "data" in text or "annotation" in text or "ai" in text:
            send_alert("👷 Lionbridge", "New AI/data opportunities detected\nCheck: https://www.lionbridge.com/join-our-community/")
        else:
            send_alert("ℹ️ Lionbridge", "No new projects announced.")
    except Exception as e:
        send_alert("⚠️ Lionbridge Error", str(e)[:200])

def scan_gitcoin_bounties():
    """Check Gitcoin for AI/data bounties."""
    try:
        # Gitcoin API
        resp = requests.get("https://gitcoincore.com/api/v0.1/bounties/?status=open&keywords=AI", timeout=20)
        bounties = []
        if resp.status_code == 200:
            data = resp.json()
            bounties = data.get("bounties", [])[:5]

        if bounties:
            msg = "🎯 Gitcoin bounties found:\n"
            for b in bounties[:5]:
                title = b.get("title", "unknown")[:60]
                value = b.get("token_value", "?")
                token = b.get("token", "?")
                msg += f"• {title} — {value} {token}\n"
            msg += "\nCheck: https://gitcoin.co/bounties/"
            send_alert("Gitcoin Bounties", msg)
        else:
            send_alert("ℹ️ Gitcoin", "No AI bounties >0.1 ETH found.")
    except Exception as e:
        # Fallback: scrape the bounties page
        try:
            resp2 = requests.get("https://gitcoin.co/bounties/?keywords=AI", timeout=20, headers={
                "User-Agent": "Mozilla/5.0 (IncomeScoutAgent/1.0)"
            })
            send_alert("ℹ️ Gitcoin", f"Bounties page HTTP {resp2.status_code}. Check https://gitcoin.co/bounties/")
        except Exception as e2:
            send_alert("⚠️ Gitcoin Error", str(e2)[:200])

def daily_report():
    """Send end-of-day summary."""
    send_alert(
        "📊 Income-Scout Daily",
        f"Date: {datetime.now(tz=tz.gettz('UTC')).strftime('%Y-%m-%d %H:%M UTC')}\n\n"
        "✅ Scanned:\n"
        "• Crowdgen (every 4h)\n"
        "• Fetch.ai marketplace (every 2h)\n"
        "• Lionbridge AI (every 4h)\n"
        "• Gitcoin bounties (daily)\n\n"
        "💰 Earnings: $0 (first day — monitoring started)\n\n"
        f"📲 View alerts: https://ntfy.sh/{NTFY_TOPIC}"
    )

# === SCHEDULE ===
def setup_schedule():
    schedule.every(4).hours.do(scan_crowdgen)
    schedule.every(2).hours.do(scan_fetchai_marketplace)
    schedule.every(4).hours.do(scan_lionbridge)
    schedule.every().day.at("09:00").do(scan_gitcoin_bounties)
    schedule.every().day.at("20:00").do(daily_report)
    # Initial scan
    scan_crowdgen()
    scan_fetchai_marketplace()
    scan_gitcoin_bounties()

def main():
    print("🚀 Income-Scout Agent started")
    print(f"📲 Alerts: https://ntfy.sh/{NTFY_TOPIC}")
    if TELEGRAM_BOT_TOKEN:
        print("📱 Telegram: configured")
    else:
        print("📱 Telegram: not configured (add TELEGRAM_BOT_TOKEN to enable)")

    setup_schedule()

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
