# OpenCode mein copy-paste karne wale prompts

Pehle terminal mein project folder kholo aur `opencode` chalao. `AGENTS.md` OpenCode khud padh leta hai.

## 1. Project samjhao
```
Read AGENTS.md, README.md, config.json and scripts/agent.py. Explain in simple Hinglish
what this project does and what I still need to set up before the first run.
```

## 2. Setup + dry-run
```
Help me set up this project on Windows: create venv, install requirements.txt,
create .env from .env.example, and run `python scripts/agent.py --mode dry-run`.
If there is any error, fix it and explain in simple Hinglish.
```

## 3. Blogger OAuth (403 fix)
```
Help me get GOOGLE_REFRESH_TOKEN using scripts/get_refresh_token.py.
Then run `python scripts/agent.py --mode draft`. If Blogger returns 403,
tell me exactly which Google Cloud / Blogger setting to check.
```

## 4. Quality sudharna
```
Open output/preview.html content logic in scripts/agent.py (write_post prompt).
Make the blog more helpful: add a comparison table where useful and make FAQs shorter.
Do not change anything else.
```

## 5. GitHub Actions
```
Check .github/workflows/blog.yml. List exactly which GitHub secrets I must add,
and how to give the workflow write permission. Then guide me to run it manually with mode dry-run.
```

## 6. Naya feature (jab ready ho)
```
Add a --count option so I can generate 2 posts in one run, without breaking the
"no repeated topics" logic in state.json.
```
