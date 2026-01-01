"""
Local File Server for LAN File Sharing
Runs on port 5001 with token-based authentication
Provides /info, /list, /download, /upload endpoints
Includes UDP discovery responder on port 5002
"""

import os
import socket
import json
import threading
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "SystemMonitorShared")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip', 'rar', '7z', 'mp3', 'mp4', 'avi', 'mkv'}
MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global token (will be set from main_gui.py)
AUTH_TOKEN = None

# Notification queue (in-memory storage)
notifications = []
notification_id_counter = 0


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def verify_token():
    """Verify authentication token from request"""
    token = request.headers.get('X-Local-Token') or request.args.get('token')
    if not token or token != AUTH_TOKEN:
        return False
    return True


@app.before_request
def check_auth():
    """Check authentication before processing request"""
    # Skip auth check for /info endpoint
    if request.path == '/info':
        return None
    
    if not verify_token():
        return jsonify({'error': 'Unauthorized', 'message': 'Invalid or missing token'}), 401


@app.route('/info', methods=['GET'])
def get_info():
    """Get server information (no auth required)"""
    hostname = socket.gethostname()
    local_ip = get_local_ip()
    return jsonify({
        'service': 'SystemMonitor File Server',
        'version': '1.0',
        'hostname': hostname,
        'ip': local_ip,
        'port': 5001,
        'upload_folder': UPLOAD_FOLDER
    })


@app.route('/list', methods=['GET'])
def list_files():
    """List all files in the shared folder"""
    try:
        files = []
        for filename in os.listdir(UPLOAD_FOLDER):
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(filepath):
                stat = os.stat(filepath)
                files.append({
                    'name': filename,
                    'size': stat.st_size,
                    'modified': stat.st_mtime
                })
        
        return jsonify({
            'success': True,
            'files': files,
            'total': len(files)
        })
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Download a specific file"""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        return send_file(filepath, as_attachment=True, download_name=safe_filename)
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload a file to the shared folder"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Handle duplicate filenames
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(filepath):
                filename = f"{base}_{counter}{ext}"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                counter += 1
            
            file.save(filepath)
            logger.info(f"File uploaded: {filename}")
            
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully',
                'filename': filename,
                'size': os.path.getsize(filepath)
            })
        else:
            return jsonify({'error': 'File type not allowed'}), 400
            
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    """Delete a file from the shared folder"""
    try:
        safe_filename = secure_filename(filename)
        filepath = os.path.join(UPLOAD_FOLDER, safe_filename)
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found'}), 404
        
        os.remove(filepath)
        logger.info(f"File deleted: {safe_filename}")
        
        return jsonify({
            'success': True,
            'message': 'File deleted successfully'
        })
    except Exception as e:
        logger.error(f"Error deleting file: {e}")
        return jsonify({'error': str(e)}), 500


def get_local_ip():
    """Get the local IP address"""
    try:
        # Create a socket to get the local IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"


def udp_discovery_responder(token):
    """UDP responder for device discovery on LAN"""
    udp_port = 5002
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', udp_port))
    
    logger.info(f"UDP discovery listening on port {udp_port}")
    
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            message = data.decode('utf-8')
            
            if message == "SYSTEMMONITOR_DISCOVER":
                # Respond with connection info
                response = {
                    'service': 'SystemMonitor',
                    'ip': get_local_ip(),
                    'port': 5001,
                    'hostname': socket.gethostname()
                }
                sock.sendto(json.dumps(response).encode('utf-8'), addr)
                logger.info(f"Discovery request from {addr}")
        except Exception as e:
            logger.error(f"UDP discovery error: {e}")


def start_server(token, host='0.0.0.0', port=5001):
    """Start the Flask server and UDP discovery"""
    global AUTH_TOKEN
    AUTH_TOKEN = token
    
    # Start UDP discovery in background thread
    udp_thread = threading.Thread(target=udp_discovery_responder, args=(token,), daemon=True)
    udp_thread.start()
    
    # Start Flask server
    logger.info(f"Starting file server on {host}:{port}")
    logger.info(f"Shared folder: {UPLOAD_FOLDER}")
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    # For testing
    import secrets
    test_token = secrets.token_urlsafe(32)
    print(f"Test token: {test_token}")
    start_server(test_token)
