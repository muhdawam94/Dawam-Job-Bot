# scrapers/weworkremotely.py
import requests, time
from bs4 import BeautifulSoup
from config import REQUEST_DELAY_SEC

BASE = "https://weworkremotely.com"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)"}

FEEDS = [
    "/remote-jobs/search.json?term=python",
    "/remote-jobs/search.json?term=web3",
    "/remote-jobs/search.json?term=trading",
    "/remote-jobs/search.json?term=react",
    "/remote-jobs/search.json?term=blockchain",
]

def scrape() -> list[dict]:
    jobs = []
    seen = set()
    for feed in FEEDS:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(BASE + feed, headers=HEADERS, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            for item in data.get("jobs", []):
                uid = str(item.get("id", ""))
                if uid in seen:
                    continue
                seen.add(uid)
                jobs.append({
                    "source":      "WeWorkRemotely",
                    "id":          uid,
                    "title":       item.get("title", ""),
                    "company":     item.get("company", ""),
                    "location":    item.get("region", "Worldwide"),
                    "tags":        item.get("category", ""),
                    "description": item.get("description", ""),
                    "url":         BASE + item.get("url", ""),
                    "email":       "",
                    "date":        item.get("created_at", ""),
                })
        except Exception as e:
            print(f"[WWR] Error {feed}: {e}")
    return jobs
