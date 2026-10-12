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
user = f"""Write a blog post.

Topic: Calculating Taxes Using a Percentage Calculator
Main keyword: percentage calculator
Language: {cfg['language']}
Length: {cfg['min_words']}-{cfg['max_words']} words.

Rules:
- Output ONLY JSON with keys: "title", "image_query", "labels", "html".
- "title": catchy, includes the main keyword, max 65 characters.
- "image_query": 2-4 English words for a relevant stock photo (e.g. "calculator money desk"). No people's names.
- "labels": array of 2-4 short labels.
- "html": the post body in HTML using ONLY h2, h3, p, ul, ol, li, table, tr, th, td, strong, em, a tags.
  No h1, no <html>/<body>, no inline CSS, no markdown.
- Structure: short intro, clear sections, one fully worked numeric example (double-check the maths),
  a short step-by-step "how to use the calculator" section, common mistakes, 4 FAQs, short conclusion.
- Add this link naturally 2 times with different anchor text (not just "click here"):
  <a href="{link}">{calc['name']}</a>
- If the topic is about money/finance/tax, add a one-line note that this is general information, not professional advice.
- Write in a natural human tone, no filler, no repeated sentences."""

body = {
    'model': 'allam-2-7b',
    'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
    'temperature': 0.7,
}
r = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=body, timeout=90)
print('Status:', r.status_code)
data = r.json()
msg = data['choices'][0]['message']
content = msg.get('content') or msg.get('reasoning') or ''
print('Content length:', len(content))

# Try to parse
text = content.strip()
text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
try:
    parsed = json.loads(text)
    print('\nParsed successfully!')
    print('Keys:', list(parsed.keys()))
    print('Title:', parsed.get('title'))
    print('Image query:', parsed.get('image_query'))
    print('Labels:', parsed.get('labels'))
    print('HTML length:', len(parsed.get('html', '')))
except json.JSONDecodeError as e:
    print('\nJSON parse error:', e)
    print('Error position:', e.pos)
    print('Text around error:', repr(text[max(0, e.pos-100):e.pos+100]))