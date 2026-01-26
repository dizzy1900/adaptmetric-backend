from pathlib import Path
import urllib.request
import os

MODEL_DIR = Path("models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

url = os.environ.get("MODEL_URL")  # set this in Railway Variables
path = MODEL_DIR / "ag_surrogate.pkl"

if not path.exists():
    if not url:
        raise RuntimeError("MODEL_URL env var not set")
    print(f"Downloading model from {url} -> {path}")
    urllib.request.urlretrieve(url, path)

print("Model present:", path, "size:", path.stat().st_size)
