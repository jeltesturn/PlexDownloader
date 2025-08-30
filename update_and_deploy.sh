#!/bin/bash
# Quick update and deployment script for PlexDownloader

echo "🔄 PlexDownloader Update & Deploy"
echo "================================="

# Stop existing server
echo "🛑 Stopping existing server..."
pkill -f "app.py" || true
pkill -f "gunicorn.*app:app" || true
sleep 2

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin master

# Make scripts executable
chmod +x start_server.sh diagnose.sh

# Check drives
echo "💾 Checking drives..."
if [ -d "/Volumes/plexlib/movies" ] && [ -d "/Volumes/plexlib/series" ]; then
    echo "✅ Both drives available"
else
    echo "⚠️  Warning: Some drives may not be mounted"
fi

# Start server
echo "🚀 Starting server..."
./start_server.sh &
SERVER_PID=$!
echo $SERVER_PID > server.pid

# Wait and test
echo "⏳ Waiting for server to start..."
sleep 10

# Test connection
if curl -s http://localhost:8035/ > /dev/null; then
    echo "✅ Deployment successful!"
    echo "🌐 Access at: http://192.168.178.38:8035"
    echo "📊 Server PID: $SERVER_PID"
else
    echo "❌ Deployment failed - server not responding"
    echo "📋 Check logs: tail -f plexdownloader.log"
fi

echo "🎬 Update complete!"