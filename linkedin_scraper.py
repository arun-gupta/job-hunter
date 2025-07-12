import time
import json
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

class LinkedInJobScraper:
    def __init__(self, headless=True):
        self.headless = headless
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
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(10)
        
    def login_to_linkedin(self, email, password):
        """Login to LinkedIn"""
        try:
            self.logger.info("Logging into LinkedIn...")
            self.driver.get("https://www.linkedin.com/login")
            
            # Enter email
            email_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()
            
            # Wait for login to complete
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".global-nav"))
            )
            
            self.logger.info("Successfully logged into LinkedIn")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to login to LinkedIn: {str(e)}")
            return False
    
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
            time.sleep(3)
            
            jobs = []
            job_cards = []
            
            # Scroll to load more jobs
            for _ in range(3):  # Scroll 3 times to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find job cards
            job_cards = self.driver.find_elements(By.CSS_SELECTOR, ".job-search-card")
            
            self.logger.info(f"Found {len(job_cards)} job cards")
            
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
def linkedin_job_search_tool(job_title, location=None, experience_level=None, max_jobs=10):
    """
    Search for jobs on LinkedIn using Selenium
    
    Args:
        job_title (str): Job title to search for
        location (str): Location to search in
        experience_level (str): Experience level (internship, entry, associate, mid-senior, senior, executive)
        max_jobs (int): Maximum number of jobs to return
    
    Returns:
        list: List of job dictionaries
    """
    scraper = LinkedInJobScraper(headless=True)
    
    try:
        scraper.setup_driver()
        
        # Note: For production use, you'd need to provide LinkedIn credentials
        # For now, we'll search without login (limited results)
        jobs = scraper.search_jobs(job_title, location, experience_level, max_jobs)
        
        return jobs
        
    except Exception as e:
        return {"error": f"Failed to search jobs: {str(e)}"}
    
    finally:
        scraper.close()

if __name__ == "__main__":
    # Test the scraper
    scraper = LinkedInJobScraper(headless=False)  # Set to False to see the browser
    scraper.setup_driver()
    
    # Test search
    jobs = scraper.search_jobs("Software Engineer", "San Francisco", "mid-senior", 5)
    print(json.dumps(jobs, indent=2))
    
    scraper.close() 