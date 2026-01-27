#!/usr/bin/env sh

MODEL_URL="${MODEL_URL:-https://github.com/dizzy1900/adaptmetric-backend/releases/download/v1.0.0/ag.surrogate.pkl}"
MODEL_PATH="ag_surrogate.pkl"
MIN_MODEL_SIZE=10000000  # 10MB minimum expected size

echo "=== Model Download Setup ==="
echo "Model URL: $MODEL_URL"
echo "Model Path: $MODEL_PATH"

# Force re-download if file doesn't look valid
if [ -f "$MODEL_PATH" ]; then
  FILE_SIZE=$(wc -c < "$MODEL_PATH" 2>/dev/null || echo "0")
  echo "File exists: YES (size: $FILE_SIZE bytes)"

  # Check if file is suspiciously small (< 10MB) or looks like HTML
  if [ "$FILE_SIZE" -lt "$MIN_MODEL_SIZE" ] || head -1 "$MODEL_PATH" | grep -q "HTTP\|<!DOCTYPE\|<html"; then
    echo "Found corrupted or invalid model file (size too small or looks like HTML). Removing..."
    rm -f "$MODEL_PATH"
  fi
else
  echo "File exists: NO"
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "Downloading model from $MODEL_URL..."
  curl -L --retry 3 --retry-delay 5 --max-time 600 --fail -o "$MODEL_PATH" "$MODEL_URL"

  if [ -f "$MODEL_PATH" ]; then
    FILE_SIZE=$(wc -c < "$MODEL_PATH")
    echo "Model downloaded successfully. Size: $FILE_SIZE bytes"

    # Verify file size is reasonable
    if [ "$FILE_SIZE" -lt "$MIN_MODEL_SIZE" ]; then
      echo "ERROR: Downloaded file is too small ($FILE_SIZE bytes), expected > 10MB"
      echo "First bytes: $(head -c 50 "$MODEL_PATH")"
      exit 1
    fi

    # Verify file isn't an error page
    if head -1 "$MODEL_PATH" | grep -q "HTTP\|<!DOCTYPE\|<html"; then
      echo "ERROR: Downloaded file appears to be HTML, not a valid model file!"
      exit 1
    fi
  else
    echo "ERROR: Model download failed - file not found"
    exit 1
  fi
else
  echo "Model file already exists with valid size, skipping download"
fi

echo "=== Starting Gunicorn ==="
exec gunicorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120
