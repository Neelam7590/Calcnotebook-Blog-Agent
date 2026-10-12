import requests
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT = Path.cwd()
load_dotenv(ROOT / '.env')
key = os.getenv('GROQ_API_KEY')
headers = {'Authorization': 'Bearer ' + key}

# Test with JSON mode
body = {
    'model': 'openai/gpt-oss-20b',
    'messages': [{'role': 'user', 'content': 'Return JSON: {"test": "hello"}'}],
    'temperature': 0.7,
    'response_format': {'type': 'json_object'}
}
r = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=body, timeout=30)
print('Status:', r.status_code)
print('Response:', r.text[:500])

# Test without JSON mode
body2 = {
    'model': 'openai/gpt-oss-20b',
    'messages': [{'role': 'user', 'content': 'Say hello'}],
    'temperature': 0.7,
}
r2 = requests.post('https://api.groq.com/openai/v1/chat/completions', headers=headers, json=body2, timeout=30)
print('\nWithout JSON mode:')
print('Status:', r2.status_code)
print('Response:', r2.text[:500])