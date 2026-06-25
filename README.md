# 🤖 Job Application Bot

Bot otomatis untuk apply kerja remote luar negeri.
Scrape 5 job board → filter by skill → AI cover letter → kirim email → notif Telegram.

---

## ⚡ Quick Setup

### 1. Clone & install

```bash
git clone https://github.com/USERNAME/job-bot.git
cd job-bot
pip install -r requirements.txt
```

### 2. Siapkan Gmail App Password

1. Buka: https://myaccount.google.com/security
2. Pastikan **2-Step Verification** aktif
3. Cari **App Passwords** → buat baru → pilih "Mail" + "Other"
4. Copy 16 karakter yang muncul

### 3. Siapkan Telegram Bot

```
1. Chat @BotFather di Telegram
2. /newbot → ikuti instruksi → copy TOKEN
3. Start bot kamu, lalu chat @userinfobot → copy CHAT_ID
```

### 4. Set environment variables

**Lokal** — buat file `.env` (jangan di-commit!):
```bash
export APPLICANT_NAME="Dawam"
export APPLICANT_EMAIL="your@gmail.com"
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASS="xxxx xxxx xxxx xxxx"
export TELEGRAM_TOKEN="123456:ABCdef..."
export TELEGRAM_CHAT_ID="123456789"
export ANTHROPIC_API_KEY="sk-ant-..."
export CV_PATH="cv.pdf"
```

**GitHub Actions** — buka repo → Settings → Secrets and variables → Actions → New secret:
- `APPLICANT_NAME`
- `APPLICANT_EMAIL`
- `GMAIL_USER`
- `GMAIL_APP_PASS`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- `ANTHROPIC_API_KEY`
- `CV_BASE64` → isi dengan: `base64 cv.pdf` (output terminal)

### 5. Upload CV

Taruh `cv.pdf` di root folder (tidak akan ter-commit karena ada di .gitignore).

Untuk GitHub Actions, convert dulu:
```bash
base64 cv.pdf | tr -d '\n'   # copy output → isi secret CV_BASE64
```

---

## 🚀 Cara Menjalankan

```bash
# Test dulu — tidak kirim email
python main.py --dry-run

# Run normal
python main.py

# Lihat dashboard status lamaran
python main.py --dashboard
```

---

## ⚙️ Konfigurasi

Edit `config.py`:
- `INCLUDE_KEYWORDS` — tambah/hapus keyword skill
- `MIN_SCORE` — threshold relevance (default 30)
- `MAX_EMAILS_PER_RUN` — batas email per run (default 10)
- `SEND_EMAILS` — set `False` untuk dry-run permanen

---

## 📊 Job Sources

| Source | API Type | Email tersedia? |
|--------|----------|-----------------|
| RemoteOK | Public JSON | ✅ Kadang |
| We Work Remotely | JSON search | ❌ |
| Remotive | Public API | ❌ |
| Himalayas | Public API | ❌ |
| Arbeitnow | Public JSON | ❌ |

> Job tanpa email disimpan sebagai `link_only` — perlu apply manual via link.

---

## 🔄 GitHub Actions Schedule

Bot otomatis jalan 3x sehari (08:00, 13:00, 18:00 WIB).
Bisa juga trigger manual: Actions tab → Run workflow.
