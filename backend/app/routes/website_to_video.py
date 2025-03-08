import os
import argparse
from typing import Optional, List
import tempfile

from .image_scraper import ImageScraper, scrape_images_from_url
from .text_scraper import TextScraper, get_gemini_summary
from .video_generator import VideoGenerator

def website_to_video(
    url: str,
    output_path: Optional[str] = None,
    max_images: int = 5,
    max_chars: int = 300,
    video_duration: int = 5,
    headless: bool = True
) -> str:
    """
    Convert a website to a video by:
    1. Scraping images from the website
    2. Scraping text and generating a summary
    3. Using both to generate a video with Replicate
    
    Args:
        url: URL of the website to scrape
        output_path: Path to save the output video
        max_images: Maximum number of images to scrape
        max_chars: Maximum characters for the text summary
        video_duration: Duration of the video in seconds
        headless: Whether to run the browser in headless mode
        
    Returns:
        Path to the generated video
    """
    print(f"Converting website {url} to video...")
    
    # Create temporary directory for downloaded images
    temp_dir = tempfile.mkdtemp()
    image_download_path = os.path.join(temp_dir, "images")
    os.makedirs(image_download_path, exist_ok=True)
    
    # Initialize scrapers
    image_scraper = ImageScraper(headless=headless, download_path=image_download_path)
    text_scraper = TextScraper(headless=headless)
    
    try:
        # Step 1: Scrape images
        print(f"Scraping images from {url}...")
        image_results = image_scraper.scrape_images(url)
        
        # Download and filter images
        downloaded_images = image_scraper.download_and_filter_images(
            image_results["image_urls"],
            max_images=max_images,
            min_width=200,
            min_height=200
        )
        
        image_paths = [os.path.join(image_download_path, img) for img in downloaded_images]
        print(f"Downloaded {len(image_paths)} images")
        
        # Step 2: Scrape text and get summary
        print(f"Scraping text from {url}...")
        text_data = text_scraper.scrape_text(url)
        
        # Get summary
        print("Generating text summary...")
        summary = get_gemini_summary(text_data, max_chars=max_chars)
        
        # Step 3: Generate video
        print("Generating video from scraped content...")
        
        # Create a prompt combining the website title and summary
        title = text_data.get("title", "Website")
        prompt = f"Create a professional video advertisement for {title}. {summary} Show the following visual elements: "
        
        # Add descriptions of the images to the prompt
        if image_paths:
            prompt += "Include visuals of: "
            for i, _ in enumerate(image_paths[:3]):  # Limit to first 3 images to keep prompt reasonable
                prompt += f"image {i+1}, "
        
        prompt += "Make it engaging, modern, and suitable for social media."
        
        # Initialize video generator and create video
        video_generator = VideoGenerator()
        final_video_path = video_generator.generate_video(
            prompt=prompt,
            images=image_paths[:3],  # Use up to 3 images as reference
            output_path=output_path,
            duration_in_seconds=video_duration,
            width=576,  # TikTok portrait mode
            height=1024,
            fps=24
        )
        
        print(f"Video generation complete! Saved to: {final_video_path}")
        return final_video_path
        
    finally:
        # Close browsers
        image_scraper.close()
        text_scraper.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert a website to a video")
    parser.add_argument("url", help="URL of the website to scrape")
    parser.add_argument("--output", "-o", help="Path to save the output video")
    parser.add_argument("--max-images", type=int, default=5, help="Maximum number of images to scrape")
    parser.add_argument("--max-chars", type=int, default=300, help="Maximum characters for the text summary")
    parser.add_argument("--duration", type=int, default=5, help="Duration of the video in seconds")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser in visible mode")
    
    args = parser.parse_args()
    
    video_path = website_to_video(
        url=args.url,
        output_path=args.output,
        max_images=args.max_images,
        max_chars=args.max_chars,
        video_duration=args.duration,
        headless=args.headless
    )
    
    print(f"Final video saved to: {video_path}") 