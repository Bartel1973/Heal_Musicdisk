#!/bin/bash

# Oldskool Music Disk Launcher Script
# This script makes the heal.py file executable and runs it

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_FILE="$SCRIPT_DIR/healv2.py"

# Check if Python file exists
if [ ! -f "$PYTHON_FILE" ]; then
    echo "Error: heal.py not found in $SCRIPT_DIR"
    exit 1
fi

# Make the Python file executable
chmod +x "$PYTHON_FILE"

# Check if required Python packages are installed
echo "Checking Python dependencies..."

# Check for pygame
python3 -c "import pygame" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: pygame is not installed. Installing..."
    pip3 install pygame
fi

# Check for numpy
python3 -c "import numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Warning: numpy is not installed. Installing..."
    pip3 install numpy
fi

# Change to the script directory
cd "$SCRIPT_DIR"

# Run the Python script
echo "Starting Oldskool Music Disk..."
python3 "$PYTHON_FILE"

# Keep the terminal open if there's an error
if [ $? -ne 0 ]; then
    echo "Press Enter to exit..."
    read
fi
