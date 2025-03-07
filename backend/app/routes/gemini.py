import os
from google import genai
from flask import request, jsonify
from http import HTTPStatus
from app.routes import bp
from app.utils.error import error_logger
import uuid
from app.utils.types import BasicInfo
from pydantic import ValidationError

@bp.route('/basic_info', methods=['POST'])
def basic_info():
    try:
        data = BasicInfo(**request.get_json())

        return jsonify({
            "status": "success",
            "message": "Basic info received",
            "data": data.model_dump()
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


@bp.route('/api/gemini', methods=['POST', 'GET'])
def gemini_proxy():
    # data = request.get_json()
    # prompt = data.get('prompt', "Explain how AI works")
    prompt = "Explain how AI works"
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return jsonify({
            "status": "error",
            "message": "GEMINI_API_KEY not found in environment variables"
        }), 500
    
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-1.5-pro",
        contents=prompt
    )

    return jsonify({
        "status": "success",
        "response": response.text
    })


