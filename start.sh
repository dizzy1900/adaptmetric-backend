#!/usr/bin/env sh

MODEL_URL="${MODEL_URL:-https://github.com/dizzy1900/adaptmetric-backend/releases/download/v1.0.0/ag.surrogate.pkl}"
MODEL_PATH="ag_surrogate.pkl"
MIN_MODEL_SIZE=10000000  # 10MB minimum expected size

echo "=== Model Download Setup ==="
echo "Model URL: $MODEL_URL"
echo "Model Path: $MODEL_PATH"

# Download or validate model using Python
python3 << 'PYTHON_SCRIPT'
import os
import sys
import urllib.request

model_url = os.environ.get("MODEL_URL", "https://github.com/dizzy1900/adaptmetric-backend/releases/download/v1.0.0/ag.surrogate.pkl")
model_path = "ag_surrogate.pkl"
min_size = 10_000_000  # 10MB

print(f"Model URL: {model_url}")
print(f"Model Path: {model_path}")

# Check if file exists and validate
if os.path.exists(model_path):
    file_size = os.path.getsize(model_path)
    print(f"File exists: YES (size: {file_size} bytes)")

    # Read first bytes to check for HTML
    with open(model_path, 'rb') as f:
        first_bytes = f.read(15).decode('utf-8', errors='ignore')

    # Re-download if too small or looks like HTML
    if file_size < min_size or 'HTTP' in first_bytes or '<!DOCTYPE' in first_bytes or '<html' in first_bytes:
        print(f"Found corrupted file (size={file_size}, first_bytes={repr(first_bytes)}). Removing...")
        os.remove(model_path)
else:
    print("File exists: NO")

# Download if missing
if not os.path.exists(model_path):
    print(f"Downloading model from {model_url}...")
    try:
        urllib.request.urlretrieve(model_url, model_path)
        file_size = os.path.getsize(model_path)
        print(f"Model downloaded successfully. Size: {file_size} bytes")

        # Verify size
        if file_size < min_size:
            print(f"ERROR: Downloaded file too small ({file_size} bytes), expected > 10MB")
            sys.exit(1)

        # Verify content
        with open(model_path, 'rb') as f:
            first_bytes = f.read(15).decode('utf-8', errors='ignore')
        if 'HTTP' in first_bytes or '<!DOCTYPE' in first_bytes or '<html' in first_bytes:
            print(f"ERROR: Downloaded file looks like HTML, not pickle data")
            sys.exit(1)
    except Exception as e:
        print(f"ERROR: Download failed: {e}")
        sys.exit(1)
else:
    print("Model file already exists with valid size, skipping download")

print("=== Model download complete ===")
PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "ERROR: Model download/preparation failed"
    exit 1
fi

echo "=== Starting Gunicorn ==="
exec gunicorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120
