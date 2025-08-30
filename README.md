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

The `config.json` is pre-configured for Mac mini deployment:

```json
{
  "movies_path": "/Volumes/plexlib/movies",
  "tv_shows_path": "/Volumes/plexlib/series",
  "port": 8035,
  "bandwidth_limit_mbps": 10,
  "allowed_extensions": [".mp4", ".mkv", ".avi", ".mov", ".m4v", ".wmv", ".flv", ".webm"],
  "max_concurrent_downloads": 3,
  "chunk_size": 8192,
  "project_path": "/Users/jelteadmin/PlexDownloader"
}
```

### Path Structure
- **Movies**: Direct files like `MovieName.mp4`
- **TV Shows**: Nested structure like `TvShowName/Season01/Episode1.mp4`

## Mac Mini Setup

### Prerequisites
- Ensure encrypted drive is mounted at `/Volumes/plexlib/`
- Movies should be at `/Volumes/plexlib/movies`
- TV Shows should be at `/Volumes/plexlib/series`

### Quick Start
1. **On Mac mini** (at `/Users/jelteadmin/PlexDownloader`):
   ```bash
   ./start_server.sh
   ```

### Manual Setup
1. **Clone the repository**:
   ```bash
   cd /Users/jelteadmin
   git clone https://github.com/jeltesturn/PlexDownloader.git
   cd PlexDownloader
   ```

2. **Run the startup script**:
   ```bash
   chmod +x start_server.sh
   ./start_server.sh
   ```

3. **Access the interface**:
   - Local: `http://localhost:8035`
   - Network: `http://mac-mini-ip:8035`

### GitHub Actions Deployment
The repository includes a GitHub Actions workflow that automatically:
- Deploys to the Mac mini when you push changes
- Checks encrypted drive availability
- Restarts the server with new code
- Provides deployment status

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

## Encrypted Drive Notes

- The app automatically detects if `/Volumes/plexlib/` is mounted
- Warns if encrypted drives are not available
- Gracefully handles drive unmounting during operation
- Logs all drive access issues

## Security Notes

- This server does not include authentication - anyone with network access can download files
- Consider running behind a VPN or adding authentication for internet exposure
- The server logs all download activities to `plexdownloader.log`
- Encrypted drive access is logged for troubleshooting

## Logs

Check `plexdownloader.log` for:
- File discovery activities
- Download start/completion events  
- Error messages and warnings
- Server startup information