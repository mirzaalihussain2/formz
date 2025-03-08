from flask import request, jsonify, send_file
from app.routes import bp
from app.utils.website_to_video_util import generate_video_from_url
import os

@bp.route('/website-to-video', methods=['GET'])
def website_to_video_route():
    """
    Generate a video from a website URL and return it directly
    
    Query parameters:
        url (required): The URL of the website to generate a video from
        max_chars (optional): Maximum characters for the summary (default: 300)
    
    Returns:
        Video file directly to the browser
    """
    # Get URL from query parameters
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            'status': 'error',
            'message': 'URL parameter is required'
        }), 400
    
    # Get optional max_chars parameter
    try:
        max_chars = int(request.args.get('max_chars', 300))
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'max_chars must be an integer'
        }), 400
    
    try:
        # Generate video from URL
        video_path = generate_video_from_url(url=url, max_chars=max_chars)
        
        # Return the video file directly
        if os.path.exists(video_path):
            # Get the filename from the path
            filename = os.path.basename(video_path)
            
            # Return the file with appropriate headers for download
            return send_file(
                video_path,
                mimetype='video/mp4',
                as_attachment=True,
                download_name=filename
            )
        else:
            return jsonify({
                'status': 'error',
                'message': 'Video file not found'
            }), 404
            
    except Exception as e:
        # Return error response
        return jsonify({
            'status': 'error',
            'message': f'Error generating video: {str(e)}'
        }), 500 