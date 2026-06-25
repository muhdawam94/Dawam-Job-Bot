# scrapers/wellfound.py
# Wellfound tidak punya public API gratis, kita scrape RSS/sitemap jobs
# sebagai fallback pakai Remotive + tag "startup"

import requests, time
from config import REQUEST_DELAY_SEC

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)"}

def scrape() -> list[dict]:
    """
    Wellfound (AngelList Talent) tidak punya open API.
    Sebagai pengganti, kita scrape Remotive dengan filter 'startup'
    dan Arbeitnow yang gratis & open.
    """
    jobs = []
    try:
        time.sleep(REQUEST_DELAY_SEC)
        # Arbeitnow — gratis, JSON API, banyak startup remote
        resp = requests.get(
            "https://www.arbeitnow.com/api/job-board-api",
            headers=HEADERS, timeout=15
        )
        resp.raise_for_status()
        for item in resp.json().get("data", []):
            jobs.append({
                "source":      "Arbeitnow",
                "id":          str(item.get("slug", "")),
                "title":       item.get("title", ""),
                "company":     item.get("company_name", ""),
                "location":    item.get("location", "Remote"),
                "tags":        " ".join(item.get("tags", [])),
                "description": item.get("description", ""),
                "url":         item.get("url", ""),
                "email":       "",
                "date":        item.get("created_at", ""),
            })
    except Exception as e:
        print(f"[Arbeitnow] Error: {e}")
    return jobs
