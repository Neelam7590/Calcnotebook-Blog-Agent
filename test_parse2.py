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

Topic: How to Calculate Your Profit Margin on a Product Using a Percentage Calculator
Main keyword: percentage calculator
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
content = msg.get('content') or ''
reasoning = msg.get('reasoning') or ''
full_text = content + reasoning

# Test parse_json logic
text = full_text.strip()
text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.M).strip()
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
                        print(f'Found candidate at {start}-{i}: keys={list(parsed.keys())}')
                except json.JSONDecodeError as e:
                    pass
                start = None
print(f'Total candidates: {len(candidates)}')
if candidates:
    last = candidates[-1]
    print('Last candidate keys:', list(last.keys()))
    print('Title:', last.get('title'))
    print('HTML length:', len(last.get('html', '')))
else:
    print('No candidates found!')
    # Debug: find all { and } positions
    brace_positions = [(i, ch) for i, ch in enumerate(text) if ch in '{}']
    print('First 20 brace positions:', brace_positions[:20])
    print('Last 20 brace positions:', brace_positions[-20:])