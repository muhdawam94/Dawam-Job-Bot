# scrapers/company_careers.py v2
# Semua perusahaan Web3 dari list Dawam + perusahaan Jerman

import requests, time, hashlib
from bs4 import BeautifulSoup
from config import REQUEST_DELAY_SEC

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"}

COMPANY_CAREER_PAGES = [

    # ── EXCHANGE & TRADING ───────────────────────────────────
    {"name":"Binance",        "country":"🌍", "url":"https://www.binance.com/en/careers/job-openings",
     "keywords":["python","developer","engineer","remote","trading","blockchain","crypto","backend"]},
    {"name":"Coinbase",       "country":"🇺🇸", "url":"https://www.coinbase.com/careers/positions",
     "keywords":["python","developer","engineer","remote","crypto","blockchain","trading"]},
    {"name":"OKX",            "country":"🌏", "url":"https://www.okx.com/careers/positions",
     "keywords":["python","developer","engineer","remote","trading","crypto","backend"]},
    {"name":"Hyperliquid",    "country":"🌍", "url":"https://hyperliquid.xyz/careers",
     "keywords":["python","developer","engineer","remote","trading","defi"]},
    {"name":"PancakeSwap",    "country":"🌍", "url":"https://pancakeswap.finance/careers",
     "keywords":["developer","engineer","remote","defi","blockchain","frontend","backend"]},
    {"name":"Uniswap",        "country":"🇺🇸", "url":"https://boards.greenhouse.io/uniswaplabs",
     "keywords":["python","developer","engineer","remote","defi","blockchain","protocol"]},

    # ── WALLETS ──────────────────────────────────────────────
    {"name":"MetaMask/Consensys","country":"🌍","url":"https://jobs.lever.co/consensys",
     "keywords":["python","developer","engineer","remote","web3","blockchain","ethereum"]},
    {"name":"Phantom",        "country":"🇺🇸", "url":"https://jobs.ashbyhq.com/phantom",
     "keywords":["developer","engineer","remote","solana","blockchain","wallet"]},
    {"name":"Trust Wallet",   "country":"🌍", "url":"https://careers.binance.com",
     "keywords":["developer","engineer","remote","blockchain","wallet","mobile"]},
    {"name":"Rainbow",        "country":"🇺🇸", "url":"https://rainbow.me/jobs",
     "keywords":["developer","engineer","remote","ethereum","wallet","react","mobile"]},
    {"name":"Exodus",         "country":"🇺🇸", "url":"https://boards.greenhouse.io/exodus",
     "keywords":["python","developer","engineer","remote","blockchain","wallet","crypto"]},

    # ── NFT MARKETPLACES ─────────────────────────────────────
    {"name":"OpenSea",        "country":"🇺🇸", "url":"https://boards.greenhouse.io/opensea",
     "keywords":["python","developer","engineer","remote","nft","blockchain","backend"]},
    {"name":"Blur",           "country":"🇺🇸", "url":"https://jobs.lever.co/blur",
     "keywords":["developer","engineer","remote","nft","ethereum","trading","defi"]},
    {"name":"Magic Eden",     "country":"🇺🇸", "url":"https://jobs.ashbyhq.com/magiceden",
     "keywords":["developer","engineer","remote","nft","solana","blockchain"]},
    {"name":"Rarible",        "country":"🌍", "url":"https://jobs.lever.co/rarible",
     "keywords":["developer","engineer","remote","nft","blockchain","web3"]},

    # ── DEFI ─────────────────────────────────────────────────
    {"name":"Aave",           "country":"🌍", "url":"https://aave.com/careers",
     "keywords":["developer","engineer","remote","defi","blockchain","solidity","protocol"]},
    {"name":"Curve Finance",  "country":"🌍", "url":"https://curve.fi/careers",
     "keywords":["python","developer","engineer","remote","defi","blockchain","protocol"]},
    {"name":"Aerodrome",      "country":"🌍", "url":"https://aerodrome.finance/jobs",
     "keywords":["developer","engineer","remote","defi","base","protocol"]},
    {"name":"Lido",           "country":"🌍", "url":"https://boards.greenhouse.io/lidofinance",
     "keywords":["developer","engineer","remote","defi","ethereum","staking","protocol"]},
    {"name":"Polymarket",     "country":"🇺🇸", "url":"https://jobs.lever.co/polymarket",
     "keywords":["python","developer","engineer","remote","defi","prediction","trading"]},
    {"name":"DeFiLlama",      "country":"🌍", "url":"https://defillama.com/jobs",
     "keywords":["developer","engineer","remote","defi","data","analytics","blockchain"]},

    # ── INFRASTRUCTURE & TOOLS ───────────────────────────────
    {"name":"Chainlink",      "country":"🌍", "url":"https://jobs.lever.co/chainlink-labs",
     "keywords":["python","developer","engineer","remote","blockchain","oracle","web3"]},
    {"name":"The Graph",      "country":"🌍", "url":"https://boards.greenhouse.io/thegraph",
     "keywords":["python","developer","engineer","remote","blockchain","indexing","web3"]},
    {"name":"Alchemy",        "country":"🇺🇸", "url":"https://boards.greenhouse.io/alchemyinsights",
     "keywords":["python","developer","engineer","remote","blockchain","infrastructure","web3"]},
    {"name":"QuickNode",      "country":"🇺🇸", "url":"https://boards.greenhouse.io/quicknode",
     "keywords":["python","developer","engineer","remote","blockchain","infrastructure","rpc"]},
    {"name":"DappRadar",      "country":"🌍", "url":"https://boards.greenhouse.io/dappradar",
     "keywords":["python","developer","engineer","remote","blockchain","analytics","data"]},
    {"name":"DeBank",         "country":"🌍", "url":"https://jobs.lever.co/debank",
     "keywords":["developer","engineer","remote","defi","analytics","blockchain","data"]},

    # ── SOCIAL & COMMUNITY ───────────────────────────────────
    {"name":"Lens Protocol",  "country":"🌍", "url":"https://jobs.lever.co/lens",
     "keywords":["developer","engineer","remote","web3","social","blockchain","protocol"]},
    {"name":"Warpcast/Farcaster","country":"🇺🇸","url":"https://jobs.ashbyhq.com/warpcast",
     "keywords":["developer","engineer","remote","web3","social","protocol","react"]},
    {"name":"Galxe",          "country":"🌍", "url":"https://boards.greenhouse.io/galxe",
     "keywords":["developer","engineer","remote","web3","blockchain","community"]},
    {"name":"CyberConnect",   "country":"🌍", "url":"https://jobs.lever.co/cyberconnect",
     "keywords":["developer","engineer","remote","web3","social","blockchain"]},

    # ── GAMING & METAVERSE ───────────────────────────────────
    {"name":"Pixels",         "country":"🌍", "url":"https://jobs.ashbyhq.com/pixels",
     "keywords":["developer","engineer","remote","web3","gaming","blockchain","react"]},
    {"name":"Illuvium",       "country":"🌍", "url":"https://boards.greenhouse.io/illuvium",
     "keywords":["developer","engineer","remote","web3","gaming","blockchain","unity"]},
    {"name":"Decentraland",   "country":"🌍", "url":"https://boards.greenhouse.io/decentraland",
     "keywords":["developer","engineer","remote","web3","metaverse","blockchain","react"]},
    {"name":"Axie/Sky Mavis", "country":"🌍", "url":"https://boards.greenhouse.io/skymavis",
     "keywords":["developer","engineer","remote","web3","gaming","blockchain","python"]},

    # ── BLOCKCHAIN EXPLORERS ─────────────────────────────────
    {"name":"Etherscan",      "country":"🌍", "url":"https://etherscan.io/jobs",
     "keywords":["developer","engineer","remote","blockchain","ethereum","data","backend"]},
    {"name":"Blockchain.com", "country":"🇬🇧", "url":"https://blockchain.com/careers",
     "keywords":["python","developer","engineer","remote","blockchain","crypto","trading"]},

    # ── JERMAN 🇩🇪 ───────────────────────────────────────────
    {"name":"Trade Republic",  "country":"🇩🇪", "url":"https://traderepublic.com/careers",
     "keywords":["developer","python","trading","engineer","remote","fintech"]},
    {"name":"N26",             "country":"🇩🇪", "url":"https://n26.com/en-de/careers",
     "keywords":["developer","python","engineer","remote","fintech","backend"]},
    {"name":"Zalando Tech",    "country":"🇩🇪", "url":"https://jobs.zalando.com/en/jobs/",
     "keywords":["python","developer","engineer","remote","backend","trading"]},
    {"name":"Personio",        "country":"🇩🇪", "url":"https://www.personio.com/about-personio/careers/",
     "keywords":["python","developer","engineer","remote","backend","software"]},

    # ── GLOBAL CRYPTO ────────────────────────────────────────
    {"name":"Bybit",           "country":"🌏", "url":"https://careers.bybit.com/",
     "keywords":["python","developer","remote","trading","crypto","engineer","backend"]},
    {"name":"Kraken",          "country":"🇺🇸", "url":"https://jobs.lever.co/kraken",
     "keywords":["python","developer","remote","crypto","blockchain","trading","engineer"]},
    {"name":"Revolut",         "country":"🇬🇧", "url":"https://www.revolut.com/careers/",
     "keywords":["python","developer","remote","trading","fintech","engineer","backend"]},
]

def _make_id(company: str, title: str) -> str:
    return "cc_" + hashlib.md5(f"{company}:{title}".encode()).hexdigest()[:12]

def _extract_jobs(html: str, company: dict) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    jobs = []
    keywords = company["keywords"]

    selectors = [
        "a[href*='/job']", "a[href*='/jobs/']", "a[href*='/careers/']",
        "a[href*='/position']", "a[href*='/opening']", "a[href*='/posting']",
        ".job-listing a", ".position a", ".opening a", ".career-item a",
        "li.job a", "div.job a", "[data-job] a", "tr.job a",
    ]

    seen = set()
    for sel in selectors:
        for el in soup.select(sel):
            href = el.get("href","")
            text = el.get_text(" ", strip=True)
            if not text or len(text) < 5 or href in seen:
                continue
            seen.add(href)
            if not any(k in text.lower() for k in keywords):
                continue

            if href.startswith("http"):
                full_url = href
            elif href.startswith("/"):
                base = "/".join(company["url"].split("/")[:3])
                full_url = base + href
            else:
                full_url = company["url"] + "/" + href

            jobs.append({
                "source":  f"Career_{company['name']}",
                "id":      _make_id(company["name"], text),
                "title":   text[:100],
                "company": company["name"],
                "location": f"Remote {company['country']}",
                "tags":    " ".join(keywords),
                "description": f"Direct opening at {company['name']}",
                "url":     full_url,
                "email":   "", "date": ""
            })

    return jobs[:8]

def scrape_company_careers() -> list[dict]:
    all_jobs = []
    for company in COMPANY_CAREER_PAGES:
        try:
            time.sleep(REQUEST_DELAY_SEC)
            r = requests.get(company["url"], headers=HEADERS, timeout=15)
            r.raise_for_status()
            jobs = _extract_jobs(r.text, company)
            if jobs:
                print(f"    [{company['name']}] {len(jobs)} jobs")
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"    [{company['name']}] Error: {e}")
    return all_jobs
