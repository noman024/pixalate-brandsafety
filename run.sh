#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "tmux is not installed. Please install it with: sudo apt-get install tmux"
    exit 1
fi

# Check if the virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup_env.sh first..."
    ./setup_env.sh
fi

# Kill any existing processes using the required ports
echo "Checking for existing processes..."
pkill -f "uvicorn app.api.main:app" || true
pkill -f "streamlit run app/main.py" || true

# Check if ports are in use
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8000 is still in use. Please close the application using this port."
    exit 1
fi

if lsof -Pi :8501 -sTCP:LISTEN -t >/dev/null ; then
    echo "Port 8501 is still in use. Please close the application using this port."
    exit 1
fi

echo "Ports are clear. Starting services..."

# Check if a tmux session named "brandsafety" already exists
if tmux has-session -t brandsafety 2>/dev/null; then
    echo "A tmux session named 'brandsafety' already exists."
    echo "Killing the existing session..."
    tmux kill-session -t brandsafety
fi

# Create a new tmux session named "brandsafety" in detached mode
tmux new-session -d -s brandsafety

# Split the window horizontally
tmux split-window -h -t brandsafety

# Configure the left pane (backend)
tmux send-keys -t brandsafety:0.0 "cd $(pwd) && source venv/bin/activate && echo 'Starting FastAPI server...' && python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000" C-m

# Wait a moment for the API to start
sleep 2

# Configure the right pane (frontend)
tmux send-keys -t brandsafety:0.1 "cd $(pwd) && source venv/bin/activate && echo 'Starting Streamlit UI...' && STREAMLIT_SERVER_RUN_ON_SAVE=false streamlit run app/main.py --server.port 8501 --server.headless=true" C-m

# Attach to the tmux session
tmux attach-session -t brandsafety

# When the tmux session is closed, make sure to clean up any remaining processes
echo "Cleaning up processes..."
pkill -f "uvicorn app.api.main:app" || true
pkill -f "streamlit run app/main.py" || true

echo "All services have been stopped."