import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseScraper:
    def __init__(self, headless=True):
        """
        Initialize the base scraper with Selenium WebDriver
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
        """
        # Set up Chrome options
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
        
        # Add additional options for better performance and compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--disable-extensions")
        
        # Initialize Chrome WebDriver
        try:
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            logger.info("Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Chrome WebDriver: {e}")
            raise
    
    def _scroll_page(self, max_scroll, wait_time):
        """
        Scroll down the page to load more content
        
        Args:
            max_scroll (int): Maximum number of times to scroll
            wait_time (int): Time to wait between scrolls (in seconds)
        """
        logger.info(f"Scrolling page (max_scroll={max_scroll}, wait_time={wait_time})")
        
        # Get initial page height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        # Scroll down to bottom
        for i in range(max_scroll):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait to load page
            time.sleep(wait_time)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                logger.info(f"Reached end of page after {i+1} scrolls")
                break
            last_height = new_height
    
    def close(self):
        """Close the WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()
            logger.info("Chrome WebDriver closed") 