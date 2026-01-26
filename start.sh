#!/usr/bin/env sh

MODEL_URL="${MODEL_URL:-https://github.com/dizzy1900/adaptmetric-backend/releases/download/v1.0.0/ag.surrogate.pkl}"
MODEL_PATH="ag_surrogate.pkl"

echo "=== Model Download Setup ==="
echo "Model URL: $MODEL_URL"
echo "Model Path: $MODEL_PATH"
echo "File exists: $([ -f "$MODEL_PATH" ] && echo "YES ($(ls -lh "$MODEL_PATH" 2>/dev/null | awk '{print $5}'))" || echo "NO")"

# Force re-download if file exists but is corrupted or wrong
if [ -f "$MODEL_PATH" ]; then
  # Check if file is valid pickle (not HTML error page)
  if head -1 "$MODEL_PATH" | grep -q "HTTP\|<!DOCTYPE\|<html"; then
    echo "Found corrupted model file (looks like HTML). Removing..."
    rm -f "$MODEL_PATH"
  fi
fi

if [ ! -f "$MODEL_PATH" ]; then
  echo "Downloading model from $MODEL_URL..."
  curl -L --retry 3 --retry-delay 5 --max-time 300 --fail -o "$MODEL_PATH" "$MODEL_URL"

  if [ -f "$MODEL_PATH" ]; then
    SIZE=$(ls -lh "$MODEL_PATH" | awk '{print $5}')
    echo "Model downloaded successfully. Size: $SIZE"

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
  echo "Model file already exists, skipping download"
fi

echo "=== Starting Gunicorn ==="
exec gunicorn main:app --bind 0.0.0.0:${PORT:-8000} --workers 2 --threads 4 --timeout 120
