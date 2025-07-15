#!/usr/bin/env python3
"""
LinkedIn Authentication Helper

This script helps users get LinkedIn cookies for better job search access.
Since LinkedIn uses OAuth, we need to manually get cookies from a logged-in browser session.
"""

import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_linkedin_cookies():
    """
    Interactive script to help users get LinkedIn cookies
    """
    print("🔐 LinkedIn Authentication Helper")
    print("=" * 50)
    print()
    print("LinkedIn uses OAuth authentication, which requires manual login.")
    print("This script will help you get cookies from your logged-in LinkedIn session.")
    print()
    print("Steps:")
    print("1. A Chrome browser will open")
    print("2. Navigate to LinkedIn and log in manually")
    print("3. The script will capture your session cookies")
    print("4. Cookies will be saved for future use")
    print()
    
    input("Press Enter to continue...")
    
    # Setup Chrome driver
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    
    driver_path = ChromeDriverManager().install()
    print(f"[DEBUG] ChromeDriverManager returned path: {driver_path}")
    # If the path is not the actual chromedriver binary, fix it
    if not driver_path.endswith("chromedriver") or driver_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
        # Try to use the correct binary in the same directory
        import os
        driver_dir = os.path.dirname(driver_path)
        candidate = os.path.join(driver_dir, "chromedriver")
        print(f"[DEBUG] Forcing driver path to: {candidate}")
        driver_path = candidate
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        # Navigate to LinkedIn
        print("🌐 Opening LinkedIn...")
        driver.get("https://www.linkedin.com")
        
        print()
        print("📝 Instructions:")
        print("- Log in to your LinkedIn account manually")
        print("- Navigate to any page on LinkedIn")
        print("- Once you're logged in, come back here and press Enter")
        print()
        
        input("Press Enter after you've logged in to LinkedIn...")
        
        # Get cookies
        print("🍪 Capturing cookies...")
        cookies = driver.get_cookies()
        
        if not cookies:
            print("❌ No cookies found. Make sure you're logged in to LinkedIn.")
            return False
        
        # Save cookies
        cookies_file = "linkedin_cookies.json"
        with open(cookies_file, 'w') as f:
            json.dump(cookies, f, indent=2)
        
        print(f"✅ Cookies saved to {cookies_file}")
        print(f"📊 Captured {len(cookies)} cookies")
        
        # Test the cookies
        print()
        print("🧪 Testing cookies...")
        driver.delete_all_cookies()
        
        for cookie in cookies:
            driver.add_cookie(cookie)
        
        # Test by going to LinkedIn jobs
        driver.get("https://www.linkedin.com/jobs/")
        
        # Check if we're still logged in
        if "login" not in driver.current_url.lower():
            print("✅ Cookie test successful! You're logged in.")
            return True
        else:
            print("❌ Cookie test failed. You may need to log in again.")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False
    
    finally:
        driver.quit()

def use_cookies_with_scraper():
    """
    Show how to use the saved cookies with the LinkedIn scraper
    """
    print()
    print("🔧 How to use cookies with the LinkedIn scraper:")
    print("=" * 50)
    print()
    print("1. Make sure you have linkedin_cookies.json file")
    print("2. Update your scraper initialization:")
    print()
    print("```python")
    print("from linkedin_scraper import LinkedInJobScraper")
    print()
    print("# Use cookies for better access")
    print("scraper = LinkedInJobScraper(")
    print("    headless=True,")
    print("    use_cookies=True,")
    print("    cookies_file='linkedin_cookies.json'")
    print(")")
    print("```")
    print()
    print("3. The scraper will automatically load cookies and use them")
    print("4. This gives you access to more job listings and better results")
    print()

if __name__ == "__main__":
    success = get_linkedin_cookies()
    
    if success:
        use_cookies_with_scraper()
        print("🎉 Setup complete! You can now use the LinkedIn scraper with better access.")
    else:
        print("❌ Setup failed. Please try again or use the scraper without cookies (limited results).") 