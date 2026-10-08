"""
image_fetcher.py  -  Pixabay se blog ki image laane ka alag module
------------------------------------------------------------------
Kaam:
  1. Keyword se Pixabay par photo dhoondta hai
  2. Photo ko images/ folder mein download karta hai
  3. Blog ke liye <img> wala HTML banata hai (credit ke saath)

Zaruri .env keys:
  PIXABAY_API_KEY   (pixabay.com/api/docs se)
  IMAGE_REPO        (jaise Neelam7590/calcnotebook-blog-agent, repo PUBLIC ho)

Akele test karne ke liye:
  python scripts/image_fetcher.py "calculator money desk"
"""
import html
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

IMAGES_DIR = ROOT / "images"


def _log(msg):
    print(f"[image] {msg}", flush=True)


def fetch_image(query, used_ids=None):
    """
    Return: dict {id, url, photographer, page}  ya  None (agar image nahi mili)
    used_ids: pehle use hui image ids ki list (repeat se bachne ke liye)
    """
    used_ids = used_ids or []
    key = os.getenv("PIXABAY_API_KEY", "").strip()
    if not key:
        _log("PIXABAY_API_KEY nahi hai, image skip.")
        return None

    try:
        r = requests.get(
            "https://pixabay.com/api/",
            params={
                "key": key,
                "q": query,
                "image_type": "photo",
                "orientation": "horizontal",
                "safe_search": "true",
                "per_page": 20,
            },
            timeout=30,
        )
        r.raise_for_status()
        hits = r.json().get("hits", [])
        if not hits:
            _log(f"'{query}' ke liye koi image nahi mili.")
            return None

        for hit in hits:
            if hit["id"] in used_ids:
                continue

            # Pixabay hotlinking allow nahi karta, isliye download karte hain
            img = requests.get(hit["largeImageURL"], timeout=60)
            img.raise_for_status()
            IMAGES_DIR.mkdir(exist_ok=True)
            filename = f"{hit['id']}.jpg"
            (IMAGES_DIR / filename).write_bytes(img.content)

            repo = os.getenv("IMAGE_REPO", "").strip() or os.getenv("GITHUB_REPOSITORY", "")
            if repo:
                public_url = f"https://cdn.jsdelivr.net/gh/{repo}@main/images/{filename}"
            else:
                _log("IMAGE_REPO set nahi hai, Pixabay ka seedha link use ho raha hai "
                     "(ye kuch ghante mein toot sakta hai).")
                public_url = hit["largeImageURL"]

            _log(f"Image mili: {filename}")
            return {
                "id": hit["id"],
                "url": public_url,
                "photographer": hit.get("user", "Pixabay"),
                "page": hit["pageURL"],
            }

        _log("Saari images pehle use ho chuki hain.")
    except Exception as e:  # noqa: BLE001
        _log(f"Pixabay fail ({e}), bina image ke aage badh rahe hain.")
    return None


def add_image(body, image, title):
    """Blog body ke upar image + credit jodta hai. Image None ho to body waisi hi lautati hai."""
    if not image:
        return body
    figure = (
        '<div style="text-align:center;margin-bottom:18px;">'
        f'<img src="{image["url"]}" alt="{html.escape(title)}" '
        'style="max-width:100%;height:auto;border-radius:8px;" />'
        f'<br/><small>Image by <a href="{image["page"]}" rel="nofollow">'
        f'{html.escape(image["photographer"])}</a> from Pixabay</small></div>'
    )
    return figure + body


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "calculator money desk"
    result = fetch_image(q)
    print(result)