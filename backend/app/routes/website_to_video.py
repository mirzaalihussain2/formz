from flask import request, jsonify, send_file
from app.routes import bp
from app.utils.website_to_video_util import generate_video_from_url, get_video_status
import os
import time

@bp.route('/website-to-video', methods=['GET'])
def website_to_video_route():
    """
    Generate a video from a website URL and return it directly
    
    Query parameters:
        url (required): The URL of the website to generate a video from
        max_chars (optional): Maximum characters for the summary (default: 300)
        async (optional): Whether to generate the video asynchronously (default: true)
        wait (optional): Whether to wait for the video to be generated (default: false)
    
    Returns:
        Video file directly to the browser or task ID if async
    """
    # Get URL from query parameters
    url = request.args.get('url')
    
    if not url:
        return jsonify({
            'status': 'error',
            'message': 'URL parameter is required'
        }), 400
    
    # Get optional parameters
    try:
        max_chars = int(request.args.get('max_chars', 300))
        async_mode = request.args.get('async', 'true').lower() == 'true'
        wait = request.args.get('wait', 'false').lower() == 'true'
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'max_chars must be an integer'
        }), 400
    
    try:
        # Generate video from URL
        result = generate_video_from_url(url=url, max_chars=max_chars, async_mode=async_mode)
        
        # If async mode and not waiting, return task ID
        if async_mode and not wait:
            return jsonify({
                'status': 'processing',
                'task_id': result['task_id'],
                'message': 'Video generation started. Use the status endpoint to check progress.'
            })
        
        # If async mode and waiting, poll for completion
        if async_mode and wait:
            task_id = result['task_id']
            video_path = result['output_path']
            max_wait_time = 60  # Maximum wait time in seconds
            poll_interval = 2   # Poll interval in seconds
            
            elapsed_time = 0
            while elapsed_time < max_wait_time:
                status = get_video_status(task_id)
                if status['status'] == 'completed':
                    break
                elif status['status'] == 'failed':
                    return jsonify({
                        'status': 'error',
                        'message': f'Video generation failed: {status.get("error", "Unknown error")}'
                    }), 500
                
                time.sleep(poll_interval)
                elapsed_time += poll_interval
            
            if elapsed_time >= max_wait_time:
                return jsonify({
                    'status': 'timeout',
                    'task_id': task_id,
                    'message': 'Video generation is taking longer than expected. Check status endpoint.'
                })
        else:
            # Synchronous mode - result is the video path
            video_path = result
        
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

@bp.route('/website-to-video/status/<task_id>', methods=['GET'])
def video_status_route(task_id):
    """
    Get the status of a video generation task
    
    Path parameters:
        task_id: The ID of the task to check
        
    Returns:
        JSON with task status
    """
    status = get_video_status(task_id)
    
    if status['status'] == 'not_found':
        return jsonify({
            'status': 'error',
            'message': f'Task ID {task_id} not found'
        }), 404
    
    # If completed, include the video URL
    if status['status'] == 'completed':
        video_path = status['output_path']
        filename = os.path.basename(video_path)
        video_url = f"/download-video/{filename}"
        status['video_url'] = video_url
    
    return jsonify(status)

@bp.route('/download-video/<filename>', methods=['GET'])
def download_video_route(filename):
    """
    Download a generated video by filename
    
    Path parameters:
        filename: The filename of the video to download
        
    Returns:
        Video file directly to the browser
    """
    video_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'video')
    video_path = os.path.join(video_dir, filename)
    
    if os.path.exists(video_path):
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