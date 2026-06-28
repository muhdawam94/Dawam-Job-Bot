#!/usr/bin/env python3
# main.py — Job Bot v4
# Tambahan: Web3 jobs langsung dari Greenhouse/Lever API + Web3 job boards

import sys, argparse
from scrapers      import ALL_SCRAPERS
from scrapers.newboards       import scrape_arc, scrape_freelancermap, scrape_malt, scrape_contra, scrape_gunio
from scrapers.company_careers import scrape_company_careers, COMPANY_CAREER_PAGES
from scrapers.web3_jobs       import scrape_all_web3
from core.filter   import filter_jobs
from core.tracker  import init_db, is_seen, save_job, mark_applied, get_stats, get_all_jobs
from core.cover_letter import generate as gen_cover
from core.emailer  import send_application
from core.notifier import (notify_new_job_with_cover, notify_new_jobs_summary,
                            notify_applied, notify_summary, notify_error)
from config        import MAX_JOBS_PER_SOURCE, MAX_EMAILS_PER_RUN, SEND_EMAILS

EXTRA_SCRAPERS = [
    ("Arc.dev",          scrape_arc),
    ("FreelancerMap🇩🇪", scrape_freelancermap),
    ("Malt🇩🇪",          scrape_malt),
    ("Contra",           scrape_contra),
    ("Gun.io",           scrape_gunio),
]

def run(dry_run=False):
    print("=" * 65)
    print("  JOB BOT v4 — Web3 Edition")
    print("=" * 65)

    init_db()
    all_raw = []

    # 1. Job boards umum
    for name, fn in (ALL_SCRAPERS + EXTRA_SCRAPERS):
        print(f"\n[Scraper] {name}...")
        try:
            jobs = fn()[:MAX_JOBS_PER_SOURCE]
            print(f"  → {len(jobs)} jobs")
            all_raw.extend(jobs)
        except Exception as e:
            print(f"  ✗ {e}")

    # 2. Web3 khusus (Greenhouse + Lever + Web3 boards)
    print(f"\n[Scraper] 🌐 WEB3 SOURCES...")
    try:
        web3_jobs = scrape_all_web3()
        print(f"  → {len(web3_jobs)} Web3 jobs total")
        all_raw.extend(web3_jobs)
    except Exception as e:
        print(f"  ✗ Web3 scraper error: {e}")

    # 3. Company career pages
    print(f"\n[Scraper] Company Career Pages ({len(COMPANY_CAREER_PAGES)} perusahaan)...")
    try:
        career_jobs = scrape_company_careers()
        print(f"  → {len(career_jobs)} jobs")
        all_raw.extend(career_jobs)
    except Exception as e:
        print(f"  ✗ {e}")

    # Filter & deduplicate
    print(f"\n[Filter] Total raw: {len(all_raw)}")
    filtered = filter_jobs(all_raw)
    new_jobs = [j for j in filtered if not is_seen(j["id"])]
    print(f"[Filter] Relevant: {len(filtered)} | NEW: {len(new_jobs)}")

    if not new_jobs:
        print("[Bot] Tidak ada job baru.")
        notify_summary(get_stats(), 0, 0)
        return

    # Summary ke Telegram
    notify_new_jobs_summary(new_jobs)

    # Per job: cover letter + notif Telegram
    applied_count = 0
    print(f"\n[Cover+Notify] {len(new_jobs)} jobs...")

    for i, job in enumerate(new_jobs, 1):
        source = job.get('source', '')
        print(f"  [{i}/{len(new_jobs)}] {job['title'][:45]} [{source}]")

        cover = gen_cover(job)
        notify_new_job_with_cover(job, cover)
        save_job(job, status="notified", cover_letter=cover)

        if job.get("email") and not dry_run and SEND_EMAILS:
            if applied_count < MAX_EMAILS_PER_RUN:
                ok = send_application(job, cover)
                if ok:
                    mark_applied(job["id"])
                    notify_applied(job)
                    applied_count += 1

    stats = get_stats()
    notify_summary(stats, len(new_jobs), applied_count)
    print(f"\n✅ SELESAI | New: {len(new_jobs)} | Applied: {applied_count}")
    print(f"   DB Total: {stats['total']} | Total Applied: {stats['applied']}")

def dashboard():
    jobs  = get_all_jobs(50)
    stats = get_stats()
    print(f"\n{'='*65}")
    print(f"  DASHBOARD | Total: {stats['total']} | Applied: {stats['applied']}")
    print(f"{'='*65}")
    for i, j in enumerate(jobs, 1):
        t = j["title"][:33] + ".." if len(j["title"]) > 35 else j["title"]
        print(f"{i:<3} {j['score']:<5} {j['status']:<11} {t:<35} {j['source']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",   action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()
    if args.dashboard:
        dashboard()
    else:
        run(dry_run=args.dry_run)
