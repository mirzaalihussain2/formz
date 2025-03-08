import time
import logging
import os
from selenium.webdriver.common.by import By
from app.routes.base_scraper import BaseScraper
import requests
import json
import google.genai as genai

# Set up logging to file instead of terminal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='text_scraper.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

class TextScraper(BaseScraper):
    def scrape_text(self, url, scroll=True, max_scroll=5, wait_time=2):
        """
        Scrape text content from a given URL
        
        Args:
            url (str): URL to scrape text from
            scroll (bool): Whether to scroll down the page to load more content
            max_scroll (int): Maximum number of times to scroll
            wait_time (int): Time to wait between actions (in seconds)
            
        Returns:
            dict: Dictionary containing website title, meta description, and text content
        """
        try:
            logger.info(f"Navigating to {url}")
            self.driver.get(url)
            
            # Wait for the page to load
            time.sleep(wait_time)
            
            # Scroll down to load more content if needed
            if scroll:
                self._scroll_page(max_scroll, wait_time)
            
            # Get page title
            title = self.driver.title
            
            # Get meta description
            meta_description = ""
            try:
                meta_tag = self.driver.find_element(By.CSS_SELECTOR, "meta[name='description']")
                meta_description = meta_tag.get_attribute("content")
            except:
                logger.info("No meta description found")
            
            # Extract headings
            headings = []
            for h_level in range(1, 7):
                h_elements = self.driver.find_elements(By.TAG_NAME, f"h{h_level}")
                for h in h_elements:
                    text = h.text.strip()
                    if text:
                        headings.append({
                            "level": h_level,
                            "text": text
                        })
            
            # Extract paragraphs
            paragraphs = []
            p_elements = self.driver.find_elements(By.TAG_NAME, "p")
            for p in p_elements:
                text = p.text.strip()
                if text:
                    paragraphs.append(text)
            
            # Extract list items
            list_items = []
            li_elements = self.driver.find_elements(By.TAG_NAME, "li")
            for li in li_elements:
                text = li.text.strip()
                if text:
                    list_items.append(text)
            
            # Extract button text
            buttons = []
            button_elements = self.driver.find_elements(By.TAG_NAME, "button")
            button_elements.extend(self.driver.find_elements(By.CSS_SELECTOR, "a.btn, .button, [role='button']"))
            for button in button_elements:
                text = button.text.strip()
                if text:
                    buttons.append(text)
            
            # Extract main content (combine all text for summarization)
            all_text = " ".join(paragraphs + [item["text"] for item in headings] + list_items)
            
            return {
                "title": title,
                "meta_description": meta_description,
                "headings": headings,
                "paragraphs": paragraphs,
                "list_items": list_items,
                "buttons": buttons,
                "all_text": all_text
            }
            
        except Exception as e:
            logger.error(f"Error scraping text: {e}")
            return {
                "title": "",
                "meta_description": "",
                "headings": [],
                "paragraphs": [],
                "list_items": [],
                "buttons": [],
                "all_text": ""
            }

def get_gemini_summary(text_data, max_chars=300):
    """
    Send scraped text to Gemini API for summarization
    
    Args:
        text_data (dict): Dictionary containing scraped text data
        max_chars (int): Maximum number of characters for the summary
        
    Returns:
        str: Gemini's summary of the website
    """
    try:
        # Get API key from environment
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            return "Error: Gemini API key not found in environment variables"
        
        # Initialize Gemini client
        client = genai.Client(api_key=api_key)
        
        # Prepare the prompt for Gemini
        title = text_data.get("title", "")
        meta_description = text_data.get("meta_description", "")
        headings = " ".join([h["text"] for h in text_data.get("headings", [])])
        paragraphs = " ".join(text_data.get("paragraphs", []))
        list_items = " ".join(text_data.get("list_items", []))
        
        # Combine the most important elements
        content = f"Title: {title}\nDescription: {meta_description}\nHeadings: {headings}\nContent: {paragraphs}\nList Items: {list_items}"
        
        # Create the prompt
        prompt = f"""Create a concise summary of this website in EXACTLY {max_chars} characters or less.
This summary will be used to generate an advertising video, so focus on:
1. The core value proposition
2. What product/service is being offered
3. Why someone would want it
4. Any unique selling points

Website content:
{content}

IMPORTANT: Your response MUST be {max_chars} characters or less. Count carefully."""
        
        # Call Gemini API directly
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )
        
        # Return the summary
        return response.text
            
    except Exception as e:
        logger.error(f"Error getting Gemini summary: {e}")
        return f"Failed to get summary from Gemini due to an error: {str(e)}"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scrape text from a URL and get a Gemini summary")
    parser.add_argument("url", help="URL to scrape text from")
    parser.add_argument("--visible", action="store_true", help="Run Chrome in visible mode (not headless)")
    parser.add_argument("--max-chars", type=int, default=300, help="Maximum characters for Gemini summary")
    
    args = parser.parse_args()
    
    scraper = TextScraper(headless=not args.visible)
    
    try:
        # Scrape text content (without printing details)
        print(f"Scraping text from {args.url}...")
        text_data = scraper.scrape_text(args.url)
        
        # Get Gemini summary
        print("\nGetting summary from Gemini...")
        summary = get_gemini_summary(text_data, max_chars=args.max_chars)
        
        # Print only the Gemini summary
        print("\n" + "="*50)
        print("WEBSITE SUMMARY")
        print("="*50)
        print(f"\nTitle: {text_data['title']}")
        print(f"\nGemini Summary:")
        print(summary)
        print("\n" + "="*50)
        
    finally:
        scraper.close() 