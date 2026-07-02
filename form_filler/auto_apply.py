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
            print(f"[Greenhouse] [OK] Submitted! Fields filled: {filled}")
            result["success"] = True
        else:
            print(f"[Greenhouse] [WARNING] Fields filled: {filled}, submit manual diperlukan")

    except Exception as e:
        print(f"[Greenhouse] X {e}")
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
            print(f"[Lever] [OK] Submitted! Fields: {filled}")
            result["success"] = True
        else:
            print(f"[Lever] [WARNING] Fields: {filled}, submit manual diperlukan")

    except Exception as e:
        print(f"[Lever] X {e}")
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
            print(f"[Ashby] [OK] Submitted!")
            result["success"] = True
        else:
            print(f"[Ashby] [WARNING] Submit manual diperlukan")

    except Exception as e:
        print(f"[Ashby] X {e}")
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
        print(f"[Workday] X {e}")
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
            print(f"[SmartRecruiters] [OK] Submitted!")
            result["success"] = True

    except Exception as e:
        print(f"[SmartRecruiters] X {e}")
    finally:
        driver.quit()
    return result

# ── WELLFOUND (AngelList) — Web3/Startup favorite ────────────
def apply_wellfound(url: str, cover: str) -> dict:
    print(f"[Wellfound] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "wellfound", "url": url}
    try:
        driver.get(url)
        time.sleep(2)

        # Click "Apply" button if not on application page
        _click(driver, ["a[data-test='ApplyButton']", "button:contains('Apply')", "a.apply"])
        time.sleep(2)

        _try_fill(driver, ["input[name='name']", "#name", "input[placeholder*='name']"], APPLICANT["full_name"])
        _try_fill(driver, ["input[name='email']", "#email", "input[type='email']"], APPLICANT["email"])
        _try_fill(driver, ["textarea[name='note']", "textarea[placeholder*='tell']", "#note"], cover)
        _try_fill(driver, ["input[name='linkedin']", "input[placeholder*='LinkedIn']"], APPLICANT["linkedin"])

        _upload(driver, APPLICANT["cv_path"])
        time.sleep(1)

        submitted = _click(driver, ["button[type='submit']", "button[data-test='submit']", ".submit-btn"])
        if submitted:
            time.sleep(2)
            print(f"[Wellfound] [OK] Submitted!")
            result["success"] = True
        else:
            print(f"[Wellfound] [WARNING] Submit manual diperlukan")

    except Exception as e:
        print(f"[Wellfound] X {e}")
    finally:
        driver.quit()
    return result

# ── BAMBOOHR ─────────────────────────────────────────────────
def apply_bamboohr(url: str, cover: str) -> dict:
    print(f"[BambooHR] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "bamboohr", "url": url}
    try:
        driver.get(url)
        time.sleep(2)

        _try_fill(driver, ["#firstName", "input[name='firstName']"], APPLICANT["first_name"])
        _try_fill(driver, ["#lastName",  "input[name='lastName']"],  APPLICANT["last_name"])
        _try_fill(driver, ["#email",     "input[name='email']"],     APPLICANT["email"])
        _try_fill(driver, ["#phone",     "input[name='phone']"],     APPLICANT["phone"])

        _try_fill(driver, ["textarea[name='coverLetter']", "#coverLetter"], cover)
        _upload(driver, APPLICANT["cv_path"])
        time.sleep(1)

        submitted = _click(driver, ["button[type='submit']", "#submitApplication"])
        if submitted:
            time.sleep(2)
            print(f"[BambooHR] [OK] Submitted!")
            result["success"] = True

    except Exception as e:
        print(f"[BambooHR] X {e}")
    finally:
        driver.quit()
    return result

# ── BREEZY HR ────────────────────────────────────────────────
def apply_breezy(url: str, cover: str) -> dict:
    print(f"[BreezyHR] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "breezy", "url": url}
    try:
        driver.get(url)
        time.sleep(2)

        _try_fill(driver, ["input[name='name']", "#name"], APPLICANT["full_name"])
        _try_fill(driver, ["input[name='email']", "#email"], APPLICANT["email"])
        _try_fill(driver, ["input[name='phone']", "#phone"], APPLICANT["phone"])
        _try_fill(driver, ["textarea[name='message']", "textarea[placeholder*='tell']"], cover)

        _upload(driver, APPLICANT["cv_path"])
        time.sleep(1)

        submitted = _click(driver, ["button[type='submit']", ".btn-submit"])
        if submitted:
            time.sleep(2)
            print(f"[BreezyHR] [OK] Submitted!")
            result["success"] = True

    except Exception as e:
        print(f"[BreezyHR] X {e}")
    finally:
        driver.quit()
    return result

# ── GENERIC FORM FILLER (fallback untuk web kecil) ───────────
def apply_generic(url: str, cover: str) -> dict:
    """
    Generic form filler untuk website company yang tidak dikenal.
    Menggunakan heuristic untuk detect field names.
    """
    print(f"[Generic] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "generic", "url": url}
    try:
        driver.get(url)
        time.sleep(3)

        # Try common field patterns
        filled = 0

        # Name fields
        name_selectors = [
            "input[name*='name']", "input[id*='name']", "input[placeholder*='name' i]",
            "input[name*='full']", "input[name*='vorname']", "input[name*='nachname']"  # German
        ]
        if _try_fill(driver, name_selectors, APPLICANT["full_name"]):
            filled += 1

        # Email fields
        email_selectors = [
            "input[type='email']", "input[name*='email']", "input[id*='email']",
            "input[name*='mail']", "input[placeholder*='email' i]"
        ]
        if _try_fill(driver, email_selectors, APPLICANT["email"]):
            filled += 1

        # Phone fields
        phone_selectors = [
            "input[type='tel']", "input[name*='phone']", "input[name*='telefon']",
            "input[id*='phone']", "input[placeholder*='phone' i]"
        ]
        if _try_fill(driver, phone_selectors, APPLICANT["phone"]):
            filled += 1

        # Message/Cover letter fields
        message_selectors = [
            "textarea[name*='message']", "textarea[name*='cover']", "textarea[name*='anschreiben']",  # German
            "textarea[id*='message']", "textarea[placeholder*='tell' i]", "textarea[placeholder*='about' i]",
            "textarea", "#message", "#cover_letter"
        ]
        if _try_fill(driver, message_selectors, cover):
            filled += 1

        # Resume upload
        if _upload(driver, APPLICANT["cv_path"]):
            filled += 1

        # Try to submit
        submit_selectors = [
            "button[type='submit']", "input[type='submit']",
            "button[name*='submit']", ".submit-btn", "#submit",
            "button:contains('Submit')", "button:contains('Send')", "button:contains('Apply')",
            "button:contains('Bewerben')"  # German
        ]
        submitted = _click(driver, submit_selectors, timeout=3)

        if submitted and filled >= 3:
            time.sleep(2)
            print(f"[Generic] [OK] Submitted! Fields filled: {filled}")
            result["success"] = True
        else:
            print(f"[Generic] [WARNING] Fields filled: {filled}, manual check needed")
            result["error"] = f"Only {filled} fields filled, submit uncertain"

    except Exception as e:
        print(f"[Generic] X {e}")
        result["error"] = str(e)
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
    if "wellfound.com"       in u: return "wellfound"
    if "angel.co"            in u: return "wellfound"  # old domain
    if "bamboohr.com"        in u: return "bamboohr"
    if "breezy.hr"           in u: return "breezy"
    if "apply.workable.com"  in u: return "generic"
    if "jobs.ashbyhq.com"    in u: return "ashby"

    # Web3 specific patterns
    if any(x in u for x in ["web3.career", "crypto.jobs", "cryptojobslist"]):
        return "generic"

    # German freelance platforms
    if any(x in u for x in ["freelance.de", "gulp.de", "freelancermap", "malt.de"]):
        return "generic"

    # If has /jobs/, /careers/, /apply in path → likely a career page
    if any(x in u for x in ["/jobs/", "/careers/", "/apply", "/positions"]):
        return "generic"

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
    elif platform == "wellfound":
        return apply_wellfound(url, cover)
    elif platform == "bamboohr":
        return apply_bamboohr(url, cover)
    elif platform == "breezy":
        return apply_breezy(url, cover)
    elif platform == "generic":
        return apply_generic(url, cover)
    else:
        print(f"[AutoApply] Platform tidak dikenal -- skip auto-apply")
        print(f"\n[TIP] Cover letter untuk di-copy manual:\n{cover[:500]}...")
        return {"success": False, "platform": "unknown", "url": url, "error": "Platform not supported"}


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
    status = "[OK] Berhasil!" if result["success"] else "[WARNING] Perlu cek manual"
    print(f"\nHasil: {status}")
