import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import logging
import os
import random
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import ExperienceLevelFilters
from linkedin_jobs_scraper.events import Events

class LinkedInJobScraper:
    def __init__(self, headless=True, use_cookies=False, cookies_file=None):
        self.headless = headless
        self.use_cookies = use_cookies
        self.cookies_file = cookies_file
        self.driver = None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable images and CSS for faster loading
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Patch: Ensure correct chromedriver binary is used
        driver_path = ChromeDriverManager().install()
        self.logger.info(f"[DEBUG] ChromeDriverManager returned path: {driver_path}")
        if not driver_path.endswith("chromedriver") or driver_path.endswith("THIRD_PARTY_NOTICES.chromedriver"):
            driver_dir = os.path.dirname(driver_path)
            candidate = os.path.join(driver_dir, "chromedriver")
            self.logger.info(f"[DEBUG] Forcing driver path to: {candidate}")
            driver_path = candidate
        service = Service(driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Load cookies if provided
        if self.use_cookies and self.cookies_file:
            self.load_cookies()
    
    def load_cookies(self):
        """Load cookies from file to maintain session"""
        try:
            self.driver.get("https://www.linkedin.com")
            time.sleep(2)
            
            with open(self.cookies_file, 'r') as f:
                cookies = json.load(f)
            
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            
            self.logger.info("Cookies loaded successfully")
            
        except Exception as e:
            self.logger.warning(f"Failed to load cookies: {str(e)}")
    
    def save_cookies(self):
        """Save current cookies to file"""
        try:
            cookies = self.driver.get_cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f)
            self.logger.info("Cookies saved successfully")
        except Exception as e:
            self.logger.warning(f"Failed to save cookies: {str(e)}")
    
    def search_jobs(self, job_title, location=None, experience_level=None, max_jobs=10):
        """Search for jobs on LinkedIn"""
        try:
            self.logger.info(f"Searching for jobs: {job_title} in {location}")
            
            # Construct search URL
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}"
            if location:
                search_url += f"&location={location.replace(' ', '%20')}"
            if experience_level:
                search_url += f"&f_E={self._get_experience_level_code(experience_level)}"
            
            self.driver.get(search_url)
            time.sleep(2)  # Initial wait for page load
            
            # Slow mode: random delay to mimic human behavior and avoid rate limiting
            slow_mo = random.uniform(1.0, 2.0)
            self.logger.info(f"[SlowMo] Waiting {slow_mo:.2f} seconds after page load...")
            time.sleep(slow_mo)

            # Explicit wait for job cards to appear
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-card-job-posting-card-wrapper__entity-lockup"))
                )
                self.logger.info("[Wait] Job cards appeared on the page.")
            except TimeoutException:
                self.logger.warning("[Wait] Timeout waiting for job cards to appear.")

            # Check if we need to handle authentication
            if self._is_auth_required():
                self.logger.warning("Authentication required. Using public job search.")
                return self._search_public_jobs(job_title, location, max_jobs)
            
            jobs = []
            job_cards = []
            
            # Scroll to load more jobs
            for scroll_num in range(3):  # Scroll 3 times to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                slow_mo = random.uniform(1.0, 2.0)
                self.logger.info(f"[SlowMo] Waiting {slow_mo:.2f} seconds after scroll {scroll_num+1}...")
                time.sleep(slow_mo)
                # Log number of job cards after each scroll
                cards_now = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-job-posting-card-wrapper__entity-lockup")
                self.logger.info(f"[Scroll {scroll_num+1}] Found {len(cards_now)} job cards so far.")
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-card-job-posting-card-wrapper__entity-lockup")
            
            self.logger.info(f"Found {len(job_cards)} job cards after scrolling.")
            
            # Save page source for debugging
            with open("debug_linkedin_jobs_after_scroll.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            self.logger.info("Saved page source to debug_linkedin_jobs_after_scroll.html")

            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    job_data = self._extract_job_data(card)
                    if job_data:
                        jobs.append(job_data)
                        self.logger.info(f"Extracted job {i+1}: {job_data['title']}")
                except Exception as e:
                    self.logger.warning(f"Failed to extract job {i+1}: {str(e)}")
                    continue
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error searching jobs: {str(e)}")
            return []
    
    def _is_auth_required(self):
        """Check if authentication is required"""
        try:
            # Look for login prompts or restricted content
            auth_elements = self.driver.find_elements(By.CSS_SELECTOR, ".auth-wall, .login-prompt, .sign-in-prompt")
            return len(auth_elements) > 0
        except:
            return False
    
    def _search_public_jobs(self, job_title, location, max_jobs):
        """Search for jobs using public LinkedIn job search (limited results)"""
        try:
            self.logger.info("Using public job search (limited results)")
            
            # Use a different approach for public access
            search_url = f"https://www.linkedin.com/jobs/search/?keywords={job_title.replace(' ', '%20')}"
            if location:
                search_url += f"&location={location.replace(' ', '%20')}"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            # Try to find job listings with different selectors
            selectors = [
                ".job-card-job-posting-card-wrapper__entity-lockup",
                ".job-search-card",
                ".job-card-container",
                ".job-card",
                "[data-job-id]"
            ]
            
            job_cards = []
            for selector in selectors:
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if job_cards:
                    break
            
            jobs = []
            for i, card in enumerate(job_cards[:max_jobs]):
                try:
                    job_data = self._extract_job_data_public(card)
                    if job_data:
                        jobs.append(job_data)
                except Exception as e:
                    continue
            
            return jobs
            
        except Exception as e:
            self.logger.error(f"Error in public job search: {str(e)}")
            return []
    
    def _extract_job_data(self, job_card):
        """Extract job data from a job card element"""
        try:
            # Job title
            title_element = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__title")
            title = title_element.text.strip()
            
            # Company name
            try:
                company_element = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__subtitle")
                company = company_element.text.strip()
            except NoSuchElementException:
                company = "Unknown Company"
            
            # Location
            try:
                location_element = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__location")
                location = location_element.text.strip()
            except NoSuchElementException:
                location = "Unknown Location"
            
            # Job URL
            try:
                link_element = job_card.find_element(By.CSS_SELECTOR, "a.job-search-card__title")
                job_url = link_element.get_attribute("href")
            except NoSuchElementException:
                job_url = ""
            
            # Posted time
            try:
                time_element = job_card.find_element(By.CSS_SELECTOR, ".job-search-card__listdate")
                posted_time = time_element.text.strip()
            except NoSuchElementException:
                posted_time = "Unknown"
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "posted_time": posted_time,
                "source": "LinkedIn"
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting job data: {str(e)}")
            return None
    
    def _extract_job_data_public(self, job_card):
        """Extract job data from public job search results"""
        try:
            # Try multiple selectors for different LinkedIn layouts
            title_selectors = [".job-search-card__title", ".job-card__title", "h3", "h4"]
            company_selectors = [".job-search-card__subtitle", ".job-card__company", ".company-name"]
            location_selectors = [".job-search-card__location", ".job-card__location", ".location"]
            
            title = "Unknown Title"
            company = "Unknown Company"
            location = "Unknown Location"
            job_url = ""
            
            # Extract title
            for selector in title_selectors:
                try:
                    element = job_card.find_element(By.CSS_SELECTOR, selector)
                    title = element.text.strip()
                    if title:
                        break
                except:
                    continue
            
            # Extract company
            for selector in company_selectors:
                try:
                    element = job_card.find_element(By.CSS_SELECTOR, selector)
                    company = element.text.strip()
                    if company:
                        break
                except:
                    continue
            
            # Extract location
            for selector in location_selectors:
                try:
                    element = job_card.find_element(By.CSS_SELECTOR, selector)
                    location = element.text.strip()
                    if location:
                        break
                except:
                    continue
            
            # Extract URL
            try:
                link_element = job_card.find_element(By.CSS_SELECTOR, "a")
                job_url = link_element.get_attribute("href")
            except:
                pass
            
            return {
                "title": title,
                "company": company,
                "location": location,
                "url": job_url,
                "posted_time": "Unknown",
                "source": "LinkedIn (Public)"
            }
            
        except Exception as e:
            self.logger.warning(f"Error extracting public job data: {str(e)}")
            return None
    
    def _get_experience_level_code(self, experience_level):
        """Convert experience level to LinkedIn filter code"""
        experience_codes = {
            "internship": "1",
            "entry": "2", 
            "associate": "3",
            "mid-senior": "4",
            "senior": "5",
            "executive": "6"
        }
        return experience_codes.get(experience_level.lower(), "")
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            self.logger.info("Browser closed")

# Tool function for CrewAI
def linkedin_job_search_tool(job_title, location=None, experience_level=None, max_jobs=10, li_at_cookie=None):
    """
    Search for jobs on LinkedIn using py-linkedin-jobs-scraper
    Args:
        job_title (str): Job title to search for
        location (str): Location to search in
        experience_level (str): Experience level (internship, entry, associate, mid-senior, senior, executive)
        max_jobs (int): Maximum number of jobs to return
        li_at_cookie (str): LinkedIn session cookie for authenticated search
    Returns:
        list: List of job dictionaries
    """
    results = []
    logger = logging.getLogger("py-linkedin-jobs-scraper-wrapper")
    logger.setLevel(logging.INFO)
    
    # Set LI_AT_COOKIE env var if provided
    if li_at_cookie:
        os.environ["LI_AT_COOKIE"] = li_at_cookie
    
    # Map experience_level to filter (see py-linkedin-jobs-scraper docs for valid enums)
    exp_map = {
        "internship": ExperienceLevelFilters.INTERNSHIP,
        "entry": ExperienceLevelFilters.ENTRY_LEVEL,
        "associate": ExperienceLevelFilters.ASSOCIATE,
        "mid-senior": ExperienceLevelFilters.MID_SENIOR,
        "senior": ExperienceLevelFilters.MID_SENIOR,  # Map 'senior' to MID_SENIOR
        "director": ExperienceLevelFilters.DIRECTOR,
        # Add more mappings if needed
    }
    exp_filter = None
    if experience_level:
        key = experience_level.strip().lower()
        exp_filter = exp_map.get(key, None)  # Ignore invalid values

    def on_data(data):
        job = {
            "title": data.title,
            "company": data.company,
            "location": data.location,
            "description": data.description,
            "url": data.link,
            "posted_time": data.date,
            "source": "LinkedIn"
        }
        results.append(job)
        logger.info(f"[DATA] {job['title']} at {job['company']}")
        # Removed scraper.stop() as it is not supported

    def on_error(error):
        logger.error(f"[ERROR] {error}")

    def on_end():
        logger.info("[END]")

    scraper = LinkedinScraper(
        chrome_executable_path=None,
        chrome_options=None,
        headless=True,
        max_workers=1,
        slow_mo=0.5,
        page_load_timeout=40
    )
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    filters = QueryFilters(
        experience=[exp_filter] if exp_filter else None
    )
    queries = [
        Query(
            query=job_title,
            options=QueryOptions(
                locations=[location] if location else [],
                limit=max_jobs,
                filters=filters
            )
        )
    ]
    scraper.run(queries)
    return results

if __name__ == "__main__":
    # Test the scraper
    scraper = LinkedInJobScraper(headless=False)  # Set to False to see the browser
    scraper.setup_driver()
    
    # Test search
    jobs = scraper.search_jobs("Software Engineer", "San Francisco", "mid-senior", 5)
    print(json.dumps(jobs, indent=2))
    
    scraper.close() 