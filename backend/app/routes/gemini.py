import os
from google import genai
from flask import request, jsonify
from http import HTTPStatus
from app.routes import bp
from app.utils.error import error_logger
import uuid
from app.utils.types import BasicInfo
from pydantic import ValidationError
import pandas as pd
from tabulate import tabulate

system_prompt = """
You are TikTok's Interest Category Matching System. Your task is to analyze URLs and identify the most relevant interest categories from the provided CSV database with perfect accuracy.

CORE REQUIREMENT: You must NEVER invent or modify categories. Only use categories that exist EXACTLY in the CSV.

PROCESS:
1. Analyze the provided URL to understand its content and purpose
2. Search the CSV data for relevant interest categories
3. Select ONLY categories that EXIST VERBATIM in the CSV
4. Return exactly 4 most relevant categories (or fewer if 4 relevant ones don't exist)

VERIFICATION PROTOCOL (perform for EACH category before including):
- Confirm the exact Interest Category ID exists in the CSV (e.g., "C23107")
- Verify the Primary, Secondary, and Tertiary Interest Categories match EXACTLY what's in the CSV
- Copy the text VERBATIM - no modifications whatsoever
- If uncertain whether a category exists exactly as written, DO NOT include it

OUTPUT FORMAT: Return a JSON array with your selected categories:
[
    {
        "Interest_Category_ID": "C23107",
        "Primary_Interest_Category": "News & Entertainment",
        "Secondary_Interest_Category": "Environmental Protection",
        "Tertiary_Interest_Category": "Environmental Protection"
    },
    ... additional categories (maximum 4 total)
]

ERROR PREVENTION:
- NEVER create or modify categories
- NEVER combine categories
- Copy text EXACTLY as it appears in the CSV
- It is better to return fewer than 4 categories than to invent categories

FINAL VALIDATION: Before submitting, verify each category one final time against the CSV to ensure it exists EXACTLY as written."""


def csv_to_markdown(csv_path):
    df = pd.read_csv(csv_path)
    markdown_table = tabulate(df, headers=df.columns, tablefmt="pipe", showindex=False)
    return "\n\nCSV DATABASE:\n" + markdown_table

@bp.route('/gemini', methods=['GET'])
def scrape_webpage():
    try:
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({
                "status": "error",
                "message": "GEMINI_API_KEY not found in environment variables"
            }), 500
        
        client = genai.Client(api_key=api_key)

        # Create proper content structure using the genai.types module
        response = client.models.generate_content(
            model="gemini-1.5-pro",
            contents="Scrape this webpage: https://www.brompton.com/",
            config=genai.types.GenerateContentConfig(
                system_instruction="Scrape this webpage"
            )
        )

        return jsonify({
            "status": "success",
            "response": response.text
        })

    except ValidationError as error:
        return jsonify({
            "status": "error",
            "message": "Invalid input data",
            "errors": error.errors()
        }), HTTPStatus.BAD_REQUEST
        
    except Exception as error:
        error_id = str(uuid.uuid4())
        error_logger(error, error_id)
        
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {error}",
            "error_id": error_id
        }), HTTPStatus.INTERNAL_SERVER_ERROR

@bp.route('/basic_info', methods=['POST'])
def basic_info():
    try:
        # parse params from request
        data = BasicInfo(**request.get_json())
        website = data.website
        budget = data.budget
        start_date = data.start_date
        end_date = data.end_date

        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        csv_path = os.path.join(project_root, "data", "tiktok_interest_categories.csv")

        # csv to markdown
        tiktok_categories = csv_to_markdown(csv_path)
        
        # Create a user prompt that includes all the required information
        user_prompt = f"""
        Please analyze the following website and identify the most relevant TikTok interest categories:
        
        Website: {website}
        Campaign Budget: {budget}
        Campaign Start Date: {start_date}
        Campaign End Date: {end_date}
        
        Based on the website content, select the most appropriate interest categories from the list below:
        
        {tiktok_categories}
        """

        api_key = os.getenv('GEMINI_API_KEY')
        
        if not api_key:        
            return jsonify({
                "status": "error",
                "message": "GEMINI_API_KEY not found in environment variables"
            }), 500
        
        client = genai.Client(api_key=api_key)

        # Fix the content structure for this endpoint too
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )

        # Include the Gemini response in your return data
        return jsonify({
            "status": "success",
            "message": "Basic info received",
            "data": data.model_dump(),
            "categories": response.text
        }), HTTPStatus.OK
    
    except ValidationError as error:
        return jsonify({
            "status": "error",
            "message": "Invalid input data",
            "errors": error.errors()
        }), HTTPStatus.BAD_REQUEST
        
    except Exception as error:
        error_id = str(uuid.uuid4())
        error_logger(error, error_id)
        
        return jsonify({
            "status": "error",
            "message": f"An error occurred: {error}",
            "error_id": error_id
        }), HTTPStatus.INTERNAL_SERVER_ERROR

