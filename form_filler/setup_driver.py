#!/usr/bin/env python3
# form_filler/setup_driver.py
# Install ChromeDriver otomatis — jalankan sekali saja

import subprocess, sys, platform, os

def install():
    print("=" * 50)
    print("  Setup ChromeDriver untuk Auto Form Filler")
    print("=" * 50)

    # Install selenium & webdriver-manager
    print("\n[1] Install Python packages...")
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "selenium", "webdriver-manager", "--upgrade", "-q"])

    # Test import
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options

        print("\n[2] Download ChromeDriver...")
        opts = Options()
        opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=opts)
        driver.get("https://www.google.com")
        title = driver.title
        driver.quit()
        print(f"  ✅ ChromeDriver OK! Test page: {title}")
        print("\n✅ Setup selesai! Auto form filler siap dipakai.")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nSolusi:")
        print("1. Pastikan Google Chrome sudah terinstall di komputer")
        print("2. Download dari: https://www.google.com/chrome/")
        print("3. Jalankan setup ini lagi setelah install Chrome")

if __name__ == "__main__":
    install()
