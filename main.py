#!/usr/bin/env python3
# main.py — Job Application Bot
# Run: python main.py
#      python main.py --dry-run   (tidak kirim email, hanya notif Telegram)
#      python main.py --dashboard (tampilkan status di terminal)

import sys, argparse
from scrapers      import ALL_SCRAPERS
from core.filter   import filter_jobs
from core.tracker  import init_db, is_seen, save_job, mark_applied, get_stats
from core.cover_letter import generate as gen_cover
from core.emailer  import send_application
from core.notifier import notify_new_jobs, notify_applied, notify_summary, notify_error
from config        import MAX_JOBS_PER_SOURCE, MAX_EMAILS_PER_RUN, SEND_EMAILS

def run(dry_run=False):
    print("=" * 60)
    print("  JOB BOT — Starting run")
    print("=" * 60)

    init_db()

    # ── 1. Scrape semua sumber ──────────────────────────────
    all_raw = []
    for name, scraper_fn in ALL_SCRAPERS:
        print(f"\n[Scraper] {name}...")
        try:
            jobs = scraper_fn()[:MAX_JOBS_PER_SOURCE]
            print(f"  → {len(jobs)} jobs fetched")
            all_raw.extend(jobs)
        except Exception as e:
            print(f"  ✗ Error: {e}")
            notify_error(f"{name} scraper failed: {e}")

    print(f"\n[Filter] Total raw jobs: {len(all_raw)}")

    # ── 2. Filter & score ───────────────────────────────────
    filtered = filter_jobs(all_raw)
    print(f"[Filter] After scoring: {len(filtered)} relevant jobs")

    # ── 3. Deduplicate dengan DB ────────────────────────────
    new_jobs = [j for j in filtered if not is_seen(j["id"])]
    print(f"[DB] New (unseen) jobs: {len(new_jobs)}")

    if not new_jobs:
        print("[Bot] No new jobs this run.")
        notify_summary(get_stats(), 0, 0)
        return

    # ── 4. Notifikasi Telegram — semua job baru ─────────────
    notify_new_jobs(new_jobs)

    # ── 5. Apply (hanya job yang punya email) ───────────────
    applied_count = 0
    email_jobs    = [j for j in new_jobs if j.get("email")]
    no_email_jobs = [j for j in new_jobs if not j.get("email")]

    print(f"\n[Apply] Jobs with email: {len(email_jobs)}")
    print(f"[Apply] Jobs without email (link only): {len(no_email_jobs)}")

    for job in email_jobs:
        if applied_count >= MAX_EMAILS_PER_RUN:
            print(f"[Apply] Max emails/run reached ({MAX_EMAILS_PER_RUN}), stopping.")
            break

        print(f"\n[Apply] Generating cover letter: {job['title']}")
        cover = gen_cover(job)

        save_job(job, status="pending", cover_letter=cover)

        if dry_run or not SEND_EMAILS:
            print(f"[DryRun] Would apply to: {job['title']} <{job['email']}>")
            save_job(job, status="dry_run")
            continue

        ok = send_application(job, cover)
        if ok:
            mark_applied(job["id"])
            notify_applied(job)
            applied_count += 1

    # Save no-email jobs sebagai "link_only"
    for job in no_email_jobs:
        save_job(job, status="link_only")

    # ── 6. Summary ──────────────────────────────────────────
    stats = get_stats()
    notify_summary(stats, len(new_jobs), applied_count)
    print(f"\n{'='*60}")
    print(f"  DONE | New: {len(new_jobs)} | Applied: {applied_count}")
    print(f"  DB Total: {stats['total']} | Total Applied: {stats['applied']}")
    print(f"{'='*60}\n")

def dashboard():
    from core.tracker import get_all_jobs
    jobs = get_all_jobs(50)
    stats = get_stats()
    print(f"\n{'='*60}")
    print(f"  JOB BOT DASHBOARD")
    print(f"  Total: {stats['total']} | Applied: {stats['applied']} | Today: {stats['today']}")
    print(f"{'='*60}")
    print(f"{'#':<4} {'Score':<6} {'Status':<12} {'Title':<40} {'Source':<15}")
    print("-"*80)
    for i, j in enumerate(jobs, 1):
        title = j["title"][:38] + ".." if len(j["title"]) > 40 else j["title"]
        print(f"{i:<4} {j['score']:<6} {j['status']:<12} {title:<40} {j['source']:<15}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automated Remote Job Application Bot")
    parser.add_argument("--dry-run",   action="store_true", help="Run without sending emails")
    parser.add_argument("--dashboard", action="store_true", help="Show job tracking dashboard")
    args = parser.parse_args()

    if args.dashboard:
        dashboard()
    else:
        run(dry_run=args.dry_run)
