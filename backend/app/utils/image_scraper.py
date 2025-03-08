import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin, urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImageScraper:
    def __init__(self, headless=True, download_path="./downloaded_images"):
        """
        Initialize the image scraper with Selenium WebDriver
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
            download_path (str): Path to save downloaded images
        """
        self.download_path = download_path
        
        # Create download directory if it doesn't exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
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
        
    def scrape_images(self, url, scroll=True, max_scroll=5, wait_time=2):
        """
        Scrape images from a given URL
        
        Args:
            url (str): URL to scrape images from
            scroll (bool): Whether to scroll down the page to load more images
            max_scroll (int): Maximum number of times to scroll
            wait_time (int): Time to wait between actions (in seconds)
            
        Returns:
            list: List of image URLs and their metadata
        """
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(wait_time)
            
            # Scroll down to load more images if needed
            if scroll:
                self._scroll_page(max_scroll, wait_time)
            
            # Find all image elements
            logger.info("Finding image elements")
            img_elements = self.driver.find_elements(By.TAG_NAME, "img")
            logger.info(f"Found {len(img_elements)} image elements")
            
            # Extract image URLs and metadata
            image_data = []
            
            for img in img_elements:
                try:
                    # Get image URL
                    src = img.get_attribute("src")
                    
                    # Try alternative attributes for lazy-loaded images
                    if not src or src.endswith('.gif') or 'data:image/gif' in src:
                        for attr in ["data-src", "data-lazy-src", "data-original", "data-srcset"]:
                            alt_src = img.get_attribute(attr)
                            if alt_src:
                                src = alt_src
                                break
                    
                    if not src:
                        continue
                    
                    # Skip WebP images
                    if src.lower().endswith('.webp') or '.webp?' in src.lower():
                        logger.info(f"Skipping WebP image: {src}")
                        continue
                    
                    # Make sure URL is absolute
                    if not src.startswith(('http://', 'https://', 'data:')):
                        src = urljoin(url, src)
                    
                    # Skip base64 encoded images unless they're large enough
                    if src.startswith('data:'):
                        if len(src) < 1000:  # Skip small base64 images (likely placeholders)
                            continue
                    
                    # Get image metadata for naming
                    alt_text = img.get_attribute("alt") or ""
                    title = img.get_attribute("title") or ""
                    
                    # Add to our list with metadata
                    image_data.append({
                        "url": src,
                        "alt_text": alt_text,
                        "title": title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing image: {e}")
            
            # Remove duplicates while preserving metadata
            unique_urls = set()
            unique_image_data = []
            
            for item in image_data:
                if item["url"] not in unique_urls:
                    unique_urls.add(item["url"])
                    unique_image_data.append(item)
            
            logger.info(f"Found {len(unique_image_data)} unique image URLs")
            
            return unique_image_data
            
        except Exception as e:
            logger.error(f"Error scraping images: {e}")
            return []
    
    def download_images(self, image_data, delay=0.5, max_images=None):
        """
        Download images from URLs
        
        Args:
            image_data (list): List of dictionaries containing image URLs and metadata
            delay (float): Delay between downloads to avoid rate limiting
            max_images (int): Maximum number of images to download (None for all)
            
        Returns:
            list: List of paths to downloaded images
        """
        downloaded_paths = []
        
        # Limit the number of images if specified
        if max_images and max_images < len(image_data):
            image_data = image_data[:max_images]
        
        for i, item in enumerate(image_data):
            try:
                url = item["url"]
                alt_text = item["alt_text"]
                title = item["title"]
                
                # Create a valid filename from metadata or URL
                if title:
                    # Use title for filename if available
                    base_name = self._sanitize_filename(title)
                elif alt_text:
                    # Use alt text if title is not available
                    base_name = self._sanitize_filename(alt_text)
                else:
                    # Fall back to URL-based filename
                    parsed_url = urlparse(url)
                    base_name = os.path.basename(parsed_url.path)
                    base_name = os.path.splitext(base_name)[0]
                    
                    # If filename is empty, create a generic one
                    if not base_name:
                        base_name = f"image_{i}"
                
                # Determine file extension from URL or default to jpg
                parsed_url = urlparse(url)
                path = parsed_url.path
                ext = os.path.splitext(path)[1]
                
                if not ext or ext == '.':
                    ext = '.jpg'  # Default extension
                
                # Create filename
                filename = f"{base_name}{ext}"
                
                # Handle duplicate filenames by adding an index
                counter = 1
                while os.path.exists(os.path.join(self.download_path, filename)):
                    filename = f"{base_name}_{counter}{ext}"
                    counter += 1
                
                # Full path to save the image
                save_path = os.path.join(self.download_path, filename)
                
                # Download the image
                logger.info(f"Downloading image {i+1}/{len(image_data)}: {url}")
                
                # Handle base64 encoded images
                if url.startswith('data:image/'):
                    # Extract the base64 encoded data
                    header, encoded = url.split(",", 1)
                    import base64
                    data = base64.b64decode(encoded)
                    
                    with open(save_path, "wb") as f:
                        f.write(data)
                    
                    downloaded_paths.append(save_path)
                    logger.info(f"Successfully saved base64 image to {save_path}")
                else:
                    # Regular URL download
                    response = requests.get(url, stream=True, timeout=10)
                    
                    # Check if the request was successful
                    if response.status_code == 200:
                        with open(save_path, 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        
                        downloaded_paths.append(save_path)
                        logger.info(f"Successfully downloaded to {save_path}")
                    else:
                        logger.warning(f"Failed to download image, status code: {response.status_code}")
                
                # Add delay to avoid rate limiting
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error downloading image {item['url']}: {e}")
        
        logger.info(f"Downloaded {len(downloaded_paths)} images out of {len(image_data)}")
        return downloaded_paths
    
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
    
    def _sanitize_filename(self, name):
        """
        Sanitize a string to be used as a filename
        
        Args:
            name (str): String to sanitize
            
        Returns:
            str: Sanitized string
        """
        # Replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            name = name.replace(char, '_')
        
        # Limit length and strip whitespace
        name = name.strip()[:100]  # Limit to 100 chars
        
        # If name is empty after sanitizing, use a default
        if not name:
            name = "image"
            
        return name
    
    def close(self):
        """Close the WebDriver"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed")

def scrape_images_from_url(url, download=True, headless=True, max_images=None):
    """
    Scrape images from a URL
    
    Args:
        url (str): URL to scrape images from
        download (bool): Whether to download the images
        headless (bool): Whether to run Chrome in headless mode
        max_images (int): Maximum number of images to download
        
    Returns:
        dict: Dictionary containing image URLs and download paths if applicable
    """
    scraper = ImageScraper(headless=headless)
    
    try:
        # Scrape image URLs and metadata
        image_data = scraper.scrape_images(url)
        
        result = {
            "url": url,
            "image_count": len(image_data),
            "image_data": image_data,
        }
        
        # Download images if requested
        if download and image_data:
            downloaded_paths = scraper.download_images(image_data, max_images=max_images)
            result["downloaded_paths"] = downloaded_paths
            result["downloaded_count"] = len(downloaded_paths)
        
        return result
    
    finally:
        # Always close the WebDriver
        scraper.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape images from a URL")
    parser.add_argument("url", help="URL to scrape images from")
    parser.add_argument("--no-download", action="store_true", help="Don't download images, just get URLs")
    parser.add_argument("--visible", action="store_true", help="Run Chrome in visible mode (not headless)")
    parser.add_argument("--max-images", type=int, help="Maximum number of images to download")
    
    args = parser.parse_args()
    
    result = scrape_images_from_url(
        args.url,
        download=not args.no_download,
        headless=not args.visible,
        max_images=args.max_images
    )
    
    print(f"Found {result['image_count']} images at {args.url}")
    
    if "downloaded_count" in result:
        print(f"Downloaded {result['downloaded_count']} images")
