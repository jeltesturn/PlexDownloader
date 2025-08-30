# PlexDownloader

A web-based file download server for your Plex media collection. Allows you to browse and download movies and TV shows from your Mac mini with bandwidth limiting and a clean web interface.

## Features

- **Web Interface**: Clean, responsive web interface accessible from any device
- **File Discovery**: Recursively scans your Movies and TV Shows directories  
- **Search & Filter**: Search files by name/path, filter by type (Movies/TV Shows) and size
- **Batch Downloads**: Select multiple files and download them sequentially
- **Bandwidth Limiting**: Configurable bandwidth limiting (default 10 Mbps)
- **Concurrent Downloads**: Support for multiple concurrent downloads with limits
- **Progress Tracking**: Real-time download progress and status
- **File Type Filtering**: Only shows video files (mp4, mkv, avi, mov, etc.)
- **Logging**: Comprehensive logging of all activities

## Configuration

Edit `config.json` to customize:

```json
{
  "movies_path": "/path/to/your/movies",
  "tv_shows_path": "/path/to/your/tv_shows", 
  "port": 8035,
  "bandwidth_limit_mbps": 10,
  "allowed_extensions": [".mp4", ".mkv", ".avi", ".mov", ".m4v", ".wmv", ".flv", ".webm"],
  "max_concurrent_downloads": 3,
  "chunk_size": 8192
}
```

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jeltesturn/PlexDownloader.git
   cd PlexDownloader
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure paths**:
   Edit `config.json` with your actual movie and TV show paths

5. **Run the server**:
   ```bash
   python app.py
   ```

   Or for production with gunicorn:
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8035 app:app
   ```

6. **Access the interface**:
   Open your browser to `http://your-mac-mini-ip:8035`

## Usage

1. **Browse Files**: The interface shows all video files from your configured directories
2. **Search**: Use the search box to find specific files by name or path
3. **Filter**: Filter by content type (Movies/TV Shows) or file size ranges
4. **Select**: Check the boxes next to files you want to download
5. **Download**: Click "Download Selected Files" to start batch download
6. **Progress**: Monitor download progress with the built-in progress bar

## Network Configuration

The server binds to `0.0.0.0:8035` by default, making it accessible from other devices on your network. Make sure your firewall allows connections on port 8035.

For internet access, you'll need to configure port forwarding on your router to forward external port 8035 to your Mac mini's IP address.

## GitHub Actions Runner Setup

This project is designed to be deployed via GitHub Actions to your Mac mini. Set up a self-hosted runner on your Mac mini to automatically deploy updates.

## Security Notes

- This server does not include authentication - anyone with network access can download files
- Consider running behind a VPN or adding authentication for internet exposure
- The server logs all download activities to `plexdownloader.log`

## Logs

Check `plexdownloader.log` for:
- File discovery activities
- Download start/completion events  
- Error messages and warnings
- Server startup information