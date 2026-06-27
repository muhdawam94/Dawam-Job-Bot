# scrapers/company_careers.py
# Monitor halaman karir perusahaan yang tidak post di job board
# Notif Telegram langsung saat ada job baru

import requests, time, hashlib
from bs4 import BeautifulSoup
from config import REQUEST_DELAY_SEC

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"
}

# ══════════════════════════════════════════════════════════════
# DAFTAR PERUSAHAAN — tambah sesukamu!
# Format: { "name", "country", "careers_url", "keywords" }
# ══════════════════════════════════════════════════════════════
COMPANY_CAREER_PAGES = [

    # ── JERMAN 🇩🇪 ───────────────────────────────────────────
    {
        "name": "Personio", "country": "🇩🇪",
        "url": "https://www.personio.com/about-personio/careers/",
        "keywords": ["python", "remote", "developer", "engineer", "backend", "frontend"]
    },
    {
        "name": "Celonis", "country": "🇩🇪",
        "url": "https://www.celonis.com/careers/jobs/",
        "keywords": ["python", "developer", "engineer", "remote", "software"]
    },
    {
        "name": "Statista", "country": "🇩🇪",
        "url": "https://www.statista.com/jobs/",
        "keywords": ["developer", "python", "react", "remote", "engineer"]
    },
    {
        "name": "FlixBus (Flix)", "country": "🇩🇪",
        "url": "https://www.flixbus.com/company/jobs",
        "keywords": ["developer", "python", "engineer", "remote", "backend"]
    },
    {
        "name": "Zalando Tech", "country": "🇩🇪",
        "url": "https://jobs.zalando.com/en/jobs/",
        "keywords": ["python", "developer", "engineer", "remote", "backend", "trading"]
    },
    {
        "name": "N26 (Berlin)", "country": "🇩🇪",
        "url": "https://n26.com/en-de/careers",
        "keywords": ["developer", "python", "engineer", "remote", "fintech"]
    },
    {
        "name": "Trade Republic", "country": "🇩🇪",
        "url": "https://traderepublic.com/careers",
        "keywords": ["developer", "python", "trading", "engineer", "remote", "fintech"]
    },
    {
        "name": "Kraken (DE Office)", "country": "🇩🇪",
        "url": "https://jobs.lever.co/kraken",
        "keywords": ["python", "developer", "remote", "crypto", "blockchain", "trading"]
    },

    # ── BELANDA 🇳🇱 ──────────────────────────────────────────
    {
        "name": "Booking.com", "country": "🇳🇱",
        "url": "https://jobs.booking.com/careers",
        "keywords": ["python", "developer", "engineer", "remote", "backend"]
    },
    {
        "name": "Adyen", "country": "🇳🇱",
        "url": "https://www.adyen.com/careers/vacancies",
        "keywords": ["developer", "python", "engineer", "fintech", "remote"]
    },

    # ── INGGRIS 🇬🇧 ──────────────────────────────────────────
    {
        "name": "Revolut", "country": "🇬🇧",
        "url": "https://www.revolut.com/careers/",
        "keywords": ["python", "developer", "remote", "trading", "fintech", "engineer"]
    },
    {
        "name": "Wise (TransferWise)", "country": "🇬🇧",
        "url": "https://wise.com/gb/careers/",
        "keywords": ["python", "developer", "engineer", "remote", "fintech"]
    },
    {
        "name": "IG Group (Trading)", "country": "🇬🇧",
        "url": "https://www.ig.com/uk/about-ig-group/careers",
        "keywords": ["developer", "python", "trading", "engineer", "remote", "quant"]
    },
    {
        "name": "Man Group (Quant)", "country": "🇬🇧",
        "url": "https://www.man.com/careers",
        "keywords": ["python", "quant", "trading", "developer", "remote", "algo"]
    },

    # ── USA REMOTE-FIRST 🇺🇸 ─────────────────────────────────
    {
        "name": "Coinbase", "country": "🇺🇸",
        "url": "https://www.coinbase.com/careers/positions",
        "keywords": ["python", "developer", "remote", "crypto", "blockchain", "engineer"]
    },
    {
        "name": "Binance", "country": "🌍",
        "url": "https://www.binance.com/en/careers/job-openings",
        "keywords": ["python", "developer", "remote", "crypto", "blockchain", "trading", "engineer"]
    },
    {
        "name": "Chainlink Labs", "country": "🌍",
        "url": "https://jobs.lever.co/chainlink",
        "keywords": ["python", "developer", "remote", "blockchain", "web3", "smart contract"]
    },
    {
        "name": "Consensys (MetaMask)", "country": "🌍",
        "url": "https://jobs.lever.co/consensys",
        "keywords": ["python", "developer", "remote", "blockchain", "web3", "ethereum"]
    },
    {
        "name": "dYdX (DeFi Trading)", "country": "🌍",
        "url": "https://jobs.lever.co/dydx",
        "keywords": ["python", "developer", "remote", "defi", "trading", "blockchain"]
    },
    {
        "name": "Uniswap Labs", "country": "🌍",
        "url": "https://boards.greenhouse.io/uniswaplabs",
        "keywords": ["python", "developer", "remote", "defi", "web3", "blockchain"]
    },

    # ── ASIA/GLOBAL ──────────────────────────────────────────
    {
        "name": "OKX", "country": "🌏",
        "url": "https://www.okx.com/careers/positions",
        "keywords": ["python", "developer", "remote", "crypto", "trading", "engineer"]
    },
    {
        "name": "Bybit", "country": "🌏",
        "url": "https://careers.bybit.com/",
        "keywords": ["python", "developer", "remote", "trading", "crypto", "engineer"]
    },
]


def _make_id(company_name: str, title: str) -> str:
    return "cc_" + hashlib.md5(f"{company_name}:{title}".encode()).hexdigest()[:12]

def _extract_jobs(html: str, company: dict) -> list[dict]:
    """Extract job listings dari HTML halaman careers."""
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    keywords = company["keywords"]

    # Coba berbagai selector umum halaman careers
    selectors = [
        "a[href*='/job']", "a[href*='/careers/']", "a[href*='/position']",
        "a[href*='/opening']", "a[href*='/vacancy']", "a[href*='/role']",
        ".job-listing a", ".position a", ".opening a", ".career-item a",
        "li.job a", "div.job a", "tr.job a",
        "[data-job] a", "[data-position] a",
    ]

    found_links = set()
    for selector in selectors:
        for el in soup.select(selector):
            href = el.get("href", "")
            text = el.get_text(" ", strip=True)
            if not text or len(text) < 5 or href in found_links:
                continue
            found_links.add(href)

            # Cek apakah relevan dengan keyword
            text_lower = text.lower()
            if not any(kw in text_lower for kw in keywords):
                continue

            # Build full URL
            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                base = "/".join(company["url"].split("/")[:3])
                full_url = base + href
            else:
                full_url = company["url"] + "/" + href

            jobs.append({
                "source": f"Career_{company['name']}",
                "id": _make_id(company["name"], text),
                "title": text[:100],
                "company": company["name"],
                "location": f"Remote {company['country']}",
                "tags": " ".join(keywords),
                "description": f"Job at {company['name']} careers page",
                "url": full_url,
                "email": "",
                "date": ""
            })

    return jobs[:10]  # max 10 per perusahaan

def scrape_company_careers() -> list[dict]:
    """Scrape semua halaman careers perusahaan."""
    all_jobs = []
    for company in COMPANY_CAREER_PAGES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            resp = requests.get(company["url"], headers=HEADERS, timeout=15)
            resp.raise_for_status()
            jobs = _extract_jobs(resp.text, company)
            if jobs:
                print(f"  [{company['name']}] {len(jobs)} relevant jobs found")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"  [{company['name']}] Error: {e}")
    return all_jobs
