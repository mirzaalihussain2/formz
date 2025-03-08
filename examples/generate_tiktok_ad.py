#!/usr/bin/env python3
"""
Example script to generate a TikTok ad using the Replicate API.
This demonstrates the basic usage of the VideoGenerator class.

Usage:
    python generate_tiktok_ad.py --output my_ad.mp4
"""

import os
import sys
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.routes.video_generator import VideoGenerator, generate_sample_tiktok_ad

def main():
    parser = argparse.ArgumentParser(description="Generate a sample TikTok ad using Replicate")
    parser.add_argument("--output", "-o", default="tiktok_ad.mp4", help="Path to save the output video")
    parser.add_argument("--api-key", help="Replicate API key (or set REPLICATE_API_TOKEN env var)")
    args = parser.parse_args()
    
    # Set API key if provided
    if args.api_key:
        os.environ["REPLICATE_API_TOKEN"] = args.api_key
    
    # Check if API key is available
    if not os.environ.get("REPLICATE_API_TOKEN"):
        print("Error: Replicate API key not found. Please provide it with --api-key or set the REPLICATE_API_TOKEN environment variable.")
        sys.exit(1)
    
    print(f"Generating sample TikTok ad...")
    try:
        video_path = generate_sample_tiktok_ad(args.output)
        print(f"Success! Video saved to: {video_path}")
    except Exception as e:
        print(f"Error generating video: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 