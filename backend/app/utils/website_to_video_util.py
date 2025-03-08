import os
import logging
import time
from app.utils.text_scraper_util import TextScraper, get_gemini_summary
from app.utils.video_generator_util import VideoGenerator

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='website_to_video.log',
    filemode='a'
)
logger = logging.getLogger(__name__)

def generate_video_from_url(url, max_chars=300):
    """
    Generate a video based on the content of a website URL
    
    Args:
        url (str): The URL of the website to scrape
        max_chars (int): Maximum characters for the Gemini summary
        
    Returns:
        str: Path to the generated video file
    """
    # Create video directory if it doesn't exist
    video_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'video')
    os.makedirs(video_dir, exist_ok=True)
    
    # Generate a unique filename based on timestamp
    timestamp = int(time.time())
    output_path = os.path.join(video_dir, f"video_{timestamp}.mp4")
    
    logger.info(f"Starting video generation process for URL: {url}")
    logger.info(f"Video will be saved to: {output_path}")
    
    # Step 1: Scrape the website text
    logger.info("Initializing text scraper...")
    text_scraper = TextScraper(headless=True)
    
    try:
        # Scrape text content
        logger.info(f"Scraping text from {url}...")
        text_data = text_scraper.scrape_text(url)
        
        # Step 2: Get summary from Gemini
        logger.info("Getting summary from Gemini...")
        summary = get_gemini_summary(text_data, max_chars=max_chars)
        
        # Log the summary
        logger.info(f"Generated summary: {summary}")
        
        # Step 3: Generate video using the summary
        logger.info("Initializing video generator...")
        video_generator = VideoGenerator()
        
        # Create a video prompt based on the summary
        video_prompt = f"Create a 5-second advertisement video for a website about: {summary}"
        logger.info(f"Video prompt: {video_prompt}")
        
        # Generate the video
        logger.info(f"Generating video...")
        video_path = video_generator.generate_video(prompt=video_prompt, output_path=output_path)
        
        logger.info(f"Video generation complete! Video saved to: {video_path}")
        return video_path
        
    except Exception as e:
        logger.error(f"Error in video generation process: {e}")
        raise
    finally:
        # Always close the scraper to release resources
        text_scraper.close() 