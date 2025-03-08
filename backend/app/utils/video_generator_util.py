import os
import requests
import replicate
import tempfile
import shutil
from dotenv import load_dotenv

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
    
    def generate_video(self, prompt=None, output_path="./generated_video.mp4"):
        """
        Generate a video based on the provided prompt and save to the specified path
        
        Args:
            prompt (str): The prompt to use for video generation. If None, a default prompt is used.
            output_path (str): Path where the generated video will be saved
            
        Returns:
            str: Path to the generated video file
        """
        # Use default prompt if none provided
        if prompt is None:
            prompt = "A trendy 5-second TikTok advertisement showing a sleek smartphone with animated apps floating around it. Fast-paced, colorful, modern aesthetic with dynamic transitions."
        
        print(f"Generating video with prompt: {prompt}")
        
        # Use the correct model ID from Replicate docs
        model = "wan-video/wan-2.1-1.3b"
        
        # Run the model
        try:
            # The output is a file-like object that can be read directly
            output = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    # Add any other parameters the model accepts
                    "negative_prompt": "poor quality, blurry, low resolution"
                }
            )
            
            print(f"Video generated successfully!")
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Write the output directly to a file
            with open(output_path, "wb") as file:
                file.write(output.read())
                
            print(f"Video saved to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            raise 