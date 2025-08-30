from flask import Flask, render_template, request, jsonify, send_file, Response
import os
import threading
import time
from threading import Lock
import mimetypes
from pathlib import Path
import json
import logging
from datetime import datetime

app = Flask(__name__)

# Load configuration
def load_config():
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("Warning: config.json not found, using defaults")
        return {
            "movies_path": "",
            "tv_shows_path": "",
            "port": 8035,
            "bandwidth_limit_mbps": 10,
            "allowed_extensions": [".mp4", ".mkv", ".avi", ".mov", ".m4v", ".wmv", ".flv", ".webm"],
            "max_concurrent_downloads": 3,
            "chunk_size": 8192
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing config.json: {e}")
        exit(1)

config = load_config()
MOVIES_PATH = config.get('movies_path', '')
TV_SHOWS_PATH = config.get('tv_shows_path', '')
PORT = config.get('port', 8035)
BANDWIDTH_LIMIT = config.get('bandwidth_limit_mbps', 10) * 1024 * 1024
ALLOWED_EXTENSIONS = config.get('allowed_extensions', [".mp4", ".mkv", ".avi", ".mov"])
MAX_CONCURRENT_DOWNLOADS = config.get('max_concurrent_downloads', 3)
CHUNK_SIZE = config.get('chunk_size', 8192)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('plexdownloader.log'),
        logging.StreamHandler()
    ]
)

# Global state for downloads
download_state = {
    'active_downloads': {},
    'bandwidth_used': 0,
    'lock': Lock()
}

def check_drive_availability(path):
    """Check if the encrypted drive is available"""
    try:
        return os.path.exists(path) and os.access(path, os.R_OK)
    except (OSError, IOError):
        return False

def get_show_info(relative_path):
    """Extract show name and season info from TV show path"""
    parts = relative_path.split(os.sep)
    if len(parts) >= 2:
        show_name = parts[0]
        season_folder = parts[1] if len(parts) > 1 else ""
        return show_name, season_folder
    return relative_path, ""

def get_all_files(base_paths):
    """Recursively get all files from the given paths"""
    files = []
    
    for base_path in base_paths:
        # Check if encrypted drive is mounted and accessible
        if not check_drive_availability(base_path):
            logging.warning(f"Drive not available or path does not exist: {base_path}")
            if "/Volumes/" in base_path:
                logging.warning(f"Encrypted drive may not be mounted: {base_path}")
            continue
        
        logging.info(f"Scanning directory: {base_path}")
        file_count = 0
        
        try:
            for root, dirs, filenames in os.walk(base_path):
                # Skip hidden directories and system files
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for filename in filenames:
                    # Skip hidden files and system files
                    if filename.startswith('.') or filename == 'Thumbs.db':
                        continue
                        
                    # Filter by allowed extensions
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext not in ALLOWED_EXTENSIONS:
                        continue
                        
                    full_path = os.path.join(root, filename)
                    try:
                        relative_path = os.path.relpath(full_path, base_path)
                        file_size = os.path.getsize(full_path)
                        
                        # Enhanced display for TV shows vs Movies
                        is_tv_show = (base_path == TV_SHOWS_PATH)
                        display_name = filename
                        show_info = ""
                        
                        if is_tv_show:
                            show_name, season_folder = get_show_info(relative_path)
                            if show_name and season_folder:
                                show_info = f"{show_name} - {season_folder}"
                                display_name = f"{show_name} - {season_folder} - {filename}"
                        
                        files.append({
                            'name': filename,
                            'display_name': display_name,
                            'path': full_path,
                            'relative_path': relative_path,
                            'size': file_size,
                            'size_mb': round(file_size / (1024 * 1024), 2),
                            'size_gb': round(file_size / (1024 * 1024 * 1024), 2),
                            'type': 'TV Show' if is_tv_show else 'Movie',
                            'extension': file_ext,
                            'show_info': show_info
                        })
                        file_count += 1
                        
                    except (OSError, IOError, PermissionError) as e:
                        logging.error(f"Error accessing file {full_path}: {e}")
                        continue
                        
        except (OSError, IOError, PermissionError) as e:
            logging.error(f"Error scanning directory {base_path}: {e}")
            continue
            
        logging.info(f"Found {file_count} video files in {base_path}")
    
    logging.info(f"Total: {len(files)} video files found")
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
    # Handle URL-encoded paths properly
    full_path = file_path
    if not full_path.startswith('/'):
        full_path = '/' + full_path
    
    # Check if file exists and is accessible
    if not os.path.exists(full_path):
        logging.error(f"File not found: {full_path}")
        return "File not found", 404
        
    # Check if drive is still mounted (for encrypted drives)
    if "/Volumes/" in full_path and not check_drive_availability(os.path.dirname(full_path)):
        logging.error(f"Drive not available for file: {full_path}")
        return "Drive not available - please check if encrypted drive is mounted", 503
    
    def generate():
        download_id = f"{int(time.time())}_{os.path.basename(full_path)}"
        
        # Check concurrent downloads
        with download_state['lock']:
            if len(download_state['active_downloads']) >= MAX_CONCURRENT_DOWNLOADS:
                return "Too many concurrent downloads", 429
            download_state['active_downloads'][download_id] = {
                'filename': os.path.basename(full_path),
                'start_time': datetime.now(),
                'size': os.path.getsize(full_path)
            }
        
        logging.info(f"Starting download: {os.path.basename(full_path)}")
        
        try:
            bytes_per_second = BANDWIDTH_LIMIT / len(download_state['active_downloads'])
            delay_per_chunk = CHUNK_SIZE / bytes_per_second
            
            with open(full_path, 'rb') as f:
                while True:
                    chunk = f.read(CHUNK_SIZE)
                    if not chunk:
                        break
                    
                    # Bandwidth limiting
                    time.sleep(delay_per_chunk)
                    yield chunk
        finally:
            # Clean up download state
            with download_state['lock']:
                if download_id in download_state['active_downloads']:
                    del download_state['active_downloads'][download_id]
            logging.info(f"Completed download: {os.path.basename(full_path)}")
    
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
    
    # Check if encrypted drives are mounted
    if MOVIES_PATH and not check_drive_availability(MOVIES_PATH):
        logging.error(f"Movies drive not available: {MOVIES_PATH}")
        print(f"⚠️  WARNING: Movies drive not mounted or accessible: {MOVIES_PATH}")
        
    if TV_SHOWS_PATH and not check_drive_availability(TV_SHOWS_PATH):
        logging.error(f"TV Shows drive not available: {TV_SHOWS_PATH}")
        print(f"⚠️  WARNING: TV Shows drive not mounted or accessible: {TV_SHOWS_PATH}")
    
    # Get paths from user if not in config
    if not MOVIES_PATH:
        MOVIES_PATH = input("Enter the path to your Movies folder: ").strip()
        # Update config
        config['movies_path'] = MOVIES_PATH
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    if not TV_SHOWS_PATH:
        TV_SHOWS_PATH = input("Enter the path to your TV Shows folder: ").strip()
        # Update config
        config['tv_shows_path'] = TV_SHOWS_PATH
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    print(f"Movies path: {MOVIES_PATH}")
    print(f"TV Shows path: {TV_SHOWS_PATH}")
    print(f"Bandwidth limit: {BANDWIDTH_LIMIT / (1024 * 1024)} Mbps")
    print()
    print(f"Starting server at http://0.0.0.0:{PORT}")
    
    app.run(host='0.0.0.0', port=PORT, debug=True)