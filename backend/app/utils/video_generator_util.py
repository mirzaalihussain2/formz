import os
import requests
import replicate
import tempfile
import shutil
import logging
import time
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables from the correct location
# This should match how your Flask app loads environment variables
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '.env.local'))

class VideoGenerator:
    """
    A simple class to generate videos using Replicate's API
    """
    
    def __init__(self):
        """Initialize the VideoGenerator with Replicate API token from environment"""
        # Get API token from environment
        self.api_token = os.environ.get("REPLICATE_API_TOKEN")
        
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN not found in environment variables")
        
        # Set the API token for the replicate client
        os.environ["REPLICATE_API_TOKEN"] = self.api_token
    
    def generate_video(self, prompt=None, output_path="./generated_video.mp4", max_retries=2, chunk_size=1024*1024):
        """
        Generate a video based on the provided prompt and save to the specified path
        
        Args:
            prompt (str): The prompt to use for video generation. If None, a default prompt is used.
            output_path (str): Path where the generated video will be saved
            max_retries (int): Maximum number of retries if generation fails
            chunk_size (int): Size of chunks to download to reduce memory usage
            
        Returns:
            str: Path to the generated video file
        """
        # Use default prompt if none provided
        if prompt is None:
            prompt = "A trendy 5-second TikTok advertisement showing a sleek smartphone with animated apps floating around it. Fast-paced, colorful, modern aesthetic with dynamic transitions."
        
        logger.info(f"Generating video with prompt: {prompt}")
        
        # Use the correct model ID from Replicate docs
        model = "wan-video/wan-2.1-1.3b"
        
        # Ensure the directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Run the model with retries
        for attempt in range(max_retries + 1):
            try:
                # The output is a URL to the video
                output = replicate.run(
                    model,
                    input={
                        "prompt": prompt,
                        # Add any other parameters the model accepts
                        "negative_prompt": "poor quality, blurry, low resolution",
                        # Add parameters to reduce quality/size if needed
                        "fps": 24,  # Lower FPS to reduce size
                        "width": 512,  # Smaller width
                        "height": 512,  # Smaller height
                    }
                )
                
                logger.info(f"Video generated successfully!")
                
                # Download the video in chunks to reduce memory usage
                with requests.get(output, stream=True) as r:
                    r.raise_for_status()
                    with open(output_path, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=chunk_size): 
                            f.write(chunk)
                
                logger.info(f"Video saved to {output_path}")
                return output_path
                
            except Exception as e:
                logger.error(f"Error generating video (attempt {attempt+1}/{max_retries+1}): {str(e)}")
                if attempt < max_retries:
                    logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                else:
                    logger.error("Max retries reached, giving up.")
                    # Create a fallback video or return an error path
                    self._create_fallback_video(output_path)
                    return output_path
    
    def _create_fallback_video(self, output_path):
        """Create a fallback video if generation fails"""
        try:
            # Use a very simple model or just copy a pre-made fallback video
            fallback_path = os.path.join(os.path.dirname(__file__), "fallback_video.mp4")
            if os.path.exists(fallback_path):
                shutil.copy(fallback_path, output_path)
                logger.info(f"Used fallback video at {output_path}")
            else:
                # Create an empty file as last resort
                with open(output_path, 'wb') as f:
                    f.write(b'')
                logger.warning(f"Created empty file at {output_path} as fallback")
        except Exception as e:
            logger.error(f"Error creating fallback video: {str(e)}")
            # Just ensure the file exists
            with open(output_path, 'wb') as f:
                f.write(b'') 