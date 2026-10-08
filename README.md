# CalcNotebook Blogger Agent

Roz 1 blog, har din alag calculator (weekly rotation):
Mon EMI, Tue GST, Wed BMI, Thu Percentage, Fri Age, Sat CGPA, Sun Stamp Duty.
Blog mein image + CalcNotebook ka backlink automatically lagta hai.

## Setup (local, VS Code)
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # phir .env mein keys bharo
```

### Keys kahan se aayengi
| Key | Kahan se |
|---|---|
| GROQ_API_KEY | console.groq.com |
| SERPAPI_KEY | serpapi.com (optional, topic research) |
| PIXABAY_API_KEY | pixabay.com/api/docs (free account, key wahin dikhti hai) |
| IMAGE_REPO | apna GitHub repo, jaise `Neelam7590/calcnotebook-blog-agent` (repo PUBLIC rakho, warna image blog mein nahi dikhegi) |
| BLOG_ID | Blogger dashboard URL mein `blogID=...` |
| GOOGLE_CLIENT_ID / SECRET | Google Cloud Console -> Credentials -> OAuth client (Desktop app) |
| GOOGLE_REFRESH_TOKEN | `python scripts/get_refresh_token.py` |

Google Cloud mein **Blogger API v3 enable** karna zaruri hai, aur OAuth consent screen mein
apna Gmail **Test user** mein add karo.

## Chalane ke tareeke
```powershell
python scripts\agent.py                    # dry-run, output\preview.html banega
python scripts\agent.py --day friday       # kisi aur din ka calculator test
python scripts\agent.py --mode draft       # Blogger par draft
python scripts\agent.py --mode publish     # Blogger par live
```

## GitHub Actions
1. Repo -> Settings -> Secrets and variables -> Actions -> New repository secret.
   Ye 7 secrets banao: `GROQ_API_KEY, SERPAPI_KEY, PIXABAY_API_KEY, BLOG_ID,
   GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN`
2. Repo -> Settings -> Actions -> General -> Workflow permissions -> **Read and write permissions**.
3. Actions tab -> "Daily Blog Post" -> Run workflow -> mode `dry-run` (test), phir `draft`, phir `publish`.
4. Schedule: `.github/workflows/blog.yml` mein cron (UTC). `30 2 * * *` = subah 8:00 IST.

## Troubleshooting
- **403 on Blogger post**: Blogger API enable nahi hai, ya Gmail Test user mein nahi hai, ya woh Gmail us blog ka owner/admin nahi hai, ya BLOG_ID galat hai. Sabse pehle `--mode draft` se test karo.
- **invalid_grant**: refresh token expire/revoke hua. `get_refresh_token.py` dobara chalao (OAuth app "Testing" mode mein token 7 din mein expire ho sakta hai; consent screen ko "In production" kar do).
- **Groq 429**: rate limit. Thodi der baad dobara ya model badlo (`config.json` -> `groq_model`).
