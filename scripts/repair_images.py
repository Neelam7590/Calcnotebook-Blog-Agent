"""
repair_images.py  -  Purani tooti hui post images ko theek karta hai
--------------------------------------------------------------------
Do problems theek karta hai:
  1. Image repo mein push hi nahi hui  -> post mein 404 image
  2. Pixabay timeout ki wajah se image lagi hi nahi -> post mein image nahi

GitHub Actions se chalta hai (secrets wahin milte hain):
  Actions -> Repair Missing Images -> Run workflow

Local par test nahi kar sakte kyunki BLOG_ID aur Google token .env mein nahi hote.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import image_fetcher  # noqa: E402
from agent import blogger_service, env, load_json, log, save_json  # noqa: E402

# Jin posts ko theek karna hai.
# image_id  -> Pixabay se wahi purani image wapas laao (push fail hui thi)
# query     -> post mein image hi nahi thi, nayi image laao
REPAIRS = [
    {
        "date": "2026-11-04",
        "calculator": "BMI Calculator",
        "topic": "How to Use a BMI Calculator to Manage Healthy Weight Gain During Pregnancy for Indian Women",
        "url": "https://calcnotebook.blogspot.com/2026/11/using-bmi-calculator-pregnancy-india.html",
        "image_id": 8676690,
        "query": None,
    },
    {
        "date": "2026-11-05",
        "calculator": "Percentage Calculator",
        "topic": "How to calculate your salary raise percentage and estimate the new take-home pay in India",
        "url": "https://calcnotebook.blogspot.com/2026/11/salary-raise-percentage-calculator.html",
        "image_id": None,
        "query": "salary money calculator",
    },
]


def norm_url(url):
    return re.sub(r"^https?://", "", (url or "").rstrip("/")).lower()


def find_post(service, blog_id, url):
    """Blogger par URL se post dhoondta hai (saare pages check karta hai)."""
    token = None
    while True:
        params = {"blogId": blog_id, "maxResults": 100, "status": "live"}
        if token:
            params["pageToken"] = token
        res = service.posts().list(**params).execute()
        for item in res.get("items", []):
            if norm_url(item.get("url")) == norm_url(url):
                return item
        token = res.get("nextPageToken")
        if not token:
            return None


def add_state_entry(state, repair, post_title, image_id):
    """Agar state.json mein entry missing hai to add karo (Nov 4 wali)."""
    exists = any(
        p.get("date") == repair["date"] and p.get("calculator") == repair["calculator"]
        for p in state["posts"]
    )
    if not exists:
        state["posts"].append({
            "date": repair["date"],
            "calculator": repair["calculator"],
            "topic": repair["topic"],
            "title": post_title,
            "mode": "publish",
            "url": repair["url"],
        })
        log(f"state.json mein entry add hui: {repair['date']}")

    if image_id:
        used = state.setdefault("used_image_ids", [])
        if image_id not in used:
            used.append(image_id)


def main():
    state = load_json("state.json")
    used = state.get("used_image_ids", [])
    blog_id = env("BLOG_ID")
    service = blogger_service()
    failed = []

    for repair in REPAIRS:
        log(f"Repair start: {repair['url']}")
        item = find_post(service, blog_id, repair["url"])
        if not item:
            log(f"Post Blogger par nahi mili: {repair['url']}")
            failed.append(repair["url"])
            continue

        content = item.get("content", "")

        # Image laao: pehle exact id se, warna query se
        image = None
        if repair["image_id"]:
            image = image_fetcher.fetch_image_by_id(repair["image_id"])
        if not image and repair["query"]:
            image = image_fetcher.fetch_image(repair["query"], used)
        if not image:
            image = image_fetcher.fetch_image("calculator finance desk", used)

        if not image:
            log("Image nahi mili, ye post abhi bhi tooti hai.")
            failed.append(repair["url"])
            continue

        # Post mein image URL pehle se hai to sirf file save karni thi (Nov 4)
        if image["url"] in content:
            log("Image file save ho gayi, post content pehle se sahi hai.")
        else:
            # Image hi nahi thi (Nov 5) -> content ke upar image jodo
            body = image_fetcher.add_image(content, image, item.get("title", ""))
            service.posts().update(
                blogId=blog_id,
                postId=item["id"],
                body={
                    "id": item["id"],
                    "title": item.get("title", ""),
                    "content": body,
                    "labels": item.get("labels", []),
                },
            ).execute()
            log("Post update ho gayi, image add ho gayi.")

        add_state_entry(state, repair, item.get("title", ""), image["id"])

    save_json("state.json", state)

    if failed:
        log(f"{len(failed)} post theek nahi hui:")
        for url in failed:
            log(f" - {url}")
        sys.exit(1)
    log("Saari purani posts theek ho gayi.")


if __name__ == "__main__":
    main()
