# CalcNotebook Blog Agent

An automated blogging agent that writes and publishes one calculator-focused blog post every day to [CalcNotebook Blog](https://calcnotebookblog.blogspot.com) on Blogger. Each post comes with an image, worked examples with accurate numbers, and a backlink to the CalcNotebook calculator website.

It runs fully on its own using GitHub Actions, so no manual posting is needed.

## Features

- **Daily auto-publishing** to Blogger through the Blogger API v3
- **Weekly calculator rotation**, so every day covers a different topic:

  | Day | Calculator |
  |-----|------------|
  | Monday | EMI |
  | Tuesday | GST |
  | Wednesday | BMI |
  | Thursday | Percentage |
  | Friday | Age |
  | Saturday | CGPA |
  | Sunday | Stamp Duty |

- **Accurate numbers**: all formulas and example calculations are computed in Python. The LLM only writes the explanatory paragraphs, so results are never made up.
- **Images added automatically** from Pixabay, stored in this repo and served through the jsDelivr CDN
- **Automatic backlinks** to the CalcNotebook calculator website in every post
- **Optional topic research** using SerpApi
- **Dry-run, draft and publish modes** for safe testing before going live
- **State tracking** (`state.json`) to avoid duplicate posts

## Tech Stack

- Python
- Groq API (LLM for paragraph writing)
- Blogger API v3 with Google OAuth
- Pixabay API (images)
- SerpApi (optional research)
- GitHub Actions (scheduling and automation)
- jsDelivr (image CDN)

## Project Structure

```
.
├── .github/workflows/   # GitHub Actions workflow (daily schedule)
├── scripts/             # Agent code (agent.py, get_refresh_token.py, ...)
├── images/              # Images used in published posts
├── config.json          # Agent settings (e.g. Groq model)
├── state.json           # Tracks what has already been posted
├── requirements.txt     # Python dependencies
└── AGENTS.md            # Notes for AI coding agents
```

## Setup (Local)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then fill in your keys
```

### Environment variables

| Key | Where to get it |
|-----|-----------------|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) |
| `SERPAPI_KEY` | [serpapi.com](https://serpapi.com) (optional) |
| `PIXABAY_API_KEY` | [pixabay.com/api/docs](https://pixabay.com/api/docs/) |
| `IMAGE_REPO` | Your GitHub repo, e.g. `Neelam7590/Calcnotebook-Blog-Agent` (**must be public**, otherwise images will not load on the blog) |
| `BLOG_ID` | In the Blogger dashboard URL (`blogID=...`) |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Google Cloud Console, Credentials, OAuth client (Desktop app) |
| `GOOGLE_REFRESH_TOKEN` | Run `python scripts/get_refresh_token.py` |

Enable the **Blogger API v3** in Google Cloud and add your Gmail as a **Test user** on the OAuth consent screen.

## Usage

```bash
python scripts/agent.py                    # dry run, creates output/preview.html
python scripts/agent.py --day friday       # test another day's calculator
python scripts/agent.py --mode draft       # save as a draft on Blogger
python scripts/agent.py --mode publish     # publish live on Blogger
```

## Deploying with GitHub Actions

1. Go to **Settings → Secrets and variables → Actions** and add these repository secrets:
   `GROQ_API_KEY`, `SERPAPI_KEY`, `PIXABAY_API_KEY`, `BLOG_ID`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN`
2. Go to **Settings → Actions → General → Workflow permissions** and select **Read and write permissions**.
3. Open the **Actions** tab, choose the daily blog workflow, and use **Run workflow** to test (dry run first, then draft, then publish).
4. The schedule is defined in `.github/workflows/` using a cron expression (UTC).

> **Security note:** never commit API keys or tokens. Keep all secrets in GitHub Secrets or a local `.env` file (which is git-ignored).

## Troubleshooting

- **403 on Blogger post**: the Blogger API is not enabled, your Gmail is not added as a Test user, the account is not the blog owner/admin, or `BLOG_ID` is wrong. Test with `--mode draft` first.
- **`invalid_grant`**: the refresh token expired or was revoked. Run `get_refresh_token.py` again. Moving the OAuth consent screen to "In production" avoids the 7-day expiry of Testing mode.
- **Groq 429**: rate limit reached. Wait a while or change the model in `config.json` (`groq_model`).
- **Images not showing on the blog**: make sure this repository is public, since the images are served from it through jsDelivr.

## Author

**Neelam Dhiman**
GitHub: [Neelam7590](https://github.com/Neelam7590) · LinkedIn: [neelam-dhiman](https://linkedin.com/in/neelam-dhiman-b5a8b4422)
