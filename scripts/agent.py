"""
CalcNotebook Blogger Agent
--------------------------
Roz ek calculator ka blog likhta hai (weekday ke hisaab se), Pixabay se image lagata hai,
CalcNotebook ka backlink daalta hai aur Blogger par post karta hai.

Modes:
  --mode dry-run   sirf likhta hai, output/preview.html mein save karta hai (post nahi)
  --mode draft     Blogger par DRAFT bana deta hai
  --mode publish   Blogger par LIVE post karta hai

Examples:
  python scripts/agent.py                       (dry-run, aaj ka calculator)
  python scripts/agent.py --day friday          (kisi aur din ka calculator test karo)
  python scripts/agent.py --mode draft
  python scripts/agent.py --mode publish
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

import requests
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

sys.path.insert(0, str(ROOT / "scripts"))
from image_fetcher import fetch_image as fetch_pixabay_image, add_image as add_pixabay_image

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]


# ----------------------------------------------------------------- helpers
def load_json(name):
    with open(ROOT / name, encoding="utf-8") as f:
        return json.load(f)


def save_json(name, data):
    with open(ROOT / name, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def env(name, required=True):
    value = os.getenv(name, "").strip()
    if required and not value:
        raise SystemExit(f"ERROR: {name} missing hai. .env ya GitHub Secrets check karo.")
    return value


def log(msg):
    try:
        print(f"[agent] {msg}", flush=True)
    except UnicodeEncodeError:
        print(f"[agent] {msg.encode('ascii', 'replace').decode()}", flush=True)


def norm(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


# ----------------------------------------------------------------- Groq
def groq_chat(cfg, messages, json_mode=False, temperature=0.7, retries=3):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {env('GROQ_API_KEY')}"}
    body = {
        "model": cfg["groq_model"],
        "messages": messages,
        "temperature": temperature,
    }
    if json_mode:
        body["response_format"] = {"type": "json_object"}

    last_err = None
    for attempt in range(1, retries + 1):
        try:
            r = requests.post(url, headers=headers, json=body, timeout=90)
            if r.status_code == 429 or r.status_code >= 500:
                raise RuntimeError(f"Groq {r.status_code}: {r.text[:200]}")
            r.raise_for_status()
            msg = r.json()["choices"][0]["message"]
            content = msg.get("content") or msg.get("reasoning") or ""
            if not content:
                raise RuntimeError("Groq returned empty content")
            return content
        except Exception as e:  # noqa: BLE001
            last_err = e
            log(f"Groq attempt {attempt} fail: {e}")
            time.sleep(5 * attempt)
    raise SystemExit(f"Groq se response nahi mila: {last_err}")


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
    # Find all complete JSON objects, return the last one with required keys
    required = {"title", "image_query", "labels", "html"}
    brace_count = 0
    start = None
    candidates = []
    for i, ch in enumerate(text):
        if ch == '{':
            if brace_count == 0:
                start = i
            brace_count += 1
        elif ch == '}':
            if brace_count > 0:
                brace_count -= 1
                if brace_count == 0 and start is not None:
                    candidate = text[start:i+1]
                    try:
                        parsed = json.loads(candidate)
                        if required.issubset(parsed.keys()):
                            candidates.append(parsed)
                    except json.JSONDecodeError:
                        pass
                    start = None
    if candidates:
        return candidates[-1]
    return json.loads(text)


# ----------------------------------------------------------------- SerpApi (optional)
def serp_context(query):
    key = env("SERPAPI_KEY", required=False)
    if not key:
        return ""
    try:
        r = requests.get(
            "https://serpapi.com/search.json",
            params={"engine": "google", "q": query, "api_key": key, "hl": "en", "gl": "in"},
            timeout=45,
        )
        r.raise_for_status()
        data = r.json()
        lines = []
        for item in data.get("organic_results", [])[:6]:
            lines.append(f"- {item.get('title', '')}")
        for q in data.get("related_questions", [])[:6]:
            lines.append(f"- Question people ask: {q.get('question', '')}")
        return "\n".join(lines)
    except Exception as e:  # noqa: BLE001
        log(f"SerpApi skip ({e})")
        return ""


# ----------------------------------------------------------------- topic + writing
def pick_topic(cfg, state, calc):
    past = [p["topic"] for p in state["posts"] if p["calculator"] == calc["name"]][-40:]
    context = serp_context(f"{calc['name']} India how to use formula example")

    prompt = f"""You plan blog posts for an Indian calculator website.
Calculator: {calc['name']}
Language of blog: {cfg['language']}

Search results for inspiration (may be empty):
{context or '(none)'}

Topics ALREADY written (do NOT repeat or closely copy any):
{json.dumps(past, ensure_ascii=False)}

Suggest ONE fresh, specific, useful blog topic that people actually search for
and that naturally leads readers to use the {calc['name']}.
Return ONLY JSON: {{"topic": "...", "keyword": "main SEO keyword"}}"""

    for _ in range(3):
        data = parse_json(groq_chat(cfg, [{"role": "user", "content": prompt}],
                                    temperature=0.9))
        if norm(data["topic"]) not in {norm(p) for p in past}:
            return data
    return data


def write_post(cfg, calc, topic):
    link = cfg["site_url"] + calc["url"]
    system = (
        "You are an experienced Indian content writer who writes accurate, original, "
        "helpful blog posts about calculators, finance and everyday maths. "
        "Never invent laws, tax rates or statistics you are not sure about; "
        "if rates vary by state or date, say so and tell readers to verify."
    )
    user = f"""Write a blog post and output ONLY a single JSON object.

Topic: {topic['topic']}
Main keyword: {topic['keyword']}
Language: {cfg['language']}
Length: {cfg['min_words']}-{cfg['max_words']} words.

JSON keys: "title", "image_query", "labels", "html".

Rules:
- "title": catchy, includes the main keyword, max 65 characters.
- "image_query": 2-4 English words for a relevant stock photo (e.g. "calculator money desk"). No people's names.
- "labels": array of 2-4 short labels.
- "html": the FULL blog post body as a JSON string. Use ONLY these HTML tags: h2, h3, p, ul, ol, li, table, tr, th, td, strong, em, a.
  No h1, no <html>/<body>, no inline CSS, no markdown.
  Escape ALL double quotes in HTML as \\". Example: <a href=\\"https://example.com\\">Link</a>
- Structure: short intro, clear sections, one fully worked numeric example (double-check the maths),
  a short step-by-step "how to use the calculator" section, common mistakes, 4 FAQs, short conclusion.
- In the "html" content, include this link 2 times with different anchor text:
  <a href="{link}">{calc['name']}</a>
- If the topic is about money/finance/tax, add a one-line note in the html that this is general information, not professional advice.
- Write in a natural human tone, no filler, no repeated sentences.
- Output ONLY the JSON object. No extra text before or after."""

    data = parse_json(groq_chat(cfg, [{"role": "system", "content": system},
                                      {"role": "user", "content": user}],
                                json_mode=True, temperature=0.7))
    for key in ("title", "image_query", "labels", "html"):
        if key not in data:
            raise SystemExit(f"Groq output mein '{key}' nahi mila.")
    if not data.get("html", "").strip():
        raise SystemExit("Groq returned empty html field")
    return data


def ensure_backlink(cfg, calc, body):
    link = cfg["site_url"] + calc["url"]
    if link in body:
        return body
    cta = (f'<p><strong>Try it now:</strong> use our free '
           f'<a href="{link}">{html.escape(calc["name"])}</a> on {cfg["site_name"]}.</p>')
    return body + cta


# ----------------------------------------------------------------- Blogger
def blogger_service():
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build

    creds = Credentials(
        token=None,
        refresh_token=env("GOOGLE_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=env("GOOGLE_CLIENT_ID"),
        client_secret=env("GOOGLE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/blogger"],
    )
    return build("blogger", "v3", credentials=creds, cache_discovery=False)


def post_to_blogger(title, content, labels, as_draft):
    service = blogger_service()
    body = {"kind": "blogger#post", "title": title, "content": content, "labels": labels}
    result = service.posts().insert(blogId=env("BLOG_ID"), body=body, isDraft=as_draft).execute()
    return result.get("url") or result.get("id")


# ----------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dry-run", "draft", "publish"], default="dry-run")
    ap.add_argument("--day", choices=DAYS, help="Kisi aur din ka calculator test karne ke liye")
    ap.add_argument("--force", action="store_true", help="Aaj pehle se post hui ho tab bhi chalao")
    args = ap.parse_args()

    cfg = load_json("config.json")
    state = load_json("state.json")

    now = dt.datetime.now(IST)
    day = args.day or DAYS[now.weekday()]
    today = now.strftime("%Y-%m-%d")
    calc = cfg["calculators"][day]
    log(f"Din: {day} | Calculator: {calc['name']} | Mode: {args.mode}")

    if args.mode != "dry-run" and not args.force:
        if any(p["date"] == today and p["mode"] != "dry-run" for p in state["posts"]):
            log("Aaj ki post pehle ho chuki hai. --force se dobara chala sakti ho. Exit.")
            return

    topic = pick_topic(cfg, state, calc)
    log(f"Topic: {topic['topic']}")

    post = write_post(cfg, calc, topic)
    body = ensure_backlink(cfg, calc, post["html"])

    image = fetch_pixabay_image(post["image_query"], state.get("used_image_ids", []))
    body = add_pixabay_image(body, image, post["title"])

    labels = list(dict.fromkeys([calc["name"], "Calculators"] + post["labels"]))[:5]

    if args.mode == "dry-run":
        out = ROOT / "output" / "preview.html"
        out.parent.mkdir(exist_ok=True)
        out.write_text(f"<h1>{html.escape(post['title'])}</h1>\n{body}", encoding="utf-8")
        log(f"Preview save hua: {out}")
        log(f"Title: {post['title']} | Labels: {labels}")
        return

    url = post_to_blogger(post["title"], body, labels, as_draft=(args.mode == "draft"))
    log(f"Blogger par ho gaya ({args.mode}): {url}")

    state["posts"].append({
        "date": today,
        "calculator": calc["name"],
        "topic": topic["topic"],
        "title": post["title"],
        "mode": args.mode,
        "url": url,
    })
    if image:
        state.setdefault("used_image_ids", []).append(image["id"])
    save_json("state.json", state)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)