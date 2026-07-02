# core/notifier.py — v3 FIXED
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def _send(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[Telegram] Not configured")
        return
    try:
        requests.post(f"{API}/sendMessage", json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       text[:4096],  # Telegram max 4096 chars
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }, timeout=15)
    except Exception as e:
        print(f"[Telegram] Error: {e}")

def notify_new_job_with_cover(job: dict, cover_letter: str):
    """Kirim 1 pesan per job lengkap dengan cover letter."""
    score = job.get('score', 0)
    stars = "⭐" * min(score // 20, 5)
    is_direct = job.get("source", "").startswith("Career_")

    msg = (
        f"{'🏢 DIRECT COMPANY' if is_direct else '🔔 JOB BARU'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>{job.get('title','')}</b>\n"
        f"🏢 {job.get('company','?')}\n"
        f"📍 {job.get('location','Remote')}\n"
        f"📊 Match: {stars} ({score}/100)\n"
        f"🔗 <a href=\"{job.get('url','')}\">BUKA & APPLY ↗</a>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"📝 <b>COVER LETTER SIAP PAKAI:</b>\n\n"
        f"{cover_letter[:1500]}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"💡 Copy teks di atas → paste di form → Submit!"
    )
    _send(msg)

def notify_new_jobs_summary(jobs: list[dict]):
    if not jobs:
        return
    lines = [f"🔍 <b>{len(jobs)} Lowongan Baru Ditemukan!</b>\n"]
    for j in jobs[:10]:
        icon = "🏢" if j.get("source","").startswith("Career_") else "🔗"
        lines.append(f"{icon} <b>{j.get('title','')}</b> — {j.get('company','?')}")
        lines.append(f"   Score: {j.get('score',0)} | {j.get('source','')}")
        lines.append(f"   <a href=\"{j.get('url','')}\">Apply ↗</a>\n")
    if len(jobs) > 10:
        lines.append(f"...dan {len(jobs)-10} lainnya")
    _send("\n".join(lines))

def notify_applied(job: dict):
    _send(
        f"✅ <b>Lamaran Terkirim!</b>\n"
        f"📌 {job.get('title','')} @ {job.get('company','?')}\n"
        f"🔗 <a href=\"{job.get('url','')}\">Job Link</a>"
    )

def notify_auto_apply_result(job: dict, success: bool, platform: str, error: str = ""):
    """Notify user about auto-apply attempt result"""
    title = job.get('title', '')
    company = job.get('company', '?')
    url = job.get('url', '')

    if success:
        _send(
            f"🤖✅ <b>AUTO-APPLY BERHASIL!</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💼 {title}\n"
            f"🏢 {company}\n"
            f"🔧 Platform: {platform.upper()}\n"
            f"🔗 <a href=\"{url}\">Cek Status ↗</a>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"✨ Form otomatis terisi & submitted!"
        )
    else:
        _send(
            f"🤖⚠️ <b>AUTO-APPLY PERLU CEK MANUAL</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💼 {title}\n"
            f"🏢 {company}\n"
            f"🔧 Platform: {platform}\n"
            f"❌ Error: {error[:200] if error else 'Form tidak dikenali'}\n"
            f"🔗 <a href=\"{url}\">Apply Manual ↗</a>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"💡 Buka link dan apply manual ya!"
        )

def notify_summary(stats: dict, new_count: int, applied_count: int):
    _send(
        f"📊 <b>Job Bot Summary</b>\n"
        f"🆕 Job baru    : {new_count}\n"
        f"📨 Auto-apply  : {applied_count}\n"
        f"📁 Total DB    : {stats.get('total',0)}\n"
        f"✅ Total apply : {stats.get('applied',0)}"
    )

def notify_error(msg: str):
    _send(f"⚠️ <b>Error</b>\n{msg}")
