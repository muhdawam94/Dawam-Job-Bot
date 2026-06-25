# core/notifier.py
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def _send(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[Telegram] Not configured, skipping: {text[:80]}")
        return
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       text,
            "parse_mode": "HTML"
        }, timeout=10)
    except Exception as e:
        print(f"[Telegram] Error: {e}")

def notify_new_jobs(jobs: list[dict]):
    if not jobs:
        return
    lines = [f"🔍 <b>Job Bot — {len(jobs)} new job(s) found</b>\n"]
    for j in jobs[:10]:   # max 10 per notif
        email_icon = "📧" if j.get("email") else "🔗"
        lines.append(
            f"{email_icon} <b>{j['title']}</b>\n"
            f"   🏢 {j.get('company','?')} | 📊 Score: {j.get('score',0)}\n"
            f"   🌐 <a href=\"{j['url']}\">View Job</a> [{j['source']}]\n"
        )
    if len(jobs) > 10:
        lines.append(f"...and {len(jobs)-10} more.")
    _send("\n".join(lines))

def notify_applied(job: dict):
    _send(
        f"✅ <b>Application Sent!</b>\n"
        f"📌 {job['title']} @ {job.get('company','?')}\n"
        f"📧 {job.get('email','')}\n"
        f"🌐 <a href=\"{job['url']}\">Job Link</a>"
    )

def notify_summary(stats: dict, new_count: int, applied_count: int):
    _send(
        f"📊 <b>Job Bot Daily Summary</b>\n"
        f"🆕 New jobs found  : {new_count}\n"
        f"📨 Applied today   : {applied_count}\n"
        f"📁 Total in DB     : {stats.get('total',0)}\n"
        f"✅ Total applied   : {stats.get('applied',0)}"
    )

def notify_error(msg: str):
    _send(f"⚠️ <b>Job Bot Error</b>\n{msg}")
