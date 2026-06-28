#!/usr/bin/env python3
# form_filler/auto_apply.py
# Auto isi & submit form lamaran di Greenhouse, Lever, Workday
# Platform ini dipakai 80% perusahaan tech global

import time, os, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# ── Import config & cover letter generator ───────────────────
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APPLICANT_NAME, APPLICANT_EMAIL, CV_PATH, GROQ_API_KEY
from core.cover_letter import generate as gen_cover

# ── Data pelamar — isi sesuai profil kamu ────────────────────
APPLICANT = {
    "first_name":  "Dawam",
    "last_name":   "Muhdawam",
    "full_name":   "Muhammad Dawam",
    "email":       APPLICANT_EMAIL,
    "phone":       "+6281231859894",   # ganti dengan nomor kamu
    "location":    "Surabaya, Indonesia",
    "linkedin":    "https://linkedin.com/in/muhdawam94",
    "github":      "https://github.com/muhdawam94",
    "portfolio":   "https://muhdawam94.github.io",
    "cv_path":     CV_PATH,

    # Jawaban standar pertanyaan umum
    "years_exp":   "3",
    "salary_exp":  "negotiable",
    "start_date":  "immediately",
    "authorized":  "yes",             # work authorization
    "visa":        "no",              # need visa sponsorship
    "remote":      "yes",             # willing to work remote
    "relocate":    "no",              # willing to relocate
}

def _driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120")
    return webdriver.Chrome(options=opts)

def _wait_and_fill(driver, selector, value, by=By.CSS_SELECTOR, timeout=5):
    try:
        el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector)))
        el.clear()
        el.send_keys(value)
        return True
    except:
        return False

def _try_selectors(driver, selectors, value):
    """Coba beberapa selector sampai berhasil."""
    for sel in selectors:
        if _wait_and_fill(driver, sel, value, timeout=3):
            return True
    return False

def _upload_cv(driver, input_selector):
    try:
        el = driver.find_element(By.CSS_SELECTOR, input_selector)
        el.send_keys(os.path.abspath(APPLICANT["cv_path"]))
        time.sleep(1)
        return True
    except:
        return False

# ══════════════════════════════════════════════════════════════
# GREENHOUSE — dipakai oleh: Figma, Notion, Linear, dll
# ══════════════════════════════════════════════════════════════
def apply_greenhouse(job_url: str, cover_letter: str) -> bool:
    print(f"[Greenhouse] Applying: {job_url}")
    driver = _driver()
    try:
        driver.get(job_url)
        time.sleep(2)

        # Isi form
        _try_selectors(driver, ["#first_name", "input[name='first_name']"], APPLICANT["first_name"])
        _try_selectors(driver, ["#last_name",  "input[name='last_name']"],  APPLICANT["last_name"])
        _try_selectors(driver, ["#email",       "input[name='email']"],      APPLICANT["email"])
        _try_selectors(driver, ["#phone",       "input[name='phone']"],      APPLICANT["phone"])

        # Upload CV
        _upload_cv(driver, "input[type='file']")

        # Cover letter
        _try_selectors(driver, [
            "textarea[name='cover_letter']",
            "#cover_letter",
            "textarea.cover-letter"
        ], cover_letter)

        # LinkedIn
        _try_selectors(driver, [
            "input[name='job_application[answers_attributes][0][text_value]']",
            "input[placeholder*='LinkedIn']",
            "input[id*='linkedin']"
        ], APPLICANT["linkedin"])

        # Submit
        time.sleep(1)
        try:
            btn = driver.find_element(By.CSS_SELECTOR, "input[type='submit'], button[type='submit']")
            btn.click()
            time.sleep(3)
            print(f"[Greenhouse] ✅ Submitted!")
            return True
        except:
            print(f"[Greenhouse] ⚠️ Submit button not found")
            return False

    except Exception as e:
        print(f"[Greenhouse] ✗ Error: {e}")
        return False
    finally:
        driver.quit()


# ══════════════════════════════════════════════════════════════
# LEVER — dipakai oleh: Coinbase, Cloudflare, dll
# ══════════════════════════════════════════════════════════════
def apply_lever(job_url: str, cover_letter: str) -> bool:
    print(f"[Lever] Applying: {job_url}")
    driver = _driver()
    try:
        # Lever apply URL biasanya: jobs.lever.co/company/id/apply
        apply_url = job_url if "/apply" in job_url else job_url + "/apply"
        driver.get(apply_url)
        time.sleep(2)

        _try_selectors(driver, ["input[name='name']",  "#name"],  APPLICANT["full_name"])
        _try_selectors(driver, ["input[name='email']", "#email"], APPLICANT["email"])
        _try_selectors(driver, ["input[name='phone']", "#phone"], APPLICANT["phone"])
        _try_selectors(driver, ["input[name='org']",   "#org"],   "Freelance Developer")

        # Cover letter / comments
        _try_selectors(driver, [
            "textarea[name='comments']",
            "textarea[name='cover_letter']",
            "#comments"
        ], cover_letter)

        # LinkedIn & URLs
        _try_selectors(driver, ["input[name='urls[LinkedIn]']", "input[placeholder*='LinkedIn']"], APPLICANT["linkedin"])
        _try_selectors(driver, ["input[name='urls[GitHub]']",   "input[placeholder*='GitHub']"],   APPLICANT["github"])

        # Upload CV
        _upload_cv(driver, "input[type='file']")
        time.sleep(1)

        # Submit
        try:
            btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit'], .template-btn-submit")
            btn.click()
            time.sleep(3)
            print(f"[Lever] ✅ Submitted!")
            return True
        except:
            print(f"[Lever] ⚠️ Submit button not found")
            return False

    except Exception as e:
        print(f"[Lever] ✗ Error: {e}")
        return False
    finally:
        driver.quit()


# ══════════════════════════════════════════════════════════════
# WORKDAY — dipakai oleh: perusahaan besar Jerman & Fortune 500
# ══════════════════════════════════════════════════════════════
def apply_workday(job_url: str, cover_letter: str) -> bool:
    print(f"[Workday] Applying: {job_url}")
    driver = _driver(headless=False)  # Workday perlu non-headless
    try:
        driver.get(job_url)
        time.sleep(3)

        # Klik Apply button
        try:
            apply_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR,
                    "a[data-automation-id='jobPostingApplyButton'], button[aria-label*='Apply']"))
            )
            apply_btn.click()
            time.sleep(3)
        except:
            print("[Workday] Apply button not found, trying direct form")

        # Isi form — Workday pakai data-automation-id
        selectors = {
            "[data-automation-id='legalNameSection_firstName']": APPLICANT["first_name"],
            "[data-automation-id='legalNameSection_lastName']":  APPLICANT["last_name"],
            "[data-automation-id='email']":                      APPLICANT["email"],
            "[data-automation-id='phone-number']":               APPLICANT["phone"],
        }
        for sel, val in selectors.items():
            _wait_and_fill(driver, sel, val, timeout=5)

        # Upload CV
        try:
            upload = driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            upload.send_keys(os.path.abspath(APPLICANT["cv_path"]))
            time.sleep(2)
        except:
            pass

        print(f"[Workday] ⚠️ Workday butuh interaksi manual untuk submit")
        print(f"[Workday] Browser terbuka — selesaikan submit secara manual")
        time.sleep(30)  # Beri waktu 30 detik untuk submit manual
        return True

    except Exception as e:
        print(f"[Workday] ✗ Error: {e}")
        return False
    finally:
        driver.quit()


# ══════════════════════════════════════════════════════════════
# MAIN DISPATCHER — deteksi platform otomatis
# ══════════════════════════════════════════════════════════════
def detect_platform(url: str) -> str:
    url_lower = url.lower()
    if "greenhouse.io"  in url_lower: return "greenhouse"
    if "lever.co"       in url_lower: return "lever"
    if "myworkdayjobs" in url_lower: return "workday"
    if "workday.com"   in url_lower: return "workday"
    return "unknown"

def auto_apply(job: dict) -> bool:
    """
    Main function — deteksi platform, generate cover letter, submit form.
    Dipanggil dari main.py atau Telegram bot handler.
    """
    url      = job.get("url", "")
    platform = detect_platform(url)
    cover    = gen_cover(job)

    print(f"\n[AutoApply] {job.get('title','')} @ {job.get('company','')}")
    print(f"[AutoApply] Platform: {platform} | URL: {url[:60]}")

    if platform == "greenhouse":
        return apply_greenhouse(url, cover)
    elif platform == "lever":
        return apply_lever(url, cover)
    elif platform == "workday":
        return apply_workday(url, cover)
    else:
        print(f"[AutoApply] Platform tidak dikenal — perlu apply manual")
        print(f"[AutoApply] Cover letter sudah di-generate:\n{cover[:200]}...")
        return False


# ── Test langsung dari command line ──────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python form_filler/auto_apply.py <job_url>")
        print("Contoh: python form_filler/auto_apply.py https://boards.greenhouse.io/company/jobs/123")
        sys.exit(1)

    test_job = {
        "title":   "Python Developer",
        "company": "Test Company",
        "url":     sys.argv[1],
        "tags":    "python remote",
        "description": "Python developer role"
    }
    result = auto_apply(test_job)
    print(f"\nResult: {'✅ Success' if result else '❌ Failed/Manual needed'}")
