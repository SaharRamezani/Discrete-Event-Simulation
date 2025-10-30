#!/bin/bash

# Set the virtual environment directory name
VENV_DIR="venv"

# Check if the virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Virtual environment not found. Creating one..."

  # Create a virtual environment
  python3 -m venv $VENV_DIR

  if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment. Ensure Python 3 is installed."
    exit 1
  fi
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source $VENV_DIR/bin/activate

if [ $? -ne 0 ]; then
  echo "Failed to activate virtual environment. Please check the setup."
  exit 1
fi

# Install project dependencies (if requirements.txt exists)
if [ -f "requirements.txt" ]; then
  echo "Installing existing dependencies from requirements.txt..."
  pip install -r requirements.txt

  if [ $? -ne 0 ]; then
    echo "Failed to install dependencies."
    exit 1
  fi
fi

# Generate the requirements.txt file
echo "Generating requirements.txt..."
pip freeze > requirements.txt

if [ $? -eq 0 ]; then
  echo "requirements.txt generated successfully."
else
  echo "Failed to generate requirements.txt."
  exit 1
fi

# Deactivate the virtual environment
echo "Deactivating virtual environment..."
deactivate

echo "Done."
