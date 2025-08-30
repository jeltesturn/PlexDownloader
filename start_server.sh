#!/bin/bash
# PlexDownloader startup script for Mac mini

echo "🎬 PlexDownloader Startup Script"
echo "================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the PlexDownloader directory."
    echo "Expected path: /Users/jelteadmin/PlexDownloader"
    exit 1
fi

echo "📁 Current directory: $(pwd)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if encrypted drives are mounted
echo "💾 Checking encrypted drives..."
if [ -d "/Volumes/plexlib/movies" ]; then
    echo "✅ Movies drive mounted: /Volumes/plexlib/movies"
else
    echo "⚠️  Warning: Movies drive not found at /Volumes/plexlib/movies"
    echo "   Please ensure the encrypted drive is mounted"
fi

if [ -d "/Volumes/plexlib/series" ]; then
    echo "✅ TV Shows drive mounted: /Volumes/plexlib/series"
else
    echo "⚠️  Warning: TV Shows drive not found at /Volumes/plexlib/series"
    echo "   Please ensure the encrypted drive is mounted"
fi

echo ""
echo "🚀 Starting PlexDownloader server..."
echo "📱 Access the web interface at: http://$(hostname -I | awk '{print $1}'):8035"
echo "🌐 Or locally at: http://localhost:8035"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server
if command -v gunicorn >/dev/null 2>&1; then
    echo "🏗️  Starting with Gunicorn (production mode)..."
    gunicorn -w 4 -b 0.0.0.0:8035 app:app --timeout 300
else
    echo "🧪 Starting with Flask development server..."
    python app.py
fi