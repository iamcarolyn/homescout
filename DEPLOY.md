# HomeScout — Deployment Guide (Railway)

## Prerequisites

- Docker installed locally (for verification)
- GitHub account
- Railway account at railway.app
- DNS access to iamcarolyn.ai

---

## Step 1 — Push to GitHub

```bash
git init
git add .
git commit -m "HomeScout Phase 1 + Phase 2"
git remote add origin https://github.com/iamcarolyn/home-scout.git
git push -u origin main
```

---

## Step 2 — Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Select `iamcarolyn/home-scout`
5. Railway auto-detects the `Dockerfile` at the repo root

---

## Step 3 — Set Environment Variables

In Railway → your project → **Variables**, add:

| Key | Value |
|---|---|
| `GEMINI_API_KEY` | Your key from aistudio.google.com |
| `TAVILY_API_KEY` | Your key from app.tavily.com |

Railway passes these to the container at runtime. supervisord forwards them to the FastAPI process.

---

## Step 4 — Set Custom Domain

1. In Railway → your project → **Settings** → **Domains**
2. Click **Add Custom Domain**
3. Enter: `home-scout.iamcarolyn.ai`
4. Railway provides a Railway hostname (e.g. `home-scout-production.up.railway.app`)

---

## Step 5 — Configure DNS

At your DNS provider for `iamcarolyn.ai`, add a CNAME record:

```
Type:  CNAME
Name:  home-scout
Value: home-scout-production.up.railway.app
TTL:   300
```

---

## Step 6 — Deploy

Click **Deploy** in Railway. The build process:

1. Builds from `Dockerfile`
2. Installs Python deps via `pip install -r requirements.txt`
3. Installs and builds Next.js frontend via `npm ci && npm run build`
4. Copies static assets to standalone output
5. Starts nginx (port 8080) + Next.js (port 3000) + FastAPI (port 8000) via supervisord

---

## Step 7 — Verify

```bash
# Health check
curl https://home-scout.iamcarolyn.ai/api/backend/health

# Expected: {"status": "ok"}
```

Then open `https://home-scout.iamcarolyn.ai` and run a search. Confirm:
- SSE events stream live in the agent feed
- All 5 agents appear in sequence
- Scorecard renders when Gavel completes

---

## Continuous Deployment

Every push to `main` triggers an automatic Railway rebuild and redeploy.
No manual intervention needed after initial setup.

---

## Local Docker Verification

Before deploying, verify the build locally:

```bash
docker build -t homescout .

docker run -p 8080:8080 \
  -e GEMINI_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  homescout
```

Then open http://localhost:8080 and test the full search → feed → scorecard flow.

Health check: http://localhost:8080/api/backend/health

---

## Architecture in Production

```
https://home-scout.iamcarolyn.ai
└── Railway container (port 8080 exposed)
    ├── nginx (8080) — routes traffic
    │   ├── / → Next.js on port 3000
    │   └── /api/backend/ → FastAPI on port 8000
    ├── Next.js frontend (3000) — search UI + live agent feed + scorecard
    └── FastAPI backend (8000) — SSE streaming crew runner
```
