# scrapers/web3_jobs.py v2
# Semua perusahaan Web3 dari list Dawam + API Greenhouse/Lever

import requests, time
from bs4 import BeautifulSoup
from config import REQUEST_DELAY_SEC

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}

# ══════════════════════════════════════════════════════════════
# GREENHOUSE API — perusahaan Web3 yang pakai Greenhouse
# ══════════════════════════════════════════════════════════════
GREENHOUSE_COMPANIES = [
    # Exchange & Trading
    ("Coinbase",        "coinbase"),
    ("Gemini",          "gemini"),
    ("Kraken",          "kraken"),
    ("Hyperliquid",     "hyperliquid"),

    # DeFi & Infrastructure
    ("Uniswap Labs",    "uniswaplabs"),
    ("Aave",            "aave"),
    ("Lido",            "lidofinance"),
    ("Chainlink",       "chainlink"),
    ("Alchemy",         "alchemyinsights"),
    ("The Graph",       "thegraph"),
    ("QuickNode",       "quicknode"),

    # NFT & Gaming
    ("OpenSea",         "opensea"),
    ("Magic Eden",      "magiceden"),
    ("Axie Infinity",   "skymavis"),       # Sky Mavis = Axie
    ("Illuvium",        "illuvium"),
    ("Decentraland",    "decentraland"),

    # Wallets
    ("MetaMask/Consensys", "consensys"),
    ("Exodus",          "exodus"),

    # Analytics & Tools
    ("DappRadar",       "dappradar"),
    ("Chainalysis",     "chainalysis"),
    ("Fireblocks",      "fireblocks"),

    # Other Web3
    ("Compound",        "compoundlabs"),
    ("Optimism",        "optimism"),
    ("Arbitrum",        "arbitrum"),
    ("Polygon",         "polygon-labs"),
    ("Galxe",           "galxe"),
]

# ══════════════════════════════════════════════════════════════
# LEVER API — perusahaan Web3 yang pakai Lever
# ══════════════════════════════════════════════════════════════
LEVER_COMPANIES = [
    # Exchange & Trading
    ("OKX",             "okx"),
    ("Binance",         "binance"),

    # DeFi
    ("dYdX",            "dydx"),
    ("Curve Finance",   "curvefi"),
    ("Polymarket",      "polymarket"),
    ("Aerodrome",       "aerodrome"),

    # Infrastructure
    ("Chainlink Labs",  "chainlink-labs"),
    ("StarkWare",       "starkware"),
    ("Aztec",           "azteclabs"),
    ("Figment",         "figment"),

    # NFT & Social
    ("Blur",            "blur"),
    ("Rarible",         "rarible"),
    ("Lens Protocol",   "lens"),
    ("Warpcast",        "farcaster"),
    ("CyberConnect",    "cyberconnect"),

    # Wallets
    ("Rainbow",         "rainbow"),
    ("Trust Wallet",    "trustwallet"),
    ("Phantom",         "phantom"),

    # Analytics
    ("DeBank",          "debank"),
    ("DeFiLlama",       "defillama"),
    ("Ledger",          "ledger"),
    ("Figment",         "figment"),
]

# ══════════════════════════════════════════════════════════════
# ASHBY API — banyak startup Web3 baru pakai Ashby
# ══════════════════════════════════════════════════════════════
ASHBY_COMPANIES = [
    ("Uniswap",         "uniswap"),
    ("Blur",            "blur"),
    ("Hyperliquid",     "hyperliquid"),
    ("Polymarket",      "polymarket"),
    ("Warpcast",        "warpcast"),
    ("Pixels",          "pixels"),
    ("Magic Eden",      "magiceden"),
    ("Aerodrome",       "aerodrome"),
]

# ══════════════════════════════════════════════════════════════
# DIRECT API — perusahaan dengan API karir sendiri
# ══════════════════════════════════════════════════════════════
DIRECT_CAREERS = [
    {
        "name": "Binance",
        "api": "https://www.binance.com/bapi/composite/v1/public/marketing/job/list",
        "url_template": "https://www.binance.com/en/careers/job-openings?id={id}",
        "id_field": "jobId", "title_field": "jobTitle",
        "desc_field": "jobDescription", "loc_field": "location",
    },
    {
        "name": "OKX",
        "api": "https://www.okx.com/v2/support/talent/position",
        "url_template": "https://www.okx.com/careers/detail/{id}",
        "id_field": "positionId", "title_field": "positionName",
        "desc_field": "positionDesc", "loc_field": "workCity",
    },
]

WEB3_KEYWORDS = [
    "python", "developer", "engineer", "backend", "frontend", "fullstack",
    "smart contract", "blockchain", "web3", "defi", "trading", "quant",
    "automation", "solidity", "rust", "react", "typescript", "node",
    "data", "analyst", "researcher", "protocol", "infrastructure", "remote"
]

def _relevant(text: str) -> bool:
    t = text.lower()
    return any(k in t for k in WEB3_KEYWORDS)

# ── Greenhouse scraper ───────────────────────────────────────
def scrape_greenhouse_web3() -> list[dict]:
    jobs = []
    for company_name, slug in GREENHOUSE_COMPANIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            r = requests.get(
                f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs",
                params={"content": "true"}, headers=HEADERS, timeout=15
            )
            if r.status_code != 200:
                continue
            for j in r.json().get("jobs", []):
                if not _relevant(j.get("title","") + j.get("content","")):
                    continue
                uid = str(j.get("id",""))
                jobs.append({
                    "source":      "Greenhouse🌿",
                    "id":          f"gh_{slug}_{uid}",
                    "title":       j.get("title",""),
                    "company":     company_name,
                    "location":    j.get("location",{}).get("name","Remote"),
                    "tags":        "web3 blockchain developer crypto",
                    "description": j.get("content","")[:400],
                    "url":         j.get("absolute_url", f"https://boards.greenhouse.io/{slug}/jobs/{uid}"),
                    "email":       "",
                    "date":        j.get("updated_at",""),
                })
        except Exception as e:
            print(f"    [GH/{company_name}] {e}")
    return jobs

# ── Lever scraper ────────────────────────────────────────────
def scrape_lever_web3() -> list[dict]:
    jobs = []
    for company_name, slug in LEVER_COMPANIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            r = requests.get(
                f"https://api.lever.co/v0/postings/{slug}",
                params={"mode": "json"}, headers=HEADERS, timeout=15
            )
            if r.status_code != 200:
                continue
            for j in r.json():
                cats = j.get("categories", {})
                if not _relevant(j.get("text","") + cats.get("team","")):
                    continue
                uid = j.get("id","")
                jobs.append({
                    "source":      "Lever⚡",
                    "id":          f"lv_{slug}_{uid}",
                    "title":       j.get("text",""),
                    "company":     company_name,
                    "location":    cats.get("location","Remote"),
                    "tags":        "web3 blockchain developer crypto",
                    "description": j.get("descriptionPlain","")[:400],
                    "url":         j.get("hostedUrl", f"https://jobs.lever.co/{slug}/{uid}"),
                    "email":       "",
                    "date":        "",
                })
        except Exception as e:
            print(f"    [LV/{company_name}] {e}")
    return jobs

# ── Ashby scraper ────────────────────────────────────────────
def scrape_ashby_web3() -> list[dict]:
    jobs = []
    for company_name, slug in ASHBY_COMPANIES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            r = requests.get(
                f"https://jobs.ashbyhq.com/api/non-user-graphql",
                json={"operationName":"ApiJobBoardWithTeams",
                      "query":"query ApiJobBoardWithTeams($organizationHostedJobsPageName:String!){jobBoard:jobBoardWithTeams(organizationHostedJobsPageName:$organizationHostedJobsPageName){jobPostings{id title locationName departmentName}}}",
                      "variables":{"organizationHostedJobsPageName": slug}},
                headers={**HEADERS, "Content-Type":"application/json"}, timeout=15
            )
            if r.status_code != 200:
                continue
            for j in r.json().get("data",{}).get("jobBoard",{}).get("jobPostings",[]):
                if not _relevant(j.get("title","") + j.get("departmentName","")):
                    continue
                uid = j.get("id","")
                jobs.append({
                    "source":      "Ashby🔷",
                    "id":          f"ash_{slug}_{uid}",
                    "title":       j.get("title",""),
                    "company":     company_name,
                    "location":    j.get("locationName","Remote"),
                    "tags":        "web3 blockchain developer crypto",
                    "description": f"Position at {company_name}",
                    "url":         f"https://jobs.ashbyhq.com/{slug}/{uid}",
                    "email":       "",
                    "date":        "",
                })
        except Exception as e:
            print(f"    [Ash/{company_name}] {e}")
    return jobs

# ── Web3 job boards ──────────────────────────────────────────
def scrape_web3_boards() -> list[dict]:
    jobs = []

    # CryptoJobsList
    try:
        time.sleep(REQUEST_DELAY_SEC)
        r = requests.get("https://cryptojobslist.com/api/jobs", headers=HEADERS, timeout=15)
        if r.status_code == 200:
            for item in r.json().get("jobs", [])[:40]:
                uid = str(item.get("id", item.get("slug","")))
                company = item.get("company",{})
                jobs.append({
                    "source":  "CryptoJobsList🌐",
                    "id":      f"cjl_{uid}",
                    "title":   item.get("title",""),
                    "company": company.get("name","") if isinstance(company,dict) else str(company),
                    "location": item.get("location","Remote"),
                    "tags":    " ".join(item.get("tags",[])),
                    "description": item.get("description","")[:400],
                    "url":     item.get("url", f"https://cryptojobslist.com/jobs/{uid}"),
                    "email":   "", "date": item.get("createdAt",""),
                })
    except Exception as e:
        print(f"    [CryptoJobsList] {e}")

    # Web3.career
    for keyword in ["python", "developer", "engineer", "defi", "blockchain"]:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            r = requests.get(f"https://web3.career/{keyword}-jobs", headers=HEADERS, timeout=15)
            soup = BeautifulSoup(r.text, "html.parser")
            for card in soup.select("tr[data-id], .job-card")[:10]:
                title_el = card.select_one("h2 a, h3 a, td a")
                if not title_el: continue
                href = title_el.get("href","")
                uid  = href.split("/")[-1] or title_el.text[:20]
                company_el = card.select_one(".company, td:nth-child(2)")
                jobs.append({
                    "source":  "Web3Career🔗",
                    "id":      f"w3c_{keyword}_{uid}",
                    "title":   title_el.text.strip(),
                    "company": company_el.text.strip() if company_el else "Web3 Company",
                    "location": "Remote",
                    "tags":    f"web3 {keyword} developer",
                    "description": "",
                    "url":     f"https://web3.career{href}" if href.startswith("/") else href,
                    "email":   "", "date": "",
                })
        except Exception as e:
            print(f"    [Web3Career/{keyword}] {e}")

    # Binance direct
    try:
        time.sleep(REQUEST_DELAY_SEC)
        r = requests.get(
            "https://www.binance.com/bapi/composite/v1/public/marketing/job/list",
            headers=HEADERS, timeout=15
        )
        if r.status_code == 200:
            for item in r.json().get("data",{}).get("list",[])[:30]:
                title = item.get("jobTitle","")
                if not _relevant(title): continue
                uid = str(item.get("jobId",""))
                jobs.append({
                    "source":  "Binance🟡",
                    "id":      f"bnb_{uid}",
                    "title":   title,
                    "company": "Binance",
                    "location": item.get("location","Remote"),
                    "tags":    "web3 crypto blockchain developer python",
                    "description": item.get("jobDescription","")[:400],
                    "url":     f"https://www.binance.com/en/careers/job-openings?id={uid}",
                    "email":   "", "date": "",
                })
    except Exception as e:
        print(f"    [Binance] {e}")

    return jobs

def scrape_all_web3() -> list[dict]:
    all_jobs = []

    print("  [Web3-Greenhouse] Scraping...")
    gh = scrape_greenhouse_web3()
    print(f"    → {len(gh)} jobs dari {len(GREENHOUSE_COMPANIES)} perusahaan")
    all_jobs.extend(gh)

    print("  [Web3-Lever] Scraping...")
    lv = scrape_lever_web3()
    print(f"    → {len(lv)} jobs dari {len(LEVER_COMPANIES)} perusahaan")
    all_jobs.extend(lv)

    print("  [Web3-Ashby] Scraping...")
    ash = scrape_ashby_web3()
    print(f"    → {len(ash)} jobs dari {len(ASHBY_COMPANIES)} perusahaan")
    all_jobs.extend(ash)

    print("  [Web3-Boards] Scraping...")
    boards = scrape_web3_boards()
    print(f"    → {len(boards)} jobs dari Web3 job boards")
    all_jobs.extend(boards)

    return all_jobs
