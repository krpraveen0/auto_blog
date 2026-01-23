#!/usr/bin/env bash
# Start API server for admin panel LinkedIn posting
# Usage: ./start_api_server.sh [port]

PORT=${1:-5000}

echo "Starting API Server for Admin Panel..."
echo "Port: $PORT"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   LinkedIn posting will not work without credentials"
    echo "   Copy .env.example to .env and configure your credentials"
    echo ""
fi

# Check for LinkedIn credentials
if [ -z "$LINKEDIN_ACCESS_TOKEN" ] || [ -z "$LINKEDIN_USER_ID" ]; then
    echo "⚠️  LinkedIn credentials not set in environment"
    echo "   Make sure LINKEDIN_ACCESS_TOKEN and LINKEDIN_USER_ID are set in .env"
    echo ""
fi

# Set environment variables
export API_PORT=$PORT
export API_DEBUG=false

# Start the server
echo "Starting server on http://localhost:$PORT"
echo "Press Ctrl+C to stop"
echo ""

python api_server.py
