# scrapers/himalayas.py
import requests, time
from config import REQUEST_DELAY_SEC

BASE = "https://himalayas.app/jobs/api"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)"}

QUERIES = ["python", "web3", "trading", "react", "blockchain", "metatrader"]

def scrape() -> list[dict]:
    jobs = []
    seen = set()
    for q in QUERIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(BASE, params={"q": q, "limit": 20},
                                headers=HEADERS, timeout=15)
            resp.raise_for_status()
            for item in resp.json().get("jobs", []):
                uid = str(item.get("id") or item.get("slug", ""))
                if uid in seen:
                    continue
                seen.add(uid)
                jobs.append({
                    "source":      "Himalayas",
                    "id":          uid,
                    "title":       item.get("title", ""),
                    "company":     item.get("companyName", ""),
                    "location":    item.get("locationRestrictions", ["Worldwide"])[0]
                                   if item.get("locationRestrictions") else "Worldwide",
                    "tags":        " ".join(item.get("skills", [])),
                    "description": item.get("descriptionHtml", ""),
                    "url":         f"https://himalayas.app/jobs/{item.get('slug',uid)}",
                    "email":       "",
                    "date":        item.get("createdAt", ""),
                })
        except Exception as e:
            print(f"[Himalayas] Error {q}: {e}")
    return jobs
