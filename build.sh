#!/bin/bash

# Create and activate a virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install the dependencies
pip install -r requirements.txt
pip install flask
# Start your Flask app
