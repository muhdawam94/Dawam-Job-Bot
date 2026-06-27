# scrapers/newboards.py — Malt, Contra, Arc.dev
import requests, time, re
from bs4 import BeautifulSoup
from config import REQUEST_DELAY_SEC

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
    "Accept": "application/json, text/html, */*"
}

# ── ARC.DEV ──────────────────────────────────────────────────
ARC_QUERIES = ["python", "web3", "trading", "react", "blockchain", "metatrader"]

def scrape_arc() -> list[dict]:
    jobs = []
    seen = set()
    for q in ARC_QUERIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(
                "https://arc.dev/remote-jobs/api",
                params={"keywords": q, "remote": "true", "limit": 20},
                headers=HEADERS, timeout=15
            )
            if resp.status_code != 200:
                # Fallback: scrape HTML
                resp2 = requests.get(
                    f"https://arc.dev/remote-jobs?keywords={q}",
                    headers=HEADERS, timeout=15
                )
                soup = BeautifulSoup(resp2.text, "html.parser")
                for card in soup.select("[data-job-id]")[:10]:
                    uid = card.get("data-job-id", "")
                    if uid in seen: continue
                    seen.add(uid)
                    title = card.select_one("h2, h3, .job-title")
                    company = card.select_one(".company-name, .company")
                    jobs.append({
                        "source": "Arc.dev", "id": f"arc_{uid}",
                        "title": title.text.strip() if title else q + " Developer",
                        "company": company.text.strip() if company else "Company",
                        "location": "Remote", "tags": q,
                        "description": "", "url": f"https://arc.dev/remote-jobs/{uid}",
                        "email": "", "date": ""
                    })
                continue

            for item in resp.json().get("jobs", []):
                uid = str(item.get("id", item.get("slug", "")))
                if uid in seen: continue
                seen.add(uid)
                jobs.append({
                    "source": "Arc.dev", "id": f"arc_{uid}",
                    "title": item.get("title", ""),
                    "company": item.get("company", {}).get("name", "") if isinstance(item.get("company"), dict) else item.get("company", ""),
                    "location": "Remote",
                    "tags": " ".join(item.get("skills", [])),
                    "description": item.get("description", ""),
                    "url": f"https://arc.dev/remote-jobs/{item.get('slug', uid)}",
                    "email": "", "date": item.get("postedAt", "")
                })
        except Exception as e:
            print(f"[Arc.dev] Error {q}: {e}")
    return jobs


# ── FREELANCERMAP (Jerman) ───────────────────────────────────
def scrape_freelancermap() -> list[dict]:
    jobs = []
    queries = ["python", "metatrader", "mql5", "web3", "react", "trading", "blockchain"]
    for q in queries:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(
                "https://www.freelancermap.com/remote-jobs",
                params={"query": q, "remote": 1},
                headers=HEADERS, timeout=15
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select(".project-container, .project-list-entry, article.project")[:10]:
                title_el = card.select_one("h2 a, h3 a, .project-title a")
                if not title_el: continue
                uid = title_el.get("href", "").split("/")[-1].split("?")[0]
                if not uid: continue
                company_el = card.select_one(".company, .client, .provider")
                jobs.append({
                    "source": "FreelancerMap🇩🇪",
                    "id": f"fmap_{uid}",
                    "title": title_el.text.strip(),
                    "company": company_el.text.strip() if company_el else "German Company",
                    "location": "Remote",
                    "tags": q,
                    "description": card.get_text(" ", strip=True)[:300],
                    "url": "https://www.freelancermap.com" + title_el.get("href", ""),
                    "email": "", "date": ""
                })
        except Exception as e:
            print(f"[FreelancerMap] Error {q}: {e}")
    return jobs


# ── MALT (Jerman/Eropa) ──────────────────────────────────────
def scrape_malt() -> list[dict]:
    """Malt tidak punya public API — kita scrape search page."""
    jobs = []
    queries = ["python developer", "web3 developer", "trading bot", "react developer", "blockchain"]
    for q in queries:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(
                "https://www.malt.com/s",
                params={"q": q, "remote": "true"},
                headers=HEADERS, timeout=15
            )
            soup = BeautifulSoup(resp.text, "html.parser")
            for card in soup.select(".freelancer-card, [data-cy='freelancer-card'], .profile-card")[:5]:
                name_el = card.select_one("h2, h3, .name")
                if not name_el: continue
                link_el = card.select_one("a[href*='/profile/']")
                uid = link_el.get("href", "").split("/")[-1] if link_el else name_el.text.strip().replace(" ", "_")
                jobs.append({
                    "source": "Malt🇩🇪",
                    "id": f"malt_{uid}",
                    "title": f"{q.title()} Freelancer Available",
                    "company": "Direct Client (Malt)",
                    "location": "Remote Europe",
                    "tags": q,
                    "description": card.get_text(" ", strip=True)[:300],
                    "url": "https://www.malt.com" + (link_el.get("href", "") if link_el else ""),
                    "email": "", "date": ""
                })
        except Exception as e:
            print(f"[Malt] Error {q}: {e}")
    return jobs


# ── CONTRA (0% komisi) ───────────────────────────────────────
def scrape_contra() -> list[dict]:
    jobs = []
    try:
        time.sleep(REQUEST_DELAY_SEC)
        # Contra punya public opportunity API
        resp = requests.get(
            "https://contra.com/api/opportunities",
            params={"search": "python developer", "remote": True, "limit": 30},
            headers=HEADERS, timeout=15
        )
        if resp.status_code == 200:
            for item in resp.json().get("data", []):
                uid = str(item.get("id", ""))
                jobs.append({
                    "source": "Contra",
                    "id": f"contra_{uid}",
                    "title": item.get("title", ""),
                    "company": item.get("client", {}).get("name", "Client") if isinstance(item.get("client"), dict) else "Client",
                    "location": "Remote",
                    "tags": " ".join(item.get("skills", [])),
                    "description": item.get("description", ""),
                    "url": f"https://contra.com/opportunity/{uid}",
                    "email": "", "date": item.get("createdAt", "")
                })
        else:
            # Fallback: scrape jobs page
            resp2 = requests.get("https://contra.com/jobs?q=python+remote", headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp2.text, "html.parser")
            for card in soup.select("[data-testid='job-card'], .job-card")[:10]:
                title_el = card.select_one("h2, h3")
                if not title_el: continue
                uid = re.sub(r'\W+', '_', title_el.text.strip())[:30]
                jobs.append({
                    "source": "Contra",
                    "id": f"contra_{uid}",
                    "title": title_el.text.strip(),
                    "company": "Client on Contra",
                    "location": "Remote",
                    "tags": "python remote",
                    "description": card.get_text(" ", strip=True)[:300],
                    "url": "https://contra.com/jobs",
                    "email": "", "date": ""
                })
    except Exception as e:
        print(f"[Contra] Error: {e}")
    return jobs


# ── GUN.IO (developer khusus) ────────────────────────────────
def scrape_gunio() -> list[dict]:
    jobs = []
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = requests.get(
            "https://gun.io/find-jobs/",
            headers=HEADERS, timeout=15
        )
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select(".job-listing, .job-card, article")[:15]:
            title_el = card.select_one("h2 a, h3 a, .job-title")
            if not title_el: continue
            uid = title_el.get("href", "").split("/")[-2] or title_el.text.strip()[:20]
            company_el = card.select_one(".company, .client")
            jobs.append({
                "source": "Gun.io",
                "id": f"gunio_{uid}",
                "title": title_el.text.strip(),
                "company": company_el.text.strip() if company_el else "Tech Company",
                "location": "Remote",
                "tags": "developer python remote",
                "description": card.get_text(" ", strip=True)[:300],
                "url": "https://gun.io" + (title_el.get("href", "") if title_el.get("href", "").startswith("/") else ""),
                "email": "", "date": ""
            })
    except Exception as e:
        print(f"[Gun.io] Error: {e}")
    return jobs
