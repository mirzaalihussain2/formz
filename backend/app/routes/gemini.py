import os
from google import genai
from flask import request, jsonify
from app.routes import bp

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


