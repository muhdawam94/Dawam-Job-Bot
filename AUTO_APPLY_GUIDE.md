# 🤖 Auto-Apply Feature - Panduan Lengkap

## 🎉 Apa yang Baru?

Bot sekarang **otomatis apply** ke lowongan kerja! Tidak perlu lagi isi form manual satu-satu.

### Fitur Baru:
✅ **Auto-fill form** untuk 9+ platform ATS populer
✅ **Upload CV otomatis**
✅ **Insert cover letter** yang sudah di-generate AI
✅ **Submit application** otomatis
✅ **Notifikasi Telegram** real-time tentang status apply
✅ **Track semua aplikasi** di database
✅ **Generic form filler** untuk website company yang tidak dikenal

---

## 🎯 Platform yang Didukung

### Major ATS Platforms (90% startup/perusahaan pakai ini):
1. **Greenhouse** (`greenhouse.io`) - Coinbase, Stripe, Airbnb, dll
2. **Lever** (`lever.co`) - Consensys, many Web3 companies
3. **Ashby** (`ashbyhq.com`) - Popular di Web3 ecosystem
4. **Workday** (`myworkdayjobs.com`) - Enterprise companies
5. **SmartRecruiters** (`smartrecruiters.com`) - Binance, dll

### Startup & Web3:
6. **Wellfound** (formerly AngelList) (`wellfound.com`, `angel.co`)
7. **BambooHR** (`bamboohr.com`)
8. **BreezyHR** (`breezy.hr`)

### Generic Support:
9. **Web3 job boards** - web3.career, crypto.jobs, cryptojobslist
10. **German freelance** - freelance.de, gulp.de, freelancermap, malt.de
11. **Company career pages** - any URL dengan `/jobs/`, `/careers/`, `/apply`

---

## 🚀 Cara Pakai

### 1. Setup Awal (sekali aja)

```bash
cd Dawam-Job-Bot

# Install dependencies
pip install -r requirements.txt

# Setup ChromeDriver
python form_filler/setup_driver.py
```

**PENTING:** Pastikan Google Chrome sudah terinstall!

### 2. Update Data Pribadi

Edit file `form_filler/auto_apply.py` baris 18-32:

```python
APPLICANT = {
    "first_name": "Muhammad",        # ← Ganti
    "last_name":  "Dawam",           # ← Ganti
    "full_name":  "Muhammad Dawam",  # ← Ganti
    "email":      "your@email.com",  # ← Ganti
    "phone":      "+6281231859894",  # ← Ganti nomor HP kamu!
    "location":   "Surabaya, Indonesia",
    "linkedin":   "https://linkedin.com/in/muhdawam94",  # ← Ganti
    "github":     "https://github.com/muhdawam94",       # ← Ganti
    "portfolio":  "https://your-portfolio.com",           # ← Ganti
    "cv_path":    CV_PATH,  # Baca dari config.py
    ...
}
```

### 3. Pastikan CV Ada

Taruh file `cv.pdf` di root folder bot (atau sesuai path di `config.py`).

```bash
# Check apakah CV ada
ls cv.pdf
```

### 4. Set Environment Variables

Tambahkan/update di `.env` atau environment:

```bash
# Yang sudah ada
export APPLICANT_EMAIL="your@gmail.com"
export TELEGRAM_TOKEN="123456:ABCdef..."
export TELEGRAM_CHAT_ID="805652229"  # ID kamu
export GROQ_API_KEY="gsk-..."        # Untuk AI cover letter
export CV_PATH="cv.pdf"

# Optional: Gmail (untuk fallback email apply)
export GMAIL_USER="your@gmail.com"
export GMAIL_APP_PASS="xxxx xxxx xxxx xxxx"
```

**Cara dapat Groq API Key (GRATIS):**
1. Buka https://console.groq.com
2. Sign up / login
3. API Keys → Create new
4. Copy key → save di `.env`

---

## 🏃 Menjalankan Bot

### Test Mode (dry-run):
```bash
python main.py --dry-run
```
Ini akan scrape jobs dan generate cover letters, tapi **TIDAK** apply apapun. Bagus untuk testing.

### Production Mode (real auto-apply):
```bash
python main.py
```

Bot akan:
1. 🔍 Scrape 10+ job boards
2. ✅ Filter berdasarkan keywords
3. 🤖 Generate cover letter dengan AI
4. 📱 Kirim notifikasi Telegram
5. **🚀 OTOMATIS APPLY** ke semua job yang platformnya didukung
6. 📊 Save hasil ke database

### Lihat Dashboard:
```bash
python main.py --dashboard
```
Lihat semua jobs yang sudah di-track dan status aplikasi.

---

## 📊 Cara Kerja Auto-Apply

### Flow Diagram:
```
Job Ditemukan
    ↓
Filter by Keywords
    ↓
Generate Cover Letter (AI)
    ↓
Kirim Notif Telegram
    ↓
Detect Platform dari URL ← AUTO-APPLY DIMULAI DI SINI
    ↓
┌─────────────────────────────────────┐
│ Platform Dikenal?                   │
├─────────────────────────────────────┤
│ YES → Open browser (headless)       │
│       → Fill form fields            │
│       → Upload CV                   │
│       → Insert cover letter         │
│       → Click Submit                │
│       → ✅ Notif sukses             │
│                                     │
│ NO  → Skip auto-apply               │
│       → User apply manual           │
└─────────────────────────────────────┘
    ↓
Save Status ke Database
```

### Platform Detection:
Bot otomatis detect platform dari URL:

```python
# Contoh:
"https://boards.greenhouse.io/company/jobs/123"
→ Detected: greenhouse → apply_greenhouse()

"https://jobs.lever.co/company/abc"
→ Detected: lever → apply_lever()

"https://company.com/careers/job-123"
→ Detected: generic → apply_generic()

"https://linkedin.com/jobs/view/123"
→ Detected: unknown → Skip (notif ke user untuk manual apply)
```

---

## 📱 Notifikasi Telegram

Kamu akan dapat notifikasi untuk setiap job:

### 1. Job Baru Ditemukan:
```
🔔 JOB BARU
━━━━━━━━━━━━━━━━━━
💼 Senior Python Developer
🏢 Polygon Labs
📍 Remote
📊 Match: ⭐⭐⭐⭐ (75/100)
🔗 BUKA & APPLY ↗
━━━━━━━━━━━━━━━━━━
📝 COVER LETTER SIAP PAKAI:
[cover letter text...]
```

### 2. Auto-Apply Berhasil:
```
🤖✅ AUTO-APPLY BERHASIL!
━━━━━━━━━━━━━━━━━━
💼 Senior Python Developer
🏢 Polygon Labs
🔧 Platform: GREENHOUSE
🔗 Cek Status ↗
━━━━━━━━━━━━━━━━━━
✨ Form otomatis terisi & submitted!
```

### 3. Auto-Apply Perlu Manual:
```
🤖⚠️ AUTO-APPLY PERLU CEK MANUAL
━━━━━━━━━━━━━━━━━━
💼 Senior Python Developer
🏢 Some Company
🔧 Platform: generic
❌ Error: Submit button not found
🔗 Apply Manual ↗
━━━━━━━━━━━━━━━━━━
💡 Buka link dan apply manual ya!
```

---

## 📁 Database Schema

File: `data/jobs.db` (SQLite)

Kolom baru yang ditambahkan:
- `auto_apply_status` - "success" / "failed" / NULL
- `auto_apply_platform` - Platform yang digunakan
- `auto_apply_error` - Error message jika gagal

Query contoh:
```sql
-- Lihat semua yang sukses auto-apply
SELECT title, company, auto_apply_platform 
FROM jobs 
WHERE auto_apply_status = 'success';

-- Lihat yang gagal
SELECT title, company, auto_apply_error 
FROM jobs 
WHERE auto_apply_status = 'failed';
```

---

## ⚙️ Konfigurasi

### Edit `config.py`:

```python
# Keywords untuk filter jobs (tambah/kurangi sesuai kebutuhan)
INCLUDE_KEYWORDS = [
    "mql4", "mql5", "python", "web3", "solidity",
    "react", "javascript", "remote", "freelance",
]

# Minimum relevance score (0-100)
MIN_SCORE = 25  # Lower = lebih banyak jobs

# Limits
MAX_JOBS_PER_SOURCE = 50
MAX_EMAILS_PER_RUN = 10  # Untuk fallback email apply
```

---

## 🧪 Testing Auto-Apply Manual

Kamu bisa test auto-apply untuk satu job URL:

```bash
python form_filler/auto_apply.py "https://boards.greenhouse.io/company/jobs/123"
```

Ini akan:
1. Detect platform
2. Open browser (non-headless - kamu bisa lihat)
3. Fill form
4. Upload CV
5. Try submit

Bagus untuk debug atau lihat gimana bot kerja!

---

## 🐛 Troubleshooting

### "ChromeDriver not found"
```bash
python form_filler/setup_driver.py
```

### "Chrome binary not found"
Install Google Chrome dari https://www.google.com/chrome/

### Auto-apply gagal terus
1. Check apakah CV path benar: `ls cv.pdf`
2. Check APPLICANT data di `auto_apply.py` sudah lengkap
3. Test manual: `python form_filler/auto_apply.py <URL>`
4. Lihat error di console output

### Form tidak terisi lengkap
Ini normal untuk generic forms. Bot akan:
- Isi sebanyak mungkin fields
- Notif ke Telegram kalau perlu manual check
- Kamu tinggal buka link, complete form, submit

### Rate limiting / too many requests
Tambahkan delay di `config.py`:
```python
REQUEST_DELAY_SEC = 3  # Naikan dari 2 ke 3-5 detik
```

---

## 🔄 GitHub Actions (Automation)

Bot sudah support auto-run via GitHub Actions (3x sehari).

File: `.github/workflows/job-bot.yml`

Secrets yang perlu di-set (GitHub repo → Settings → Secrets):
- `APPLICANT_EMAIL`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GROQ_API_KEY`
- `CV_BASE64` (base64 encode CV kamu)
- (Optional) `GMAIL_USER`, `GMAIL_APP_PASS`

---

## 📈 Best Practices

### 1. Mulai dengan Dry Run
```bash
python main.py --dry-run
```
Lihat dulu jobs apa yang ditemukan sebelum real apply.

### 2. Monitor Telegram
Setiap auto-apply akan dapat notif. Check apakah yang sukses atau gagal.

### 3. Check Dashboard Regular
```bash
python main.py --dashboard
```
Lihat stats: berapa total jobs, berapa yang udah di-apply.

### 4. Manual Check untuk Platform Generic
Kalau platform = "generic", bot coba best-effort tapi mungkin perlu manual check.

### 5. Update CV Regular
Pastikan `cv.pdf` selalu up-to-date.

---

## 📊 Stats & Monitoring

Setelah run, bot akan output:

```
✅ SELESAI | New: 15 | Applied: 12 (Auto: 10)
   DB Total: 150 | Total Applied: 45
```

- **New** = Job baru yang ditemukan
- **Applied** = Total yang berhasil apply (auto + email)
- **Auto** = Yang berhasil auto-apply via form filler
- **DB Total** = Total jobs di database
- **Total Applied** = Total aplikasi sepanjang waktu

---

## 🎯 Strategi untuk Web3 & German Jobs

### Web3 Jobs:
Bot sudah scrape dari:
- Web3 job boards (web3.career, crypto.jobs)
- Greenhouse/Lever/Ashby (banyak Web3 companies pakai)
- Company career pages (Polygon, Chainlink, dll)

Keywords di `config.py`:
```python
"web3", "solidity", "defi", "blockchain", "smart contract", "crypto"
```

### German Freelance:
Bot sudah scrape dari:
- FreelancerMap 🇩🇪
- Malt 🇩🇪
- Gulp.de, Freelance.de (via generic form filler)

Keywords German:
```python
"remote", "freelance", "contract"
```

Generic form filler support German field names:
- `vorname` (first name)
- `nachname` (last name)
- `telefon` (phone)
- `anschreiben` (cover letter)
- `Bewerben` button (apply)

---

## 🔐 Security & Privacy

- ✅ CV tidak pernah di-upload ke cloud (kecuali ke job application forms)
- ✅ Credentials disimpan di environment variables (tidak di-commit)
- ✅ Database lokal (SQLite) di folder `data/`
- ✅ Bot jalan headless (tidak buka window kecuali debug)
- ✅ Groq API untuk AI cover letter (gratis, private)

---

## 🚀 Future Enhancements (Ideas)

- [ ] AI-powered form detection (GPT-4 Vision to "see" forms)
- [ ] Puppeteer support (alternative to Selenium)
- [ ] Multi-account support (apply dengan beda profiles)
- [ ] Job quality scoring (ML model untuk rank jobs)
- [ ] Application tracking page (web dashboard)
- [ ] Interview scheduling integration

---

## 💬 Support

Issues / questions:
1. Check Telegram notifikasi - biasanya ada hint error
2. Run dengan `--dry-run` untuk debug
3. Test manual apply: `python form_filler/auto_apply.py <URL>`
4. Check console output untuk detailed logs

---

## 🎉 Summary

Sekarang bot kamu:
1. ✅ Scrape 10+ job boards (Web3 + German included)
2. ✅ Filter by skills & relevance
3. ✅ Generate AI cover letters
4. ✅ **AUTO-APPLY to 9+ platforms**
5. ✅ Track everything in database
6. ✅ Real-time Telegram notifications
7. ✅ Generic fallback for unknown sites

**Next step:** Run `python main.py --dry-run` untuk test!

Good luck dengan job hunting! 🚀
