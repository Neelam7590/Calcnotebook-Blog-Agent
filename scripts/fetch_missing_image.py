#!/usr/bin/env python3
"""
Fetch missing Pixabay image by ID and save to images/
"""
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

IMAGES_DIR = ROOT / "images"
PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "").strip()

if not PIXABAY_API_KEY:
    print("ERROR: PIXABAY_API_KEY not found in .env")
    sys.exit(1)

image_id = "178127"
url = f"https://pixabay.com/api/?key={PIXABAY_API_KEY}&id={image_id}"

print(f"Fetching Pixabay image ID: {image_id}")
resp = requests.get(url, timeout=30)
resp.raise_for_status()
data = resp.json()

hits = data.get("hits", [])
if not hits:
    print(f"ERROR: Image ID {image_id} not found on Pixabay")
    sys.exit(1)

hit = hits[0]
large_url = hit["largeImageURL"]
print(f"Downloading from: {large_url}")

img_resp = requests.get(large_url, timeout=60)
img_resp.raise_for_status()

IMAGES_DIR.mkdir(exist_ok=True)
filename = f"{hit['id']}.jpg"
(IMAGES_DIR / filename).write_bytes(img_resp.content)
print(f"Saved to: images/{filename}")
print(f"Size: {len(img_resp.content)} bytes")