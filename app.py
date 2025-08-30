from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import threading
import time
from threading import Lock
import mimetypes
from pathlib import Path

app = Flask(__name__)

# Configuration
MOVIES_PATH = ""  # To be set by user
TV_SHOWS_PATH = ""  # To be set by user
PORT = 8035
BANDWIDTH_LIMIT = 10 * 1024 * 1024  # 10 Mbps in bytes per second

# Global state for downloads
download_state = {
    'active_downloads': {},
    'bandwidth_used': 0,
    'lock': Lock()
}

def get_all_files(base_paths):
    """Recursively get all files from the given paths"""
    files = []
    for base_path in base_paths:
        if not os.path.exists(base_path):
            continue
        
        for root, dirs, filenames in os.walk(base_path):
            for filename in filenames:
                full_path = os.path.join(root, filename)
                relative_path = os.path.relpath(full_path, base_path)
                file_size = os.path.getsize(full_path)
                
                files.append({
                    'name': filename,
                    'path': full_path,
                    'relative_path': relative_path,
                    'size': file_size,
                    'size_mb': round(file_size / (1024 * 1024), 2),
                    'type': 'Movie' if base_path == MOVIES_PATH else 'TV Show'
                })
    
    return sorted(files, key=lambda x: (x['type'], x['relative_path']))

@app.route('/')
def index():
    """Main page with file listing"""
    paths = []
    if MOVIES_PATH:
        paths.append(MOVIES_PATH)
    if TV_SHOWS_PATH:
        paths.append(TV_SHOWS_PATH)
    
    files = get_all_files(paths)
    return render_template('index.html', files=files)

@app.route('/api/files')
def api_files():
    """API endpoint to get file list"""
    paths = []
    if MOVIES_PATH:
        paths.append(MOVIES_PATH)
    if TV_SHOWS_PATH:
        paths.append(TV_SHOWS_PATH)
    
    files = get_all_files(paths)
    return jsonify(files)

@app.route('/download/<path:file_path>')
def download_file(file_path):
    """Download a file with bandwidth limiting"""
    full_path = os.path.join('/', file_path)
    
    if not os.path.exists(full_path):
        return "File not found", 404
    
    def generate():
        chunk_size = 8192  # 8KB chunks
        bytes_per_second = BANDWIDTH_LIMIT
        delay_per_chunk = chunk_size / bytes_per_second
        
        with open(full_path, 'rb') as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                
                # Bandwidth limiting
                time.sleep(delay_per_chunk)
                yield chunk
    
    filename = os.path.basename(full_path)
    mimetype = mimetypes.guess_type(full_path)[0] or 'application/octet-stream'
    
    return Response(
        generate(),
        mimetype=mimetype,
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(os.path.getsize(full_path))
        }
    )

@app.route('/api/download-status')
def download_status():
    """Get current download status"""
    with download_state['lock']:
        return jsonify({
            'active_downloads': len(download_state['active_downloads']),
            'bandwidth_used_mbps': round(download_state['bandwidth_used'] / (1024 * 1024), 2)
        })

if __name__ == '__main__':
    print("File Download Server")
    print("===================")
    print(f"Server will run on port {PORT}")
    print()
    
    # Get paths from user
    if not MOVIES_PATH:
        MOVIES_PATH = input("Enter the path to your Movies folder: ").strip()
    if not TV_SHOWS_PATH:
        TV_SHOWS_PATH = input("Enter the path to your TV Shows folder: ").strip()
    
    print(f"Movies path: {MOVIES_PATH}")
    print(f"TV Shows path: {TV_SHOWS_PATH}")
    print(f"Bandwidth limit: {BANDWIDTH_LIMIT / (1024 * 1024)} Mbps")
    print()
    print(f"Starting server at http://0.0.0.0:{PORT}")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)