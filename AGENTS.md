# Project: CalcNotebook Blogger Agent

Python automation that writes one blog post per day for https://calcnotebook.vercel.app
and posts it to Blogger. Controlled from GitHub Actions, runnable locally from VS Code.

## Structure
- `scripts/agent.py` main pipeline (topic -> Groq writing -> Pexels image -> backlink -> Blogger)
- `scripts/get_refresh_token.py` one-time Google OAuth helper
- `config.json` site url, language, word count, 7 calculators (one per weekday)
- `state.json` memory of published topics and used image ids (committed by the workflow)
- `.github/workflows/blog.yml` daily schedule + manual run (dry-run / draft / publish)

## Rules for the AI assistant
- User is a beginner. Explain each step in simple Hinglish, give exact commands for Windows PowerShell.
- Never print, hardcode or commit secrets. Keys live only in `.env` (local) and GitHub Secrets.
- Do not change the folder structure or rename files without asking.
- Keep code simple and commented. Prefer small changes; run `python scripts/agent.py` (dry-run) to test.
- Every blog must include a backlink to the day's calculator page and must not repeat past topics.
- Always test with `--mode dry-run` first, then `--mode draft`, then `--mode publish`.
