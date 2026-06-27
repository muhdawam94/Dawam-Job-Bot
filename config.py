# config.py — UPDATE: ganti ANTHROPIC_API_KEY → GROQ_API_KEY
import os

APPLICANT_NAME   = os.getenv("APPLICANT_NAME", "Dawam")
APPLICANT_EMAIL  = os.getenv("APPLICANT_EMAIL", "your@gmail.com")
CV_PATH          = os.getenv("CV_PATH", "cv.pdf")

GMAIL_USER       = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASS   = os.getenv("GMAIL_APP_PASS", "")

TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Ganti dari Anthropic ke Groq (GRATIS) ───────────────────
GROQ_API_KEY     = os.getenv("GROQ_API_KEY", "")

INCLUDE_KEYWORDS = [
    "mql4", "mql5", "metatrader", "mt4", "mt5", "expert advisor", "trading bot",
    "algorithmic trading", "quant", "pine script", "tradingview",
    "python", "bot", "automation", "scraping",
    "web3", "solidity", "defi", "blockchain", "smart contract", "crypto",
    "react", "javascript", "typescript", "node",
    "remote", "freelance", "contract",
]

EXCLUDE_KEYWORDS = [
    "senior only", "10+ years", "us citizen only", "clearance required",
    "on-site", "onsite", "in-office", "requires german", "deutsch erforderlich",
]

MIN_SCORE            = 25   # diturunkan agar lebih banyak job tertangkap
MAX_JOBS_PER_SOURCE  = 50
REQUEST_DELAY_SEC    = 2
EMAIL_SUBJECT_TEMPLATE = "Application for {job_title} — {applicant_name}"
SEND_EMAILS          = True
MAX_EMAILS_PER_RUN   = 10

APPLICANT_PROFILE = """
Name: Dawam
Location: Surabaya, Indonesia (UTC+7)
Experience: 3+ years freelance developer

Core Skills:
- MQL4/MQL5: Expert Advisor development, custom indicators, backtesting, XAUUSD scalping
- Python: trading bots, automation, web scraping, API integration, GitHub Actions
- Pine Script: TradingView strategy & indicator development
- Web3/Blockchain: smart contracts, DeFi, Solana/Meteora ecosystem
- React: frontend development, dashboard, web apps
- Tools: Git, VPS deployment (Ubuntu), Telegram Bot API, SQLite

Notable Projects:
- Gold scalping EA (XAUUSD) with auto-compound & risk management (MQL5)
- Automated job application bot using GitHub Actions + AI cover letters
- DeFi LP agent for Meteora DLMM (Solana)
- Meme coin scanner with GeckoTerminal API (React)
- Multiple trading dashboards and portfolio websites

Languages: Indonesian (native), English (professional working)
Platforms: Upwork, Fiverr
Work type: remote, contract, part-time, full-time
Timezone: UTC+7 (flexible for US/EU overlap)
"""
