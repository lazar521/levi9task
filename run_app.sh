#!/bin/bash

echo "Creating virtual environment..."
python -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment."
    exit 1
fi

echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi

echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
fi

echo "Building the app..."
python -m compileall main.py
if [ $? -ne 0 ]; then
    echo "Failed to build the app."
    exit 1
fi

echo "Starting the app..."
python main.py
if [ $? -ne 0 ]; then
    echo "Failed to start the app."
    exit 1
fi
