# scrapers/web3_jobs.py
# Scrape langsung dari job board Web3 yang punya API publik
# + Greenhouse/Lever API untuk perusahaan Web3 spesifik

import requests, time
from bs4 import BeautifulSoup
from config import REQUEST_DELAY_SEC

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}

# ── Web3 companies yang pakai Greenhouse API ─────────────────
GREENHOUSE_COMPANIES = [
    ("Coinbase",      "coinbase"),
    ("Gemini",        "gemini"),
    ("Kraken",        "kraken"),
    ("Chainalysis",   "chainalysis"),
    ("Alchemy",       "alchemyinsights"),
    ("OpenSea",       "opensea"),
    ("Uniswap",       "uniswaplabs"),
    ("Compound",      "compoundlabs"),
    ("Optimism",      "optimism"),
    ("Arbitrum",      "arbitrum"),
]

# ── Web3 companies yang pakai Lever API ─────────────────────
LEVER_COMPANIES = [
    ("Consensys",     "consensys"),
    ("Chainlink",     "chainlink-labs"),
    ("dYdX",          "dydx"),
    ("Figment",       "figment"),
    ("Fireblocks",    "fireblocks"),
    ("Ledger",        "ledger"),
    ("Polygon",       "polygon-labs"),
    ("StarkWare",     "starkware"),
    ("Aztec",         "azteclabs"),
]

WEB3_KEYWORDS = [
    "python", "developer", "engineer", "backend", "smart contract",
    "blockchain", "web3", "defi", "trading", "quant", "automation",
    "solidity", "rust", "react", "typescript", "remote"
]

def _is_relevant(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in WEB3_KEYWORDS)

def scrape_greenhouse_web3() -> list[dict]:
    """Scrape job dari perusahaan Web3 yang pakai Greenhouse."""
    jobs = []
    for company_name, slug in GREENHOUSE_COMPANIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                params={"content": "true"},
                headers=HEADERS, timeout=15
            )
            if resp.status_code != 200:
                continue
            for job in resp.json().get("jobs", []):
                title = job.get("title", "")
                if not _is_relevant(title + " " + job.get("content", "")):
                    continue
                uid = str(job.get("id", ""))
                jobs.append({
                    "source":      f"Greenhouse🌿",
                    "id":          f"gh_{slug}_{uid}",
                    "title":       title,
                    "company":     company_name,
                    "location":    job.get("location", {}).get("name", "Remote"),
                    "tags":        "web3 crypto blockchain developer",
                    "description": job.get("content", "")[:500],
                    "url":         job.get("absolute_url", f"https://boards.greenhouse.io/{slug}/jobs/{uid}"),
                    "email":       "",
                    "date":        job.get("updated_at", ""),
                })
        except Exception as e:
            print(f"  [Greenhouse/{company_name}] Error: {e}")
    return jobs

def scrape_lever_web3() -> list[dict]:
    """Scrape job dari perusahaan Web3 yang pakai Lever."""
    jobs = []
    for company_name, slug in LEVER_COMPANIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(
                f"https://api.lever.co/v0/postings/{slug}",
                params={"mode": "json"},
                headers=HEADERS, timeout=15
            )
            if resp.status_code != 200:
                continue
            for job in resp.json():
                title = job.get("text", "")
                categories = job.get("categories", {})
                if not _is_relevant(title + " " + categories.get("team", "")):
                    continue
                uid = job.get("id", "")
                jobs.append({
                    "source":      f"Lever⚡",
                    "id":          f"lv_{slug}_{uid}",
                    "title":       title,
                    "company":     company_name,
                    "location":    categories.get("location", "Remote"),
                    "tags":        "web3 crypto blockchain developer",
                    "description": job.get("descriptionPlain", "")[:500],
                    "url":         job.get("hostedUrl", f"https://jobs.lever.co/{slug}/{uid}"),
                    "email":       "",
                    "date":        "",
                })
        except Exception as e:
            print(f"  [Lever/{company_name}] Error: {e}")
    return jobs

def scrape_web3_career_boards() -> list[dict]:
    """Scrape dari job board khusus Web3."""
    jobs = []

    # 1. CryptoJobsList
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = requests.get(
            "https://cryptojobslist.com/api/jobs",
            headers=HEADERS, timeout=15
        )
        if resp.status_code == 200:
            for item in resp.json().get("jobs", [])[:30]:
                uid = str(item.get("id", item.get("slug", "")))
                jobs.append({
                    "source":      "CryptoJobsList🌐",
                    "id":          f"cjl_{uid}",
                    "title":       item.get("title", ""),
                    "company":     item.get("company", {}).get("name", "") if isinstance(item.get("company"), dict) else item.get("company", ""),
                    "location":    item.get("location", "Remote"),
                    "tags":        " ".join(item.get("tags", [])),
                    "description": item.get("description", "")[:400],
                    "url":         item.get("url", f"https://cryptojobslist.com/jobs/{uid}"),
                    "email":       "",
                    "date":        item.get("createdAt", ""),
                })
        else:
            # Fallback scrape HTML
            resp2 = requests.get("https://cryptojobslist.com/python", headers=HEADERS, timeout=15)
            soup = BeautifulSoup(resp2.text, "html.parser")
            for card in soup.select("a[href*='/jobs/']")[:15]:
                title = card.get_text(strip=True)
                if not title or len(title) < 5: continue
                href = card.get("href", "")
                uid = href.split("/")[-1]
                jobs.append({
                    "source": "CryptoJobsList🌐", "id": f"cjl_{uid}",
                    "title": title, "company": "Web3 Company",
                    "location": "Remote", "tags": "python web3 crypto",
                    "description": "", "url": f"https://cryptojobslist.com{href}",
                    "email": "", "date": ""
                })
    except Exception as e:
        print(f"  [CryptoJobsList] Error: {e}")

    # 2. Web3.career
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = requests.get("https://web3.career/python-jobs", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        for card in soup.select("tr.job_seen_beacon, .job-card, tr[data-id]")[:20]:
            title_el = card.select_one("h2 a, h3 a, .job-title, td a")
            if not title_el: continue
            company_el = card.select_one(".company, .employer")
            href = title_el.get("href", "")
            uid = href.split("/")[-1] or title_el.text.strip()[:20]
            jobs.append({
                "source": "Web3Career🔗", "id": f"w3c_{uid}",
                "title": title_el.text.strip(),
                "company": company_el.text.strip() if company_el else "Web3 Company",
                "location": "Remote", "tags": "python web3 developer",
                "description": card.get_text(" ", strip=True)[:300],
                "url": f"https://web3.career{href}" if href.startswith("/") else href,
                "email": "", "date": ""
            })
    except Exception as e:
        print(f"  [Web3.career] Error: {e}")

    # 3. Pompcryptojobs
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = requests.get(
            "https://pompcryptojobs.com/api/jobs",
            headers=HEADERS, timeout=15
        )
        if resp.status_code == 200:
            for item in resp.json().get("data", [])[:20]:
                uid = str(item.get("id", ""))
                jobs.append({
                    "source": "PompCrypto💰", "id": f"pomp_{uid}",
                    "title": item.get("title", ""),
                    "company": item.get("company_name", ""),
                    "location": item.get("location", "Remote"),
                    "tags": item.get("tags", ""),
                    "description": item.get("description", "")[:400],
                    "url": item.get("url", ""),
                    "email": "", "date": item.get("created_at", "")
                })
    except Exception as e:
        print(f"  [PompCrypto] Error: {e}")

    # 4. Binance Careers langsung
    try:
        time.sleep(REQUEST_DELAY_SEC)
        resp = requests.get(
            "https://www.binance.com/bapi/composite/v1/public/marketing/job/list",
            headers=HEADERS, timeout=15
        )
        if resp.status_code == 200:
            data = resp.json().get("data", {})
            for item in data.get("list", [])[:20]:
                title = item.get("jobTitle", "")
                if not _is_relevant(title):
                    continue
                uid = str(item.get("jobId", ""))
                jobs.append({
                    "source": "Binance🟡", "id": f"bnb_{uid}",
                    "title": title,
                    "company": "Binance",
                    "location": item.get("location", "Remote"),
                    "tags": "web3 crypto blockchain developer python",
                    "description": item.get("jobDescription", "")[:400],
                    "url": f"https://www.binance.com/en/careers/job-openings?id={uid}",
                    "email": "", "date": ""
                })
    except Exception as e:
        print(f"  [Binance] Error: {e}")

    return jobs

def scrape_all_web3() -> list[dict]:
    """Gabungkan semua scraper Web3."""
    all_jobs = []

    print("  [Web3] Greenhouse companies...")
    gh_jobs = scrape_greenhouse_web3()
    print(f"    → {len(gh_jobs)} jobs dari {len(GREENHOUSE_COMPANIES)} Web3 companies")
    all_jobs.extend(gh_jobs)

    print("  [Web3] Lever companies...")
    lv_jobs = scrape_lever_web3()
    print(f"    → {len(lv_jobs)} jobs dari {len(LEVER_COMPANIES)} Web3 companies")
    all_jobs.extend(lv_jobs)

    print("  [Web3] Web3 job boards...")
    board_jobs = scrape_web3_career_boards()
    print(f"    → {len(board_jobs)} jobs dari Web3 job boards")
    all_jobs.extend(board_jobs)

    return all_jobs
