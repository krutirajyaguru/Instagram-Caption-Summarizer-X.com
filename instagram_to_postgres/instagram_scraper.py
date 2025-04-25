import logging,os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import tokens
from insta_to_postgres import PostgresDatabase
from utils import setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


class InstagramScraper:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = self.setup_driver()

    def setup_driver(self):
        """Initialize and return the WebDriver."""
        try:
            options = webdriver.FirefoxOptions()
            driver = webdriver.Remote(
                command_executor='http://selenium-firefox:4444/wd/hub',
                options=options
            )
            driver.maximize_window()
            return driver
        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise

    def close_popup(self, xpath):
        """Close popups if they appear."""
        try:
            popup_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            popup_button.click()
            logger.info(f"Closed popup with xpath: {xpath}")
        except Exception as e:
            logger.info(f"No popup found or failed to interact: {e}")
        '''
        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
            logger.info(f"Closed popup with xpath: {xpath}")
        except Exception as e:
            logger.info(f"No popup found with xpath: {xpath} or error: {e}")'''


    def login(self):
        """Log in to Instagram."""
        try:
            self.driver.get("https://www.instagram.com/accounts/login/")
            logger.info("Opened Instagram login page.")

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )

            self.driver.find_element(By.NAME, "username").send_keys(self.username)
            self.driver.find_element(By.NAME, "password").send_keys(self.password)
            self.driver.find_element(By.NAME, "password").send_keys(Keys.RETURN)

            logger.info("Logged in successfully.")

            self.close_popup("//button[contains(text(), 'Not Now')]")
        except Exception as e:
            logger.error(f"Error during login: {e}")
            self.driver.quit()
            raise

    def navigate_to_profile(self, profile_url):
        """Navigate to a specified Instagram profile."""
        try:
            self.driver.get(profile_url)
            logger.info(f"Navigating to profile: {profile_url}")
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/p/')]"))
            )
        except Exception as e:
            logger.error(f"Error navigating to profile: {e}")
            self.driver.quit()
            raise

    def fetch_post_urls(self):
        """Fetch post URLs from the profile page."""
        try:
            posts = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
            post_urls = [post.get_attribute("href") for post in posts]
            logger.info(f"Fetched {len(post_urls)} posts.")
            return post_urls
        except Exception as e:
            logger.error(f"Error fetching post URLs: {e}")
            return []

    def extract_caption(self):
        """Extract caption (title) from a post."""
        try:
            caption = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h1[contains(@class, '_ap3a')]")
            )).text
            return caption
        except Exception as e:
            logger.error(f"Error extracting caption: {e}")
            return None

    def extract_image_url(self):
        """Extract image URL from a post."""
        try:
            image_url = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//article//img")
            )).get_attribute("src")
            return image_url
        except Exception as e:
            logger.error(f"Error extracting image URL: {e}")
            return None

    def scrape_posts(self, profile_url, limit=5):
        """Scrape posts from the given profile URL."""
        try:
            self.login()
            self.navigate_to_profile(profile_url)

            post_urls = self.fetch_post_urls()
            db = PostgresDatabase()

            for i, post_url in enumerate(post_urls[:limit]):
                logger.info(f"Processing post {i + 1} URL: {post_url}")
                self.driver.get(post_url)

                caption = self.extract_caption()
                image_url = self.extract_image_url()

                if caption and image_url:
                    db.store_data_in_postgres(caption, image_url)

                logger.info("-" * 40)

        finally:
            self.driver.quit()
            logger.info("Scraping completed. Browser closed.")

if __name__ == "__main__":
    username = tokens['insta_username']
    password = tokens['insta_password']

    scraper = InstagramScraper(username, password)
    scraper.scrape_posts("https://www.instagram.com/bbcnews/")
