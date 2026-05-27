#!/bin/bash

# Start all services for Wand application
SCRIPT_DIR="/Users/nishant/Desktop/wand"
echo "Starting Wand services..."

# 1. Start Backend API in background
echo "Starting Backend API on port 8000..."
cd "$SCRIPT_DIR"
uvicorn api.main:app --reload &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait a moment for backend to start
sleep 3

# 2. Start Frontend in background
echo "Starting Frontend on port 3000..."
cd "$SCRIPT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Save PIDs to a file for stop script
echo "$BACKEND_PID" > "$SCRIPT_DIR/.pids"
echo "$FRONTEND_PID" >> "$SCRIPT_DIR/.pids"

echo ""
echo "All services started!"
echo "Backend API: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "To stop all services, run: ./stop_services.sh"
echo "Or use Ctrl+C to stop this script and all services"

# Keep script running and wait for Ctrl+C
trap 'echo "Stopping all services..."; "$SCRIPT_DIR/stop_services.sh"; exit' INT

# Wait indefinitely
while true; do
    sleep 1
done
