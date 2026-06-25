# ============================================================
# config.py — Semua settings bot, isi sesuai kebutuhanmu
# ============================================================

import os

# ── Identitas Pelamar ────────────────────────────────────────
APPLICANT_NAME   = os.getenv("APPLICANT_NAME", "Dawam")
APPLICANT_EMAIL  = os.getenv("APPLICANT_EMAIL", "your@gmail.com")
CV_PATH          = os.getenv("CV_PATH", "cv.pdf")          # taruh cv.pdf di root folder

# ── Gmail (pakai App Password, bukan password biasa) ─────────
# Cara dapat App Password:
#   1. Google Account → Security → 2-Step Verification → App Passwords
#   2. Pilih "Mail" + "Other device" → generate → copy 16 karakter
GMAIL_USER       = os.getenv("GMAIL_USER", "your@gmail.com")
GMAIL_APP_PASS   = os.getenv("GMAIL_APP_PASS", "xxxx xxxx xxxx xxxx")

# ── Telegram ─────────────────────────────────────────────────
# Cara dapat TOKEN: chat @BotFather → /newbot
# Cara dapat CHAT_ID: chat @userinfobot setelah start botmu
TELEGRAM_TOKEN   = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ── Anthropic API (untuk generate cover letter) ──────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Filter Keywords ──────────────────────────────────────────
# Job akan di-score berdasarkan keyword ini
INCLUDE_KEYWORDS = [
    # Trading / Algo
    "mql4", "mql5", "metatrader", "mt4", "mt5", "expert advisor", "trading bot",
    "algorithmic trading", "quant", "pine script", "tradingview",
    # Python
    "python", "bot", "automation", "scraping",
    # Web3 / Crypto
    "web3", "solidity", "defi", "blockchain", "smart contract", "crypto",
    # General dev
    "react", "javascript", "typescript", "node",
    # Remote
    "remote", "freelance", "contract",
]

EXCLUDE_KEYWORDS = [
    "senior only", "10+ years", "us citizen only", "clearance required",
    "on-site", "onsite", "in-office",
]

# Minimum score untuk dianggap relevant (0-100)
MIN_SCORE = 30

# ── Scraper Settings ─────────────────────────────────────────
MAX_JOBS_PER_SOURCE = 50   # batas per run per sumber
REQUEST_DELAY_SEC   = 2    # jeda antar request (hindari rate limit)

# ── Email Settings ───────────────────────────────────────────
EMAIL_SUBJECT_TEMPLATE = "Application for {job_title} — {applicant_name}"
SEND_EMAILS = True          # set False untuk dry-run (hanya notif Telegram)
MAX_EMAILS_PER_RUN = 10     # batas kirim email per run

# ── Profil untuk AI Cover Letter ────────────────────────────
APPLICANT_PROFILE = """
Nama: Dawam
Lokasi: Surabaya, Indonesia
Pengalaman: 3+ tahun freelance developer

Skill utama:
- MQL4/MQL5: Expert Advisor development, custom indicator, backtesting
- Python: trading bot, automation, web scraping, API integration
- Pine Script: TradingView strategy & indicator development
- Web3/Blockchain: smart contract, DeFi, Solana ecosystem
- React: frontend development, dashboard, web app
- Tools: Git, GitHub Actions, VPS deployment (Ubuntu), Telegram Bot API

Proyek unggulan:
- Gold scalping EA (XAUUSD) dengan auto compound & risk management
- Automated job application bot dengan GitHub Actions
- DeFi LP agent untuk Meteora DLMM (Solana)
- Meme coin scanner dengan GeckoTerminal API
- Portfolio website (dark theme, gold/green accents)

Bahasa: Indonesia (native), Inggris (professional working)
Freelance platform: Upwork, Fiverr
Tipe kerja: remote, contract, part-time, full-time
"""
