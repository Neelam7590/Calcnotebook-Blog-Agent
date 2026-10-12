import requests
import json
import os
import re
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

system = (
    "You are an experienced Indian content writer who writes accurate, original, "
    "helpful blog posts about calculators, finance and everyday maths. "
    "Never invent laws, tax rates or statistics you are not sure about; "
    "if rates vary by state or date, say so and tell readers to verify."
)
user = f"""Write a blog post and output ONLY a single JSON object.

Topic: How to Calculate the Discount Percentage on Your Online Shopping Deals: A Step-by-Step Guide
Main keyword: discount percentage
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

body = {
    'model': 'openai/gpt-oss-20b',
    'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
    'temperature': 0.7,
}
r = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=body, timeout=90)
print('Status:', r.status_code)
data = r.json()
msg = data['choices'][0]['message']
print('Content:', repr(msg.get('content', ''))[:500])
print('Reasoning:', repr(msg.get('reasoning', ''))[:500])