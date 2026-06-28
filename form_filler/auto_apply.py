#!/usr/bin/env python3
# form_filler/auto_apply.py v2
# Support: Greenhouse, Lever, Workday, Ashby, SmartRecruiters

import time, os, sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import APPLICANT_EMAIL, CV_PATH
from core.cover_letter import generate as gen_cover

APPLICANT = {
    "first_name": "Muhammad",
    "last_name":  "Dawam",
    "full_name":  "Muhammad Dawam",
    "email":      APPLICANT_EMAIL,
    "phone":      "+6281231859894",    # ← GANTI nomor HP kamu
    "location":   "Surabaya, Indonesia",
    "linkedin":   "https://linkedin.com/in/muhdawam94",
    "github":     "https://github.com/muhdawam94",
    "portfolio":  "https://github.com/muhdawam94",
    "cv_path":    CV_PATH,
    "years_exp":  "3",
    "remote":     "yes",
    "visa":       "no",
}

def _driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=opts)
    except:
        return webdriver.Chrome(options=opts)

def _fill(driver, selector, value, by=By.CSS_SELECTOR, timeout=5):
    try:
        el = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector)))
        el.clear()
        el.send_keys(value)
        return True
    except:
        return False

def _try_fill(driver, selectors, value):
    for s in selectors:
        if _fill(driver, s, value, timeout=3):
            return True
    return False

def _upload(driver, value):
    for s in ["input[type='file']", "input[accept*='pdf']", "input[name*='resume']"]:
        try:
            el = driver.find_element(By.CSS_SELECTOR, s)
            el.send_keys(os.path.abspath(value))
            time.sleep(1)
            return True
        except:
            continue
    return False

def _click(driver, selectors, timeout=5):
    for s in selectors:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, s)))
            el.click()
            return True
        except:
            continue
    return False

# ── GREENHOUSE ───────────────────────────────────────────────
def apply_greenhouse(url: str, cover: str) -> dict:
    print(f"[Greenhouse] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "greenhouse", "url": url}
    try:
        driver.get(url)
        time.sleep(2)

        filled = 0
        if _try_fill(driver, ["#first_name", "input[name='first_name']", "input[id*='first']"], APPLICANT["first_name"]): filled += 1
        if _try_fill(driver, ["#last_name",  "input[name='last_name']",  "input[id*='last']"],  APPLICANT["last_name"]):  filled += 1
        if _try_fill(driver, ["#email",       "input[name='email']",      "input[type='email']"], APPLICANT["email"]):    filled += 1
        if _try_fill(driver, ["#phone",       "input[name='phone']",      "input[type='tel']"],   APPLICANT["phone"]):    filled += 1

        _upload(driver, APPLICANT["cv_path"])

        _try_fill(driver, [
            "textarea[name='cover_letter']", "#cover_letter",
            "textarea[id*='cover']", "textarea[placeholder*='cover']"
        ], cover)

        _try_fill(driver, [
            "input[placeholder*='LinkedIn']", "input[id*='linkedin']",
            "input[name*='linkedin']"
        ], APPLICANT["linkedin"])

        time.sleep(1)
        submitted = _click(driver, [
            "input[type='submit']", "button[type='submit']",
            ".submit-app", "#submit_app", "button[data-qa='btn-submit']"
        ])

        if submitted:
            time.sleep(2)
            print(f"[Greenhouse] ✅ Submitted! Fields filled: {filled}")
            result["success"] = True
        else:
            print(f"[Greenhouse] ⚠️ Fields filled: {filled}, submit manual diperlukan")

    except Exception as e:
        print(f"[Greenhouse] ✗ {e}")
    finally:
        driver.quit()
    return result

# ── LEVER ────────────────────────────────────────────────────
def apply_lever(url: str, cover: str) -> dict:
    apply_url = url if "/apply" in url else url + "/apply"
    print(f"[Lever] {apply_url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "lever", "url": url}
    try:
        driver.get(apply_url)
        time.sleep(2)

        filled = 0
        if _try_fill(driver, ["input[name='name']",  "#name"],  APPLICANT["full_name"]): filled += 1
        if _try_fill(driver, ["input[name='email']", "#email"], APPLICANT["email"]):     filled += 1
        if _try_fill(driver, ["input[name='phone']", "#phone"], APPLICANT["phone"]):     filled += 1
        if _try_fill(driver, ["input[name='org']",   "#org"],   "Freelance Developer"): filled += 1

        _try_fill(driver, [
            "textarea[name='comments']", "textarea[name='cover_letter']",
            "#additional-information", "textarea[placeholder*='tell us']"
        ], cover)

        _try_fill(driver, ["input[name='urls[LinkedIn]']", "input[placeholder*='LinkedIn']"], APPLICANT["linkedin"])
        _try_fill(driver, ["input[name='urls[GitHub]']",   "input[placeholder*='GitHub']"],   APPLICANT["github"])
        _try_fill(driver, ["input[name='urls[Portfolio]']", "input[placeholder*='Portfolio']"], APPLICANT["portfolio"])

        _upload(driver, APPLICANT["cv_path"])
        time.sleep(1)

        submitted = _click(driver, [
            "button[type='submit']", ".template-btn-submit",
            "button[data-qa='btn-apply']", "#btn-submit"
        ])

        if submitted:
            time.sleep(2)
            print(f"[Lever] ✅ Submitted! Fields: {filled}")
            result["success"] = True
        else:
            print(f"[Lever] ⚠️ Fields: {filled}, submit manual diperlukan")

    except Exception as e:
        print(f"[Lever] ✗ {e}")
    finally:
        driver.quit()
    return result

# ── ASHBY (dipakai banyak startup Web3) ─────────────────────
def apply_ashby(url: str, cover: str) -> dict:
    print(f"[Ashby] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "ashby", "url": url}
    try:
        driver.get(url)
        time.sleep(2)

        _try_fill(driver, ["input[name='_systemfield_name']", "input[placeholder*='Full name']", "input[placeholder*='Name']"], APPLICANT["full_name"])
        _try_fill(driver, ["input[name='_systemfield_email']", "input[type='email']"], APPLICANT["email"])
        _try_fill(driver, ["input[name='_systemfield_phone']", "input[type='tel']"],   APPLICANT["phone"])
        _try_fill(driver, ["textarea[placeholder*='cover']", "textarea[name*='cover']"], cover)
        _try_fill(driver, ["input[placeholder*='LinkedIn']"], APPLICANT["linkedin"])

        _upload(driver, APPLICANT["cv_path"])
        time.sleep(1)

        submitted = _click(driver, ["button[type='submit']", "button[data-testid='submit']"])
        if submitted:
            time.sleep(2)
            print(f"[Ashby] ✅ Submitted!")
            result["success"] = True
        else:
            print(f"[Ashby] ⚠️ Submit manual diperlukan")

    except Exception as e:
        print(f"[Ashby] ✗ {e}")
    finally:
        driver.quit()
    return result

# ── WORKDAY ──────────────────────────────────────────────────
def apply_workday(url: str, cover: str) -> dict:
    print(f"[Workday] {url[:70]}")
    driver = _driver(headless=False)  # Workday perlu non-headless
    result = {"success": False, "platform": "workday", "url": url}
    try:
        driver.get(url)
        time.sleep(3)

        try:
            btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((
                By.CSS_SELECTOR,
                "a[data-automation-id='jobPostingApplyButton'], button[aria-label*='Apply']"
            )))
            btn.click()
            time.sleep(3)
        except:
            pass

        _fill(driver, "[data-automation-id='legalNameSection_firstName']", APPLICANT["first_name"])
        _fill(driver, "[data-automation-id='legalNameSection_lastName']",  APPLICANT["last_name"])
        _fill(driver, "[data-automation-id='email']",                      APPLICANT["email"])
        _fill(driver, "[data-automation-id='phone-number']",               APPLICANT["phone"])
        _upload(driver, APPLICANT["cv_path"])

        print(f"[Workday] Data sudah diisi — browser terbuka 45 detik untuk submit manual")
        time.sleep(45)
        result["success"] = True

    except Exception as e:
        print(f"[Workday] ✗ {e}")
    finally:
        driver.quit()
    return result

# ── SMARTRECRUITERS ──────────────────────────────────────────
def apply_smartrecruiters(url: str, cover: str) -> dict:
    print(f"[SmartRecruiters] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "smartrecruiters", "url": url}
    try:
        driver.get(url)
        time.sleep(2)

        _try_fill(driver, ["input[name='firstName']", "#firstName"], APPLICANT["first_name"])
        _try_fill(driver, ["input[name='lastName']",  "#lastName"],  APPLICANT["last_name"])
        _try_fill(driver, ["input[name='email']",     "#email"],     APPLICANT["email"])
        _try_fill(driver, ["input[name='phone']",     "#phone"],     APPLICANT["phone"])

        _upload(driver, APPLICANT["cv_path"])
        time.sleep(1)

        submitted = _click(driver, ["button[data-ui='btn-primary']", "button[type='submit']"])
        if submitted:
            time.sleep(2)
            print(f"[SmartRecruiters] ✅ Submitted!")
            result["success"] = True

    except Exception as e:
        print(f"[SmartRecruiters] ✗ {e}")
    finally:
        driver.quit()
    return result

# ══════════════════════════════════════════════════════════════
# DISPATCHER — deteksi platform otomatis dari URL
# ══════════════════════════════════════════════════════════════
def detect_platform(url: str) -> str:
    u = url.lower()
    if "greenhouse.io"       in u: return "greenhouse"
    if "lever.co"            in u: return "lever"
    if "myworkdayjobs"       in u: return "workday"
    if "workday.com"         in u: return "workday"
    if "ashbyhq.com"         in u: return "ashby"
    if "smartrecruiters.com" in u: return "smartrecruiters"
    return "unknown"

def auto_apply(job: dict) -> dict:
    url      = job.get("url", "")
    platform = detect_platform(url)
    cover    = gen_cover(job)

    print(f"\n{'='*60}")
    print(f"[AutoApply] {job.get('title','')} @ {job.get('company','')}")
    print(f"[AutoApply] Platform: {platform}")
    print(f"{'='*60}")

    if platform == "greenhouse":
        return apply_greenhouse(url, cover)
    elif platform == "lever":
        return apply_lever(url, cover)
    elif platform == "workday":
        return apply_workday(url, cover)
    elif platform == "ashby":
        return apply_ashby(url, cover)
    elif platform == "smartrecruiters":
        return apply_smartrecruiters(url, cover)
    else:
        print(f"[AutoApply] Platform tidak dikenal — apply manual")
        print(f"\nCover letter untuk di-copy:\n{cover}")
        return {"success": False, "platform": "unknown", "url": url}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python form_filler/auto_apply.py <job_url>")
        print("")
        print("Contoh URL yang didukung:")
        print("  https://boards.greenhouse.io/coinbase/jobs/123456")
        print("  https://jobs.lever.co/consensys/abc-def")
        print("  https://ashbyhq.com/polygon/jobs/123")
        print("  https://careers.smartrecruiters.com/Binance/123")
        sys.exit(1)

    url = sys.argv[1]
    job = {
        "title": "Developer", "company": "Company",
        "url": url, "tags": "python web3 developer",
        "description": "Remote developer position"
    }
    result = auto_apply(job)
    status = "✅ Berhasil!" if result["success"] else "⚠️ Perlu cek manual"
    print(f"\nHasil: {status}")
