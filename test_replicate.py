#!/usr/bin/env python3
"""
Simple test script to verify that the Replicate API integration works.
This script generates a 5-second video using a hardcoded prompt.

Usage:
    python test_replicate.py --api-key YOUR_API_KEY --output test_video.mp4
"""

import os
import sys
import argparse
from backend.app.routes.video_generator import test_video_generation

def main():
    parser = argparse.ArgumentParser(description="Test Replicate API for video generation")
    parser.add_argument("--api-key", help="Replicate API key (or set REPLICATE_API_TOKEN env var)")
    parser.add_argument("--output", "-o", default="test_video.mp4", help="Path to save the output video")
    args = parser.parse_args()
    
    # Set API key if provided
    api_token = None
    if args.api_key:
        api_token = args.api_key
        os.environ["REPLICATE_API_TOKEN"] = args.api_key
    
    # Check if API key is available
    if not os.environ.get("REPLICATE_API_TOKEN") and not api_token:
        print("Error: Replicate API key not found. Please provide it with --api-key or set the REPLICATE_API_TOKEN environment variable.")
        sys.exit(1)
    
    print("Testing Replicate API for video generation...")
    try:
        video_path = test_video_generation(api_token=api_token, output_path=args.output)
        print(f"Success! Video saved to: {video_path}")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 