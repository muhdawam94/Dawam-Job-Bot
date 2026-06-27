# core/notifier.py — versi upgrade dengan tombol Apply
import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

def _send(text: str, reply_markup=None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print(f"[Telegram] Not configured: {text[:80]}")
        return
    payload = {
        "chat_id":    TELEGRAM_CHAT_ID,
        "text":       text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(f"{API}/sendMessage", json=payload, timeout=10)
    except Exception as e:
        print(f"[Telegram] Error: {e}")

def notify_new_job_with_cover(job: dict, cover_letter: str):
    """
    Kirim notif job baru lengkap dengan cover letter siap pakai.
    1 pesan per job — mudah dibaca di HP.
    """
    score_bar = "🟢" * min(job.get("score", 0) // 20, 5)
    source_flag = {
        "FreelancerMap🇩🇪": "🇩🇪", "Malt🇩🇪": "🇩🇪",
        "Arc.dev": "🌐", "Contra": "🌐", "Gun.io": "🌐",
    }.get(job.get("source",""), "🌍")

    # Cek apakah dari career page perusahaan langsung
    is_direct = job.get("source","").startswith("Career_")

    header = (
        f"{'🏢 DIRECT COMPANY' if is_direct else '🔔 NEW JOB'} {source_flag}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💼 <b>{job['title']}</b>\n"
        f"🏢 {job.get('company','?')}\n"
        f"📍 {job.get('location','Remote')}\n"
        f"📊 Match Score: {score_bar} ({job.get('score',0)}/100)\n"
        f"🔗 <a href=\"{job['url']}\">Buka Lowongan ↗</a>\n"
    )

    cover_section = (
        f"\n📝 <b>COVER LETTER (siap pakai):</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{cover_letter[:800]}"
        f"{'...' if len(cover_letter) > 800 else ''}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"💡 Copy cover letter di atas → apply di link job"
    )

    _send(header + cover_section)

def notify_new_jobs_summary(jobs: list[dict]):
    """Summary singkat semua job baru — tanpa cover letter."""
    if not jobs:
        return
    lines = [f"🔍 <b>{len(jobs)} New Jobs Found!</b>\n"]
    for j in jobs[:15]:
        icon = "🏢" if j.get("source","").startswith("Career_") else "🔗"
        lines.append(
            f"{icon} <b>{j['title']}</b>\n"
            f"   {j.get('company','?')} | Score: {j.get('score',0)} | {j.get('source','')}\n"
            f"   <a href=\"{j['url']}\">Apply ↗</a>\n"
        )
    if len(jobs) > 15:
        lines.append(f"...dan {len(jobs)-15} lainnya")
    _send("\n".join(lines))

def notify_applied(job: dict):
    _send(
        f"✅ <b>Lamaran Terkirim!</b>\n"
        f"📌 {job['title']} @ {job.get('company','?')}\n"
        f"📧 {job.get('email','')}\n"
        f"🔗 <a href=\"{job['url']}\">Job Link</a>"
    )

def notify_summary(stats: dict, new_count: int, applied_count: int):
    _send(
        f"📊 <b>Job Bot Summary</b>\n"
        f"🆕 Job baru ditemukan : {new_count}\n"
        f"📨 Auto apply (email) : {applied_count}\n"
        f"📁 Total di database  : {stats.get('total',0)}\n"
        f"✅ Total terlamar     : {stats.get('applied',0)}\n\n"
        f"💡 Job link-only: tap 'Apply ↗' di notif sebelumnya"
    )

def notify_error(msg: str):
    _send(f"⚠️ <b>Job Bot Error</b>\n{msg}")
