#!/usr/bin/env python3
"""
Example script to convert a website to a video using our pipeline.
This demonstrates the full process of:
1. Scraping images from a website
2. Scraping text and generating a summary
3. Using both to generate a video with Replicate

Usage:
    python website_to_video.py https://example.com --output my_video.mp4
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.routes.website_to_video import website_to_video

def main():
    parser = argparse.ArgumentParser(description="Convert a website to a video")
    parser.add_argument("url", help="URL of the website to scrape")
    parser.add_argument("--output", "-o", help="Path to save the output video")
    parser.add_argument("--max-images", type=int, default=5, help="Maximum number of images to scrape")
    parser.add_argument("--max-chars", type=int, default=300, help="Maximum characters for the text summary")
    parser.add_argument("--duration", type=int, default=5, help="Duration of the video in seconds")
    parser.add_argument("--no-headless", action="store_false", dest="headless", help="Run browser in visible mode")
    parser.add_argument("--api-key", help="Replicate API key (or set REPLICATE_API_TOKEN env var)")
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["REPLICATE_API_TOKEN"] = args.api_key
    
    # Check if API key is available
    if not os.environ.get("REPLICATE_API_TOKEN"):
        print("Error: Replicate API key not found. Please provide it with --api-key or set the REPLICATE_API_TOKEN environment variable.")
        sys.exit(1)
    
    try:
        video_path = website_to_video(
            url=args.url,
            output_path=args.output,
            max_images=args.max_images,
            max_chars=args.max_chars,
            video_duration=args.duration,
            headless=args.headless
        )
        
        print(f"Success! Video saved to: {video_path}")
    except Exception as e:
        print(f"Error converting website to video: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 