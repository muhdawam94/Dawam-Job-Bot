#!/usr/bin/env python3
# main.py — Job Application Bot v2
# Tambahan: Arc.dev, FreelancerMap, Malt, Contra, Gun.io, Company Career Pages
# Cover letter dikirim per job ke Telegram — tinggal copy-paste!

import sys, argparse
from scrapers      import ALL_SCRAPERS
from scrapers.newboards       import scrape_arc, scrape_freelancermap, scrape_malt, scrape_contra, scrape_gunio
from scrapers.company_careers import scrape_company_careers, COMPANY_CAREER_PAGES
from core.filter   import filter_jobs
from core.tracker  import init_db, is_seen, save_job, mark_applied, get_stats
from core.cover_letter import generate as gen_cover
from core.emailer  import send_application
from core.notifier import (notify_new_job_with_cover, notify_new_jobs_summary,
                            notify_applied, notify_summary, notify_error)
from config        import MAX_JOBS_PER_SOURCE, MAX_EMAILS_PER_RUN, SEND_EMAILS

# ── Semua scraper digabung ───────────────────────────────────
EXTRA_SCRAPERS = [
    ("Arc.dev",           scrape_arc),
    ("FreelancerMap🇩🇪",  scrape_freelancermap),
    ("Malt🇩🇪",           scrape_malt),
    ("Contra",            scrape_contra),
    ("Gun.io",            scrape_gunio),
]

def run(dry_run=False):
    print("=" * 65)
    print("  JOB BOT v2 — Starting run")
    print(f"  Sources: {len(ALL_SCRAPERS) + len(EXTRA_SCRAPERS)} job boards + {len(COMPANY_CAREER_PAGES)} company pages")
    print("=" * 65)

    init_db()
    all_raw = []

    # ── 1. Scrape job boards lama ────────────────────────────
    for name, fn in ALL_SCRAPERS:
        print(f"\n[Scraper] {name}...")
        try:
            jobs = fn()[:MAX_JOBS_PER_SOURCE]
            print(f"  → {len(jobs)} jobs")
            all_raw.extend(jobs)
        except Exception as e:
            print(f"  ✗ {e}")
            notify_error(f"{name}: {e}")

    # ── 2. Scrape job boards baru ────────────────────────────
    for name, fn in EXTRA_SCRAPERS:
        print(f"\n[Scraper] {name}...")
        try:
            jobs = fn()[:MAX_JOBS_PER_SOURCE]
            print(f"  → {len(jobs)} jobs")
            all_raw.extend(jobs)
        except Exception as e:
            print(f"  ✗ {e}")

    # ── 3. Scrape company career pages ───────────────────────
    print(f"\n[Scraper] Company Career Pages ({len(COMPANY_CAREER_PAGES)} companies)...")
    try:
        career_jobs = scrape_company_careers()
        print(f"  → {len(career_jobs)} relevant jobs from company pages")
        all_raw.extend(career_jobs)
    except Exception as e:
        print(f"  ✗ {e}")

    # ── 4. Filter & score ────────────────────────────────────
    print(f"\n[Filter] Total raw: {len(all_raw)}")
    filtered  = filter_jobs(all_raw)
    new_jobs  = [j for j in filtered if not is_seen(j["id"])]
    print(f"[Filter] Relevant: {len(filtered)} | New: {len(new_jobs)}")

    if not new_jobs:
        print("[Bot] Tidak ada job baru.")
        notify_summary(get_stats(), 0, 0)
        return

    # ── 5. Summary singkat dulu ke Telegram ─────────────────
    notify_new_jobs_summary(new_jobs)

    # ── 6. Per job: generate cover letter + kirim ke Telegram ─
    applied_count = 0
    print(f"\n[Cover Letter] Generating untuk {len(new_jobs)} jobs...")

    for i, job in enumerate(new_jobs, 1):
        print(f"  [{i}/{len(new_jobs)}] {job['title'][:50]}")

        # Generate cover letter
        cover = gen_cover(job)

        # Kirim ke Telegram dengan cover letter (untuk semua job)
        notify_new_job_with_cover(job, cover)

        # Save ke DB
        save_job(job, status="notified", cover_letter=cover)

        # Kalau ada email → auto kirim
        if job.get("email") and not dry_run and SEND_EMAILS:
            if applied_count < MAX_EMAILS_PER_RUN:
                ok = send_application(job, cover)
                if ok:
                    mark_applied(job["id"])
                    notify_applied(job)
                    applied_count += 1

    # ── 7. Summary akhir ─────────────────────────────────────
    stats = get_stats()
    notify_summary(stats, len(new_jobs), applied_count)
    print(f"\n{'='*65}")
    print(f"  SELESAI | New: {len(new_jobs)} | Auto-applied: {applied_count}")
    print(f"  Total DB: {stats['total']} | Total Applied: {stats['applied']}")
    print(f"{'='*65}\n")

def dashboard():
    from core.tracker import get_all_jobs
    jobs  = get_all_jobs(50)
    stats = get_stats()
    print(f"\n{'='*65}")
    print(f"  JOB BOT DASHBOARD")
    print(f"  Total: {stats['total']} | Applied: {stats['applied']} | Today: {stats['today']}")
    print(f"{'='*65}")
    print(f"{'#':<4} {'Score':<6} {'Status':<12} {'Title':<38} {'Source'}")
    print("-"*80)
    for i, j in enumerate(jobs, 1):
        title = j["title"][:36] + ".." if len(j["title"]) > 38 else j["title"]
        print(f"{i:<4} {j['score']:<6} {j['status']:<12} {title:<38} {j['source']}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Job Bot v2")
    parser.add_argument("--dry-run",   action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    args = parser.parse_args()
    if args.dashboard:
        dashboard()
    else:
        run(dry_run=args.dry_run)
