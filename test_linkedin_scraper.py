#!/usr/bin/env python3
"""
Test script for the updated LinkedIn scraper with OAuth authentication handling
"""

import json
from linkedin_scraper import LinkedInJobScraper

def test_linkedin_scraper():
    """Test the LinkedIn scraper with OAuth handling"""
    print("🧪 Testing LinkedIn Scraper with OAuth Authentication")
    print("=" * 60)
    
    # Test without cookies (public access)
    print("\n1️⃣ Testing public access (no authentication)...")
    scraper = LinkedInJobScraper(headless=True)
    
    try:
        scraper.setup_driver()
        
        # Test search
        jobs = scraper.search_jobs("Software Engineer", "San Francisco", "mid-senior", 3)
        
        print(f"✅ Found {len(jobs)} jobs with public access")
        
        if jobs:
            print("\n📋 Sample job:")
            sample_job = jobs[0]
            print(f"   Title: {sample_job.get('title', 'N/A')}")
            print(f"   Company: {sample_job.get('company', 'N/A')}")
            print(f"   Location: {sample_job.get('location', 'N/A')}")
            print(f"   Source: {sample_job.get('source', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Error with public access: {str(e)}")
    
    finally:
        scraper.close()
    
    # Test with cookies if available
    print("\n2️⃣ Testing with cookies (if available)...")
    try:
        scraper_with_cookies = LinkedInJobScraper(
            headless=True,
            use_cookies=True,
            cookies_file="linkedin_cookies.json"
        )
        
        scraper_with_cookies.setup_driver()
        
        # Test search
        jobs_with_cookies = scraper_with_cookies.search_jobs("Data Scientist", "New York", "senior", 3)
        
        print(f"✅ Found {len(jobs_with_cookies)} jobs with cookies")
        
        if jobs_with_cookies:
            print("\n📋 Sample job (with cookies):")
            sample_job = jobs_with_cookies[0]
            print(f"   Title: {sample_job.get('title', 'N/A')}")
            print(f"   Company: {sample_job.get('company', 'N/A')}")
            print(f"   Location: {sample_job.get('location', 'N/A')}")
            print(f"   Source: {sample_job.get('source', 'N/A')}")
        
        scraper_with_cookies.close()
        
    except FileNotFoundError:
        print("ℹ️  No cookies file found. Run linkedin_auth_helper.py to set up cookies.")
    except Exception as e:
        print(f"❌ Error with cookies: {str(e)}")
    
    print("\n🎉 Test completed!")
    print("\n💡 Tips:")
    print("- For better results, run: python linkedin_auth_helper.py")
    print("- This will help you get cookies for authenticated access")
    print("- Public access works but has limited results")

if __name__ == "__main__":
    test_linkedin_scraper() 