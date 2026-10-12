import requests
import json
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path.cwd()
load_dotenv(ROOT / '.env')
key = os.getenv('GROQ_API_KEY')
headers = {'Authorization': 'Bearer ' + key}

with open(ROOT / 'config.json') as f:
    cfg = json.load(f)

calc = cfg['calculators']['thursday']
link = cfg['site_url'] + calc['url']

system = 'You are an experienced Indian content writer. Output ONLY valid JSON with keys: title, image_query, labels, html.'
user = '''Write a blog post.

Topic: How to Calculate Your Effective Tax Rate on Income in India - A Practical Guide
Main keyword: effective tax rate
Language: English
Length: 900-1300 words.

Rules:
- Output ONLY JSON with keys: "title", "image_query", "labels", "html".
- "title": catchy, includes the main keyword, max 65 characters.
- "image_query": 2-4 English words for a relevant stock photo.
- "labels": array of 2-4 short labels.
- "html": the post body in HTML using ONLY h2, h3, p, ul, ol, li, table, tr, th, td, strong, em, a tags.
  No h1, no <html>/<body>, no inline CSS, no markdown.
- Add this link 2 times: <a href="%s">%s</a>''' % (link, calc['name'])

body = {
    'model': 'openai/gpt-oss-20b',
    'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
    'temperature': 0.7,
}
r = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=body, timeout=90)
print('Status:', r.status_code)
data = r.json()
content = data['choices'][0]['message']['content']
print('Content length:', len(content))
print('First 500 chars:', content[:500])
print('Last 500 chars:', content[-500:])

# Try to parse
import re
text = content.strip()
text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
try:
    parsed = json.loads(text)
    print('\nParsed successfully!')
    print('Keys:', parsed.keys())
    print('Title:', parsed.get('title'))
    print('Image query:', parsed.get('image_query'))
    print('Labels:', parsed.get('labels'))
    print('HTML length:', len(parsed.get('html', '')))
except json.JSONDecodeError as e:
    print('\nJSON parse error:', e)
    print('Text around error:', text[max(0, e.pos-50):e.pos+50])