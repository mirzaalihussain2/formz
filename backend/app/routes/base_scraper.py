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
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        # Set up user agent to avoid being blocked
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Initialize the WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
    
    def _scroll_page(self, max_scroll, wait_time):
        """
        Scroll down the page to load more content
        
        Args:
            max_scroll (int): Maximum number of times to scroll
            wait_time (int): Time to wait between scrolls
        """
        logger.info(f"Scrolling page up to {max_scroll} times")
        
        # Get initial page height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        for i in range(max_scroll):
            # Scroll down to the bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Wait for new content to load
            time.sleep(wait_time)
            
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Break if no new content loaded
            if new_height == last_height:
                logger.info(f"No more content to load after {i+1} scrolls")
                break
                
            last_height = new_height
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed") 