#!/usr/bin/env python3
"""
Test script for LinkedIn job scraper
"""

from linkedin_scraper import LinkedInJobScraper
import json

def test_linkedin_scraper():
    print("🧪 Testing LinkedIn Job Scraper...")
    
    # Create scraper instance
    scraper = LinkedInJobScraper(headless=True)
    
    try:
        # Setup driver
        print("🔧 Setting up Chrome driver...")
        scraper.setup_driver()
        
        # Test job search
        print("🔍 Searching for jobs...")
        jobs = scraper.search_jobs(
            job_title="Software Engineer",
            location="San Francisco",
            experience_level="mid-senior",
            max_jobs=5
        )
        
        # Display results
        print(f"\n✅ Found {len(jobs)} jobs:")
        for i, job in enumerate(jobs, 1):
            print(f"\n{i}. {job['title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   Posted: {job['posted_time']}")
            print(f"   URL: {job['url']}")
        
        # Save results to file
        with open('test_results.json', 'w') as f:
            json.dump(jobs, f, indent=2)
        print(f"\n💾 Results saved to test_results.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    finally:
        # Clean up
        scraper.close()
        print("🧹 Cleanup complete")

if __name__ == "__main__":
    test_linkedin_scraper() 