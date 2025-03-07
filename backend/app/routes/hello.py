from app.routes import bp

@bp.route('/hello', methods=['GET'])
def api_endpoint():
    return {
        "message": "Hello, World!",
        "status": "success"
    }