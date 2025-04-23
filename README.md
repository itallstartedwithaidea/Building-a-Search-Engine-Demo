# Google-Sheets SERP on Cloud Run

A tiny search engine front-end:

| piece | tech | purpose |
|-------|------|---------|
| **Cloud Run service** | FastAPI + SerpAPI + OpenAI | Returns 10 search hits as JSON |
| **Dockerfile** | python:3.11-slim | containerize for Cloud Run |
| **Google Sheet** | Apps Script | instant SERP view inside Sheets |

---

## 1-click deploy

```bash
./setup/create-secrets.sh      # OPENAI key (required) + SerpAPI key (opt.)
./setup/deploy.sh              # build & push to Cloud Run
