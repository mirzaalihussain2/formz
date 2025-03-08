# Website to Video Generator

This project provides tools to:
1. Scrape images from websites
2. Extract and summarize text content
3. Generate videos using AI

## Quick Start - Testing Replicate API

To test if the Replicate API integration works correctly:

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the test script:
```bash
python test_replicate.py --api-key YOUR_REPLICATE_API_KEY --output test_video.mp4
```

This will generate a simple 5-second video using a hardcoded prompt and save it to the specified output path.

## Getting a Replicate API Key

1. Sign up for an account at [Replicate](https://replicate.com/)
2. Navigate to your account settings
3. Generate an API token
4. Use this token with the `--api-key` parameter or set it as the `REPLICATE_API_TOKEN` environment variable

## Project Structure

- `backend/app/routes/video_generator.py`: Core functionality for generating videos using Replicate
- `backend/app/routes/image_scraper.py`: Tools for scraping images from websites
- `backend/app/routes/text_scraper.py`: Tools for extracting and summarizing text from websites
- `test_replicate.py`: Simple test script for the Replicate API integration

## Full Website-to-Video Pipeline

The full pipeline for converting websites to videos is still under development. Currently, you can test the individual components:

1. Image scraping
2. Text extraction and summarization
3. Video generation (via the test script)

Stay tuned for updates on the complete pipeline integration.
