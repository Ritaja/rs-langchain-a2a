#!/usr/bin/env bash
set -e

# Update package lists and install Python venv and pip
echo "Checking for python3..."
if ! command -v python3 &> /dev/null; then
  echo "Python3 not found. Installing python3, python3-venv, and python3-pip..."
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip
else
  echo "Python3 is installed."
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
  echo "Creating virtual environment in .venv..."
  python3 -m venv .venv
else
  echo "Virtual environment .venv already exists."
fi

# Activate virtual environment and upgrade pip
echo "Activating virtual environment..."
source .venv/bin/activate
echo "Upgrading pip..."
pip install --upgrade pip

# Install project dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt
