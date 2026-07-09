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

# ── GENERIC FORM FILLER (improved fallback) ──────────────────
def apply_generic(url: str, cover: str) -> dict:
    """
    Generic form filler dengan improved heuristics.
    Handles multi-step forms, cookie popups, and better field detection.
    """
    print(f"[Generic] {url[:70]}")
    driver = _driver()
    result = {"success": False, "platform": "generic", "url": url}
    try:
        driver.get(url)
        time.sleep(4)  # Wait longer for dynamic content

        # Dismiss cookie consent popups
        _click(driver, [
            "button:contains('Accept')", "button:contains('OK')", "button:contains('Got it')",
            "button:contains('Agree')", "button:contains('Close')", "#onetrust-accept-btn-handler",
            ".cookie-consent-accept", "[data-testid='cookie-accept']"
        ], timeout=3)
        time.sleep(1)

        # Try to click "Apply" button if on job listing page
        _click(driver, [
            "a:contains('Apply')", "button:contains('Apply')", "a:contains('Apply Now')",
            "button:contains('Apply Now')", "a[data-qa*='apply']",
            "button[class*='apply']", "a[class*='apply']"
        ], timeout=3)
        time.sleep(3)  # Wait for apply form to load

        filled = 0

        # First/Last name (try separate fields first)
        if _try_fill(driver, ["input[name='first_name']", "input[id*='first' i]", "input[placeholder*='first' i]"], APPLICANT["first_name"]):
            filled += 1
            _try_fill(driver, ["input[name='last_name']", "input[id*='last' i]", "input[placeholder*='last' i]"], APPLICANT["last_name"])
        # Full name fallback
        elif _try_fill(driver, ["input[name*='name']", "input[id*='name' i]", "input[placeholder*='name' i]", "input[name*='full']"], APPLICANT["full_name"]):
            filled += 1

        # Email
        if _try_fill(driver, ["input[type='email']", "input[name*='email']", "input[id*='email' i]", "input[placeholder*='email' i]", "input[name*='mail']"], APPLICANT["email"]):
            filled += 1

        # Phone
        if _try_fill(driver, ["input[type='tel']", "input[name*='phone']", "input[id*='phone' i]", "input[placeholder*='phone' i]", "input[name*='telefon']"], APPLICANT["phone"]):
            filled += 1

        # LinkedIn
        if _try_fill(driver, ["input[name*='linkedin']", "input[id*='linkedin' i]", "input[placeholder*='linkedin' i]"], APPLICANT["linkedin"]):
            filled += 1

        # GitHub/Portfolio
        _try_fill(driver, ["input[name*='github']", "input[id*='github' i]", "input[placeholder*='github' i]"], APPLICANT["github"])

        # Message/Cover letter (try multiple patterns)
        cover_selectors = [
            "textarea[name*='cover']", "textarea[name*='message']",
            "textarea[id*='cover' i]", "textarea[id*='message' i]",
            "textarea[placeholder*='cover' i]", "textarea[placeholder*='tell' i]",
            "textarea[placeholder*='about' i]", "textarea[placeholder*='message' i]",
            "textarea[name*='anschreiben']",  # German
            "textarea"
        ]
        if _try_fill(driver, cover_selectors, cover):
            filled += 1

        # Resume/CV upload
        if _upload(driver, APPLICANT["cv_path"]):
            filled += 1

        print(f"[Generic] Fields filled: {filled}")

        # Try to submit if we have at least 3 fields
        if filled >= 3:
            # Scroll to bottom to make submit button visible
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)

            submitted = _click(driver, [
                "button[type='submit']",
                "input[type='submit']",
                "button[name*='submit']",
                "#submit", ".submit-btn",
                "button:contains('Submit')",
                "button:contains('Send')",
                "button:contains('Apply')",
                "button:contains('Apply Now')",
                "button:contains('Bewerben')",
                "button[class*='submit']",
                "button[class*='apply']"
            ], timeout=5)

            if submitted:
                time.sleep(3)
                # Check for success indicators
                page_text = driver.page_source.lower()
                success_indicators = ["thank you", "submitted", "received", "success", "applied"]
                if any(indicator in page_text for indicator in success_indicators):
                    print(f"[Generic] [OK] Submitted successfully!")
                    result["success"] = True
                else:
                    print(f"[Generic] [OK] Submit clicked (verify manually)")
                    result["success"] = True  # Assume success if submit was clicked
            else:
                print(f"[Generic] [WARNING] Submit button not found")
                result["error"] = "Submit button not found"
        else:
            print(f"[Generic] [WARNING] Too few fields filled ({filled}), skipping submit")
            result["error"] = f"Only {filled} fields filled"

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

    # Known ATS platforms
    if "greenhouse.io"       in u: return "greenhouse"
    if "lever.co"            in u: return "lever"
    if "myworkdayjobs"       in u: return "workday"
    if "workday.com"         in u: return "workday"
    if "ashbyhq.com"         in u: return "ashby"
    if "smartrecruiters.com" in u: return "smartrecruiters"
    if "wellfound.com"       in u: return "wellfound"
    if "angel.co"            in u: return "wellfound"
    if "bamboohr.com"        in u: return "bamboohr"
    if "breezy.hr"           in u: return "breezy"
    if "apply.workable.com"  in u: return "generic"
    if "jobs.ashbyhq.com"    in u: return "ashby"
    if "boards.greenhouse.io" in u: return "greenhouse"
    if "jobs.lever.co"       in u: return "lever"

    # More ATS platforms
    if "icims.com"           in u: return "generic"
    if "taleo.net"           in u: return "generic"
    if "successfactors"      in u: return "generic"
    if "jobvite.com"         in u: return "generic"
    if "ultipro.com"         in u: return "generic"
    if "paylocity.com"       in u: return "generic"
    if "adp.com"             in u: return "generic"

    # Web3 specific patterns
    if any(x in u for x in ["web3.career", "crypto.jobs", "cryptojobslist"]):
        return "generic"

    # German freelance platforms
    if any(x in u for x in ["freelance.de", "gulp.de", "freelancermap", "malt.de"]):
        return "generic"

    # Remote job boards that link to company pages
    if any(x in u for x in ["remoteok.com", "weworkremotely.com", "remotive.com", "himalayas.app", "arbeitnow.com"]):
        return "generic"

    # If has /jobs/, /careers/, /apply, /positions in path → likely a career page
    if any(x in u for x in ["/jobs/", "/careers/", "/apply", "/positions", "/opening/", "/vacancy/"]):
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
