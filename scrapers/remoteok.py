# scrapers/remoteok.py
import requests, time
from config import REQUEST_DELAY_SEC

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; JobBot/1.0)"}

def scrape() -> list[dict]:
    """Scrape RemoteOK via public JSON API."""
    jobs = []
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = requests.get("https://remoteok.com/api", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for item in data:
            if not isinstance(item, dict) or "id" not in item:
                continue
            jobs.append({
                "source":      "RemoteOK",
                "id":          str(item.get("id", "")),
                "title":       item.get("position", ""),
                "company":     item.get("company", ""),
                "location":    item.get("location", "Worldwide"),
                "tags":        " ".join(item.get("tags", [])),
                "description": item.get("description", ""),
                "url":         item.get("url", f"https://remoteok.com/remote-jobs/{item.get('id')}"),
                "email":       item.get("company_email", ""),
                "date":        item.get("date", ""),
            })
    except Exception as e:
        print(f"[RemoteOK] Error: {e}")
    return jobs
