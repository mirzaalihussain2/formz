import os
import time
import requests
import io
from selenium.webdriver.common.by import By
from urllib.parse import urljoin, urlparse
import logging
from PIL import Image
import numpy as np
import base64
from app.routes.base_scraper import BaseScraper

# Set up logging
logger = logging.getLogger(__name__)

class ImageScraper(BaseScraper):
    def __init__(self, headless=True, download_path="./downloaded_images"):
        """
        Initialize the image scraper with Selenium WebDriver
        
        Args:
            headless (bool): Whether to run Chrome in headless mode
            download_path (str): Path to save downloaded images
        """
        super().__init__(headless=headless)
        self.download_path = download_path
        
        # Create download directory if it doesn't exist
        if not os.path.exists(download_path):
            os.makedirs(download_path)
            
    def scrape_images(self, url, scroll=True, max_scroll=5, wait_time=2):
        """
        Scrape images from a given URL
        
        Args:
            url (str): URL to scrape images from
            scroll (bool): Whether to scroll down the page to load more images
            max_scroll (int): Maximum number of times to scroll
            wait_time (int): Time to wait between actions (in seconds)
            
        Returns:
            list: List of image URLs
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
            
            # Extract image URLs
            image_urls = []
            
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
                    
                    # Get metadata for naming
                    alt_text = img.get_attribute("alt") or ""
                    title = img.get_attribute("title") or ""
                    
                    # Add to our list with metadata
                    image_urls.append({
                        "url": src,
                        "alt_text": alt_text,
                        "title": title
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing image: {e}")
            
            # Remove duplicates
            unique_urls = []
            seen = set()
            
            for item in image_urls:
                if item["url"] not in seen:
                    seen.add(item["url"])
                    unique_urls.append(item)
            
            logger.info(f"Found {len(unique_urls)} unique image URLs")
            
            return unique_urls
            
        except Exception as e:
            logger.error(f"Error scraping images: {e}")
            return []
    
    def download_and_filter_images(self, image_urls, delay=0.5, max_images=None, 
                                  min_width=200, min_height=200, min_filesize=5000, max_filesize=10000000):
        """
        Download and filter images in one step, only saving those that pass the filter
        
        Args:
            image_urls (list): List of dictionaries containing image URLs and metadata
            delay (float): Delay between downloads to avoid rate limiting
            max_images (int): Maximum number of images to process (None for all)
            min_width (int): Minimum width in pixels
            min_height (int): Minimum height in pixels
            min_filesize (int): Minimum file size in bytes
            max_filesize (int): Maximum file size in bytes
            
        Returns:
            list: List of paths to saved (filtered) images
        """
        saved_paths = []
        
        # Limit the number of images if specified
        if max_images and max_images < len(image_urls):
            image_urls = image_urls[:max_images]
        
        total_processed = 0
        total_filtered = 0
        
        for i, item in enumerate(image_urls):
            try:
                url = item["url"]
                alt_text = item.get("alt_text", "")
                title = item.get("title", "")
                
                logger.info(f"Processing image {i+1}/{len(image_urls)}: {url}")
                total_processed += 1
                
                # Download image to memory first
                if url.startswith('data:image/'):
                    # Handle base64 encoded images
                    header, encoded = url.split(",", 1)
                    image_data = base64.b64decode(encoded)
                    content_length = len(image_data)
                else:
                    # Regular URL download
                    response = requests.get(url, stream=True, timeout=10)
                    
                    # Check if the request was successful
                    if response.status_code != 200:
                        logger.warning(f"Failed to download image, status code: {response.status_code}")
                        continue
                    
                    # Get content length for initial file size check
                    content_length = int(response.headers.get('content-length', 0))
                    
                    # If content length header is available, do initial file size check
                    if content_length > 0 and (content_length < min_filesize or content_length > max_filesize):
                        logger.info(f"Skipping {url}: file size {content_length} bytes outside range")
                        continue
                    
                    # Get the image data
                    image_data = response.content
                
                # Check file size if we couldn't get it from headers
                if content_length == 0:
                    content_length = len(image_data)
                    if content_length < min_filesize or content_length > max_filesize:
                        logger.info(f"Skipping {url}: file size {content_length} bytes outside range")
                        continue
                
                # Load image into memory to check dimensions and quality
                try:
                    img = Image.open(io.BytesIO(image_data))
                    
                    # Check dimensions
                    width, height = img.size
                    if width < min_width or height < min_height:
                        logger.info(f"Skipping {url}: dimensions {width}x{height} too small")
                        continue
                    
                    # Check if image is mostly empty/white
                    try:
                        img_array = np.array(img.convert('RGB'))
                        std_dev = np.std(img_array)
                        
                        # Skip images with very low variation (likely blank/solid color)
                        if std_dev < 20:
                            logger.info(f"Skipping {url}: low variation (std_dev={std_dev:.2f})")
                            continue
                    except Exception as e:
                        logger.warning(f"Error analyzing image content: {e}")
                    
                    # Image passed all filters, now save it
                    
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
                    
                    # Determine file extension from URL or image format
                    if hasattr(img, 'format') and img.format:
                        ext = f".{img.format.lower()}"
                    else:
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
                    
                    # Save the image
                    with open(save_path, 'wb') as f:
                        f.write(image_data)
                    
                    saved_paths.append(save_path)
                    total_filtered += 1
                    logger.info(f"Saved filtered image to {save_path}")
                    
                except Exception as e:
                    logger.error(f"Error processing image data: {e}")
                    continue
                
                # Add delay to avoid rate limiting
                time.sleep(delay)
                
            except Exception as e:
                logger.error(f"Error processing image {url}: {e}")
        
        logger.info(f"Processed {total_processed} images, saved {total_filtered} filtered images")
        return saved_paths
    
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
        # Scrape image URLs
        image_urls = scraper.scrape_images(url)
        
        result = {
            "url": url,
            "image_count": len(image_urls),
            "image_urls": image_urls,
        }
        
        # Download and filter images if requested
        if download and image_urls:
            filtered_paths = scraper.download_and_filter_images(image_urls, max_images=max_images)
            result["filtered_paths"] = filtered_paths
            result["filtered_count"] = len(filtered_paths)
        
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
    
    if "filtered_count" in result:
        print(f"Downloaded and filtered {result['filtered_count']} quality images") 