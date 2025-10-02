#!/bin/bash
# Setup and run script for Manus scheduled task
# This script is executed by the Manus scheduler

set -e  # Exit on error

echo "=================================================="
echo "Manus Content Pipeline Automation - Setup"
echo "=================================================="

# Install Python dependencies
echo "📦 Installing dependencies..."
pip3 install -q -r requirements.txt

# Check if credentials exist
if [ ! -f "credentials.json" ]; then
    echo "❌ ERROR: credentials.json not found"
    echo "Please add credentials.json to the repository"
    exit 1
fi

# Check if token exists
if [ ! -f "token.json" ]; then
    echo "❌ ERROR: token.json not found"
    echo "Please run authentication first and add token.json to repository"
    exit 1
fi

echo "✅ Setup complete"
echo ""

# Run the automation
echo "=================================================="
echo "Starting Automation"
echo "=================================================="
python3 run_automation.py
