# scrapers/remotive.py
import requests, time
from config import REQUEST_DELAY_SEC

BASE = "https://remotive.com/api/remote-jobs"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)"}

CATEGORIES = ["software-dev", "devops-sysadmin", "finance-legal"]

def scrape() -> list[dict]:
    jobs = []
    seen = set()
    for cat in CATEGORIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(BASE, params={"category": cat, "limit": 50},
                                headers=HEADERS, timeout=15)
            resp.raise_for_status()
            for item in resp.json().get("jobs", []):
                uid = str(item.get("id", ""))
                if uid in seen:
                    continue
                seen.add(uid)
                jobs.append({
                    "source":      "Remotive",
                    "id":          uid,
                    "title":       item.get("title", ""),
                    "company":     item.get("company_name", ""),
                    "location":    item.get("candidate_required_location", "Worldwide"),
                    "tags":        " ".join(item.get("tags", [])),
                    "description": item.get("description", ""),
                    "url":         item.get("url", ""),
                    "email":       "",
                    "date":        item.get("publication_date", ""),
                })
        except Exception as e:
            print(f"[Remotive] Error {cat}: {e}")
    return jobs
