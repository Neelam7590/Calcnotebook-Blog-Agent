#!/usr/bin/env python3
"""
Debug script to check Blogger post images.
"""
import os
import re
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

def env(name, required=True):
    value = os.getenv(name, "").strip()
    if required and not value:
        raise SystemExit(f"ERROR: {name} missing")
    return value

def blogger_service():
    creds = Credentials(
        token=None,
        refresh_token=env("GOOGLE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=env("GOOGLE_CLIENT_ID"),
        client_secret=env("GOOGLE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/blogger"],
    )
    return build("blogger", "v3", credentials=creds, cache_discovery=False)

def main():
    service = blogger_service()
    blog_id = env("BLOG_ID")
    
    # Get latest 2 published posts
    posts = service.posts().list(blogId=blog_id, status="LIVE", maxResults=2).execute()
    items = posts.get("items", [])
    
    if not items:
        print("No published posts found")
        return
    
    print(f"Found {len(items)} published posts\n")
    
    local_images = set(f.lower() for f in os.listdir(ROOT / "images"))
    repo_name = "Neelam7590/Calcnotebook-Blog-Agent"
    
    for i, post in enumerate(items, 1):
        title = post.get("title", "Untitled")
        content = post.get("content", "")
        url = post.get("url", "")
        
        print(f"{'='*60}")
        print(f"POST {i}: {title}")
        print(f"URL: {url}")
        print(f"{'='*60}")
        
        # Find first <img> tag
        img_match = re.search(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', content, re.IGNORECASE)
        if not img_match:
            print("No <img> tag found in content")
            continue
            
        img_tag = img_match.group(0)
        img_url = img_match.group(1)
        
        print(f"\nFirst <img> tag:")
        print(f"  {img_tag}")
        print(f"\nImage URL: {img_url}")
        
        # Check HTTP status
        print(f"\nHTTP HEAD request to image URL:")
        try:
            resp = requests.head(img_url, timeout=10, allow_redirects=True)
            print(f"  Status: {resp.status_code}")
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Also try GET to see if HEAD fails
        print(f"\nHTTP GET request to image URL (first 1KB):")
        try:
            resp = requests.get(img_url, timeout=10, allow_redirects=True, stream=True)
            print(f"  Status: {resp.status_code}")
            print(f"  Content-Type: {resp.headers.get('Content-Type', 'N/A')}")
            print(f"  Content-Length: {resp.headers.get('Content-Length', 'N/A')}")
            # Read a bit to confirm it's an image
            chunk = next(resp.iter_content(1024), b'')
            print(f"  First bytes: {chunk[:20]}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # Compare with local images
        print(f"\nComparison:")
        # Extract filename from URL
        filename_match = re.search(r'/([^/]+\.jpg)$', img_url, re.IGNORECASE)
        if filename_match:
            url_filename = filename_match.group(1)
            print(f"  Filename from URL: {url_filename}")
            print(f"  Exists locally (case-insensitive): {url_filename.lower() in local_images}")
            # Check exact case match
            exact_match = url_filename in os.listdir(ROOT / "images")
            print(f"  Exact case match: {exact_match}")
            if not exact_match and url_filename.lower() in local_images:
                actual = next(f for f in os.listdir(ROOT / "images") if f.lower() == url_filename.lower())
                print(f"  Actual local filename: {actual}")
        else:
            print(f"  Could not extract filename from URL")
        
        # Check repo name in URL
        print(f"  Repo in URL: {repo_name}")
        if repo_name.lower() in img_url.lower():
            print(f"  Repo name matches (case-insensitive): True")
        else:
            print(f"  Repo name matches (case-insensitive): False")
            # Find what repo name is in the URL
            repo_match = re.search(r'cdn\.jsdelivr\.net/gh/([^/]+)/', img_url)
            if repo_match:
                print(f"  Actual repo in URL: {repo_match.group(1)}")
        
        print()

if __name__ == "__main__":
    main()