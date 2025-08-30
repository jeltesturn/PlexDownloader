#!/bin/bash
echo "🔍 PlexDownloader Diagnostics"
echo "============================="
echo "Date: $(date)"
echo "Hostname: $(hostname)"
echo "IP: $(hostname -I | awk '{print $1}')"
echo ""

echo "📁 Directory Check:"
pwd
ls -la app.py config.json start_server.sh 2>/dev/null || echo "Missing files"
echo ""

echo "🐍 Python Check:"
which python3
python3 --version
echo ""

echo "💾 Drive Check:"
echo "Movies: $([ -d '/Volumes/plexlib/movies' ] && echo '✅ Mounted' || echo '❌ Not found')"
echo "Series: $([ -d '/Volumes/plexlib/series' ] && echo '✅ Mounted' || echo '❌ Not found')"
echo ""

echo "🔍 Process Check:"
ps aux | grep -E "(app.py|gunicorn|flask)" | grep -v grep || echo "No PlexDownloader processes running"
echo ""

echo "🔌 Port Check:"
lsof -i :8035 || echo "Nothing listening on port 8035"
netstat -an | grep 8035 || echo "Port 8035 not found in netstat"
echo ""

echo "📋 Log Files:"
for log in server.log plexdownloader.log deployment.log; do
    if [ -f "$log" ]; then
        echo "--- $log (last 5 lines) ---"
        tail -5 "$log"
        echo ""
    fi
done

echo "🧪 Quick App Test:"
if [ -f "venv/bin/activate" ] && [ -f "app.py" ]; then
    source venv/bin/activate
    python3 -c "
try:
    import app
    print('✅ App imports successfully')
    print('✅ Movies path check:', app.check_drive_availability('/Volumes/plexlib/movies'))
    print('✅ Series path check:', app.check_drive_availability('/Volumes/plexlib/series'))
except Exception as e:
    print('❌ Error:', e)
" 2>/dev/null
else
    echo "❌ venv or app.py not found"
fi

echo ""
echo "🌐 Network Test:"
curl -s -o /dev/null -w "Local connection: %{http_code}\n" http://localhost:8035 2>/dev/null || echo "Local connection: Failed"
echo ""
echo "Diagnostics complete!"