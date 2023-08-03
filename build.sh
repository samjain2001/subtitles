#!/bin/bash

# Build script for your project

# Step 1: Build frontend assets
echo "Building frontend assets..."
npm install
npm run build

# Step 2: Create and activate virtual environment
echo "Creating and activating virtual environment..."
python3.9 -m venv venv
source venv/bin/activate

# Step 3: Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Step 4: Deactivate virtual environment
deactivate

echo "Build completed successfully!"
