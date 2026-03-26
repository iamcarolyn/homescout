# HomeScout — Product Requirements Document

## Project Overview
HomeScout is a standalone Python application built with CrewAI.
You enter a city, neighborhood, or zip code and a crew of five specialized agents
researches it from every angle — property prices, schools, safety, and lifestyle.
Each agent owns its domain, outputs chain sequentially, and a final verdict writer
synthesizes everything into a structured neighborhood scorecard.
The public frontend streams each agent's reasoning live to the browser as the crew runs —
users watch the agents work in real time before the scorecard renders.
Deploys to Railway as a single Docker container at home-scout.iamcarolyn.ai.
This project applies CrewAI's sequential delegation pattern to real-world
data research using free APIs: Tavily, Census Bureau, and Overpass (OpenStreetMap).

## Local Path
~/projects/home-scout/

## Tech Stack
- **Agent Framework:** CrewAI (latest)
- **LLM Brain:** Gemini Flash (gemini-2.5-flash-lite)
- **Search Tool:** Tavily API
- **Demographics Tool:** Census Bureau API (free, no billing, no key needed)
- **POI Tool:** Overpass API — OpenStreetMap (free, no key needed)
- **Geocoding:** Nominatim — OpenStreetMap (free, no key needed)
- **Public Frontend:** Next.js (App Router)
- **Public Backend:** FastAPI — SSE streaming + CrewAI crew
- **Deployment:** Railway — single Docker container
- **Domain:** home-scout.iamcarolyn.ai
- **Runtime:** Python 3.11+
- **Output:** Structured neighborhood scorecard

## Architecture
```
home-scout.iamcarolyn.ai
└── Docker container on Railway (port 8080)
    ├── nginx (8080) — routes traffic
    │   ├── / → Next.js on port 3000
    │   └── /api/backend/ → FastAPI on port 8000
    ├── Next.js frontend (3000) — search UI + live agent feed + scorecard
    └── FastAPI backend (8000) — SSE streaming crew runner
```

## Key UX Pattern — Live Agent Feed
When a user submits a location:
1. Frontend opens a streaming fetch connection to FastAPI via /api/scout
2. Backend starts the CrewAI crew in a background thread
3. Every agent step fires a step_callback → pushed to a queue → streamed as SSE event
4. Frontend appends each event to a scrolling feed, color-coded by agent
5. When Gavel completes, the final scorecard JSON arrives as the last SSE event
6. Scorecard renders below the feed

---

## Full Actor Roster

| # | Actor | Name | Role | Task |
|---|---|---|---|---|
| 1 | Property Scout | Brick | Agent | Avg home prices, price trends, Census demographics |
| 2 | School Analyst | Scholar | Agent | School ratings, district performance via Tavily |
| 3 | Safety Analyst | Shield | Agent | Crime stats, safety perception via Tavily |
| 4 | Lifestyle Scout | Vibe | Agent | Parks, gyms, restaurants, transit via Overpass |
| 5 | Verdict Writer | Gavel | Agent | Synthesizes all four into final neighborhood scorecard |
| 6 | Crew Manager | The Block | Crew | Sequential delegation, callback wiring |
| 7 | Backend | server.py | FastAPI | SSE streaming endpoint, crew runner |
| 8 | Frontend | Next.js | App Router | Search UI, agent feed, scorecard display |

## Agent Personas
- **Brick:** Grounded, data-driven, pragmatic. Knows what homes actually cost and why.
- **Scholar:** Thorough, research-oriented. Finds the real story behind school ratings.
- **Shield:** Unflinching. Presents safety data plainly — no sugarcoating, no alarm.
- **Vibe:** Curious, local-minded. Finds what makes a neighborhood actually liveable.
- **Gavel:** Balanced, decisive. Weighs all inputs, delivers a clear honest verdict.

## Agent Feed Color Coding

| Agent | Color | Hex |
|---|---|---|
| Brick | Amber | #f59e0b |
| Scholar | Blue | #3b82f6 |
| Shield | Red | #ef4444 |
| Vibe | Green | #22c55e |
| Gavel | Purple | #a855f7 |
| System | Grey | #6b7280 |

---

## Phase 1 — CrewAI Backend

### Task 1 — Project Scaffold
- [x] Create project directory structure:
```
home-scout/
├── agents/
│   ├── brick.py
│   ├── scholar.py
│   ├── shield.py
│   ├── vibe.py
│   └── gavel.py
├── tasks/
│   ├── property_task.py
│   ├── school_task.py
│   ├── safety_task.py
│   ├── lifestyle_task.py
│   └── scorecard_task.py
├── tools/
│   ├── tavily_search.py
│   ├── census_tool.py
│   └── overpass_tool.py
├── output/
├── crew.py
├── server.py
├── scout.py
├── config.py
├── requirements.txt
└── .env.example
```
- [x] Create requirements.txt with:
  crewai, crewai-tools, google-generativeai, tavily-python, httpx,
  fastapi, uvicorn, python-dotenv
- [x] Create .env.example with placeholders for:
  GEMINI_API_KEY, TAVILY_API_KEY
- [x] Create config.py to load all env vars via python-dotenv
- [x] Configure Gemini Flash as the LLM for all agents:
  ```python
  from crewai import LLM
  llm = LLM(model="gemini/gemini-2.5-flash-lite", api_key=GEMINI_API_KEY)
  ```

**Acceptance criteria:** Directory exists. pip install -r requirements.txt completes without errors.

---

### Task 2 — Tavily Search Tool
- [x] Create tools/tavily_search.py
- [x] Implement search(query: str) -> str using Tavily API
- [x] Returns formatted string of top 5 results with title, url, and snippet
- [x] Register as CrewAI tool using @tool decorator
- [x] Handle API errors gracefully — return error string on failure

**Acceptance criteria:** Tool callable standalone returns valid results for a test query.

---

### Task 3 — Census Tool
- [x] Create tools/census_tool.py
- [x] Implement get_census_data(zip_code: str) -> dict using Census Bureau ACS5 API
  - Endpoint: https://api.census.gov/data/2022/acs/acs5
  - Variables: B19013_001E (median income), B25077_001E (median home value),
    B01003_001E (population), B25003_002E (owner-occupied), B25003_003E (renter-occupied)
  - No API key required
  - Returns dict with human-readable keys
  - Missing fields return "Data not available" — never crashes
- [x] Register as CrewAI tool using @tool decorator

**Acceptance criteria:** Returns valid dict for a test zip code. Missing fields handled gracefully.

---

### Task 4 — Overpass Tool
- [x] Create tools/overpass_tool.py
- [x] Implement get_pois(lat: float, lon: float, radius_meters: int = 2000) -> dict
  - Queries https://overpass-api.de/api/interpreter
  - Fetches counts and names (max 5 per category) for:
    parks, gyms, restaurants, grocery stores, transit stops, schools
  - Always sleep 1 second before request — respect Overpass rate limits
  - Handle timeouts and errors gracefully — return empty dict on failure
- [x] Implement geocode_location(location: str) -> tuple[float, float] | None
  - Uses Nominatim: https://nominatim.openstreetmap.org/search
  - Returns (lat, lon) or None on failure
  - User-Agent header: "HomeScout/1.0"
  - Sleep 1 second before request
- [x] Register get_pois as CrewAI tool

**Acceptance criteria:** get_pois returns valid POI dict for a test coordinate.
geocode_location returns valid (lat, lon) for a test city name.

---

### Task 5 — Agents
Each agent must be a factory function create_[name]() returning a CrewAI Agent.
Required for callback wiring in crew.py.

- [x] Create agents/brick.py — create_brick()
  - Role: Real Estate Market Analyst
  - Goal: Find current average home prices, price trends, Census demographic data
  - Backstory: Grounded, data-driven. Cuts through hype to show what homes actually cost.
  - Tools: tavily_search, census_tool
  - verbose=True, allow_delegation=False

- [x] Create agents/scholar.py — create_scholar()
  - Role: Education Research Analyst
  - Goal: Find school quality, district performance, ratings, parent perception
  - Backstory: Thorough, research-oriented. Knows ratings are proxies — finds what they mean.
  - Tools: tavily_search
  - verbose=True, allow_delegation=False

- [x] Create agents/shield.py — create_shield()
  - Role: Safety and Crime Research Analyst
  - Goal: Find crime statistics, safety trends, local safety perception
  - Backstory: Unflinching. Presents safety data plainly — no alarm, no sugarcoating.
  - Tools: tavily_search
  - verbose=True, allow_delegation=False

- [x] Create agents/vibe.py — create_vibe()
  - Role: Neighborhood Lifestyle Analyst
  - Goal: Map practical liveability — POI counts, walkability, neighborhood character
  - Backstory: Curious, local-minded. Uses real POI data to map what is actually there.
  - Tools: overpass_tool, tavily_search
  - verbose=True, allow_delegation=False

- [x] Create agents/gavel.py — create_gavel()
  - Role: Neighborhood Evaluator
  - Goal: Synthesize all research into a structured, honest neighborhood scorecard
  - Backstory: Balanced and decisive. Delivers verdicts that are specific and useful.
  - Tools: none
  - verbose=True, allow_delegation=False

**Acceptance criteria:** All five factory functions importable and initialize without errors.

---

### Task 6 — Task Definitions
Each task must be a factory function create_[name]_task(agent, context=[]).

- [x] Create tasks/property_task.py — create_property_task(agent)
  - Assigned to Brick
  - Uses census_tool for zip code data + tavily_search for price trends
  - If {location} is not a zip code, identify the zip first via tavily_search
  - Expected output: median home value (Census), avg list price (Tavily),
    price trend direction, owner/renter ratio, median income, data sources

- [x] Create tasks/school_task.py — create_school_task(agent, context)
  - Assigned to Scholar
  - context: [property_task]
  - Expected output: school names, ratings or performance notes, district context,
    plain summary of overall school quality

- [x] Create tasks/safety_task.py — create_safety_task(agent, context)
  - Assigned to Shield
  - context: [property_task, school_task]
  - Expected output: crime rate vs city average, trend direction, resident perception summary

- [x] Create tasks/lifestyle_task.py — create_lifestyle_task(agent, context)
  - Assigned to Vibe
  - context: [property_task, school_task, safety_task]
  - Geocodes {location} first, then calls get_pois for POI counts
  - Expected output: POI counts with named highlights, walkability summary,
    qualitative neighborhood character

- [x] Create tasks/scorecard_task.py — create_scorecard_task(agent, context)
  - Assigned to Gavel
  - context: [all four tasks]
  - Output format must be exactly:
    ```
    PRICE SCORE: X/10 — rationale
    SCHOOL SCORE: X/10 — rationale
    SAFETY SCORE: X/10 — rationale
    LIFESTYLE SCORE: X/10 — rationale
    OVERALL VERDICT: [Strong Buy / Consider / Proceed with Caution / Pass]
    KEY STRENGTHS:
    - item
    KEY CONCERNS:
    - item
    SUMMARY: 2-3 sentences
    ```
  - Strict format required — server.py parses scores via regex

**Acceptance criteria:** All five factory functions importable. Context chaining correct.
Scorecard format exactly matches the specified structure.

---

### Task 7 — crew.py
- [x] Create crew.py
- [x] Implement build_crew(step_callback=None, task_callback=None) -> Crew:
  ```python
  def build_crew(step_callback=None, task_callback=None):
      brick = create_brick()
      scholar = create_scholar()
      shield = create_shield()
      vibe = create_vibe()
      gavel = create_gavel()

      property_task = create_property_task(brick)
      school_task = create_school_task(scholar, context=[property_task])
      safety_task = create_safety_task(shield, context=[property_task, school_task])
      lifestyle_task = create_lifestyle_task(vibe, context=[property_task, school_task, safety_task])
      scorecard_task = create_scorecard_task(gavel, context=[property_task, school_task, safety_task, lifestyle_task])

      return Crew(
          agents=[brick, scholar, shield, vibe, gavel],
          tasks=[property_task, school_task, safety_task, lifestyle_task, scorecard_task],
          process=Process.sequential,
          verbose=True,
          step_callback=step_callback,
          task_callback=task_callback
      )
  ```

**Acceptance criteria:** build_crew() returns a Crew that kicks off without errors.
Callbacks wire correctly — step_callback fires on each agent step.

---

### Task 8 — scout.py (CLI Runner)
- [x] Create scout.py as CLI entry point
- [x] Accepts: python scout.py "Arcadia Phoenix AZ" or python scout.py "85028"
- [x] Calls build_crew() with no callbacks, kicks off with location input
- [x] Saves scorecard to output/scorecard_YYYY-MM-DD_HH-MM_[slug].md
- [x] Accepts --dry-run: runs Brick only, stops cleanly

**Acceptance criteria:** python scout.py "location" produces a complete scorecard file.

---

### Task 9 — server.py (FastAPI SSE Backend)
- [x] Create server.py as the FastAPI app
- [x] Implement GET /health → { "status": "ok" }
- [x] Implement POST /scout as an SSE streaming endpoint:
  - Accepts JSON body: { "location": "Arcadia Phoenix AZ" }
  - Creates a per-request queue
  - Wires step_callback and task_callback to push events to queue
  - Runs crew in background thread
  - Streams queue events as SSE: `data: {json}\n\n`
  - step events: { type: "step", agent: name, message: text }
  - task_complete events: { type: "task_complete", agent: name, message: "Task complete." }
  - system events: { type: "system", agent: "System", message: text }
  - done event: { type: "done", scorecard: parsed_dict, error: null }
  - Truncates step messages over 500 chars with ellipsis
  - parse_scorecard(text) extracts scores via regex from Gavel's output
  - Timeout: 180 seconds — returns error event if exceeded
  - SSE headers: Cache-Control: no-cache, X-Accel-Buffering: no
  - CORS middleware: allow_origins=["*"]
- [x] Runs on port 8000

**Acceptance criteria:** uvicorn server:app starts cleanly. POST /scout streams SSE
events and terminates with a done event containing a parsed scorecard dict.
parse_scorecard correctly extracts all score fields from a test scorecard string.

---

## Phase 2 — Next.js Frontend + Docker + Railway

### Task 10 — Next.js Project Scaffold
- [x] Scaffold Next.js app with App Router inside ~/projects/home-scout/frontend/
- [x] Install dependencies: tailwindcss, framer-motion, lucide-react
- [x] Configure Tailwind custom theme:
  - colors: hs-forest (#1a3c34), hs-cream (#f5f0e8), hs-amber (#d4a017),
    hs-sage (#7a9e7e), hs-white (#ffffff), hs-border (#d9d0be),
    hs-green (#2d6a4f), hs-red (#c0392b), hs-orange (#e67e22)
  - fonts: display (Playfair Display or Bitter), sans (Source Sans 3 or Lato)
- [x] Add Google Font imports to app/layout.tsx
- [x] next.config.ts: add env block exposing BACKEND_URL to standalone runtime
- [x] Create .env.local: BACKEND_URL=http://localhost:8000
- [x] Create .env.local.example with same key as placeholder
- [x] Confirm npm run dev runs cleanly on localhost:3000

**Acceptance criteria:** Dev server starts. Colors and fonts render correctly.

---

### Task 11 — AgentFeed Component (components/AgentFeed.tsx)
- [x] Create components/AgentFeed.tsx
- [x] Terminal-style scrolling feed — dark background, monospace or semi-mono font
- [x] Agent color coding:
  - Brick: amber (#f59e0b border + text, amber/10 bg)
  - Scholar: blue (#3b82f6)
  - Shield: red (#ef4444)
  - Vibe: green (#22c55e)
  - Gavel: purple (#a855f7)
  - System: gray (#6b7280)
- [x] Each message: colored agent badge (uppercase, bold) + message text below
- [x] Fixed height h-96, overflow-y-auto, auto-scrolls to bottom on new messages
- [x] Pulsing dot indicator while isStreaming is true
- [x] Props: messages: FeedMessage[], isStreaming: boolean, feedEndRef: RefObject

**Acceptance criteria:** Messages render with correct agent colors. Auto-scroll works.
Pulsing indicator shows while streaming.

---

### Task 12 — ScoreCard Component (components/ScoreCard.tsx)
- [x] Create components/ScoreCard.tsx
- [x] Four score badges 2x2 grid (desktop) / stacked (mobile):
  - Domain name, X/10 score, one-line rationale
  - 8-10: hs-green, 6-7: hs-amber, 4-5: hs-orange, 1-3: hs-red
- [x] Overall verdict callout box full width, color-coded background matching verdict
- [x] Key Strengths + Key Concerns two-column cards
- [x] Summary paragraph
- [x] Download button: saves raw scorecard as .md file
- [x] Framer Motion fade-in on mount

**Acceptance criteria:** All fields render. Score colors correct. Download saves .md.

---

### Task 13 — Landing Page (app/page.tsx)
- [x] hs-cream background
- [x] Section 1 — Hero + Search:
  - Serif headline: "Know your neighborhood before you buy."
  - Subheading: "Enter any city, neighborhood, or zip code."
  - Centered search input with submit button: "Scout It" (hs-forest bg)
  - Framer Motion staggered reveal on load
- [x] Section 2 — Agent Progress Bar (visible only while streaming):
  - Five labeled steps: Brick → Scholar → Shield → Vibe → Gavel
  - Active step pulses in hs-amber — inferred from last agent name in feed
  - Completed steps show checkmark in hs-green
- [x] Section 3 — Agent Feed (visible once first SSE event arrives):
  - Renders AgentFeed component
  - Heading: "The crew is working..."
- [x] Section 4 — Scorecard (visible once done event received):
  - Renders ScoreCard component
  - Heading: location name from request
- [x] Footer: HomeScout, tagline, year, "Powered by CrewAI + Gemini"
- [x] SSE consumption pattern:
  ```typescript
  const response = await fetch('/api/scout', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ location })
  })
  const reader = response.body?.getReader()
  // read chunks, parse data: lines, update state
  ```

**Acceptance criteria:** Full flow works — search → progress → feed → scorecard.
Mobile and desktop correct.

---

### Task 14 — Scout API Route (app/api/scout/route.ts)
- [x] Create app/api/scout/route.ts
- [x] Accepts POST with JSON: { location: string }
- [x] Proxies to FastAPI POST BACKEND_URL/scout as a streaming pass-through
- [x] Does not buffer — passes SSE stream directly to browser
- [x] Timeout: 180 seconds
- [x] Error: returns 500 on failure

**Acceptance criteria:** POST to /api/scout streams SSE events from FastAPI to browser
without buffering.

---

### Task 15 — Dockerfile and supervisord
- [x] Create Dockerfile at project root:
  - Base image: python:3.11-slim
  - Install Node.js 20
  - pip install -r requirements.txt
  - cd frontend && npm install && npm run build
  - Install supervisor and nginx
  - Copy supervisord.conf and nginx.conf
  - EXPOSE 8080
  - CMD: supervisord
- [x] Create supervisord.conf:
  - [program:nextjs]: node frontend/.next/standalone/server.js
    environment=PORT=3000,HOSTNAME=0.0.0.0
  - [program:fastapi]: uvicorn server:app --host 0.0.0.0 --port 8000
    environment=PORT=8000,GEMINI_API_KEY=%(ENV_GEMINI_API_KEY)s,TAVILY_API_KEY=%(ENV_TAVILY_API_KEY)s
- [x] Create nginx.conf:
  - listen 8080
  - / → proxy_pass http://localhost:3000
  - /api/backend/ → proxy_pass http://localhost:8000/
  - SSE-critical on /api/backend/ location block:
    ```
    proxy_buffering off;
    proxy_cache off;
    proxy_set_header Connection '';
    proxy_http_version 1.1;
    chunked_transfer_encoding on;
    ```
- [x] .dockerignore: .venv, node_modules, output/, .env

**Acceptance criteria:** docker build completes. docker run -p 8080:8080 serves app on
localhost:8080. SSE stream reaches browser without buffering. /health returns ok.
Full search → feed → scorecard flow works in Docker.

---

### Task 16 — Deploy to Railway
- [x] Create DEPLOY.md:
  1. Push to GitHub: github.com/iamcarolyn/home-scout
  2. railway.app → New Project → Deploy from GitHub
  3. Dockerfile auto-detected at root
  4. Set env vars: GEMINI_API_KEY, TAVILY_API_KEY
  5. Set custom domain: home-scout.iamcarolyn.ai
  6. CNAME at iamcarolyn.ai: home-scout → Railway hostname
  7. Deploy
  8. Verify SSE stream works end to end at live URL
- [x] Document: every push to main triggers Railway rebuild
- [x] Do not deploy yet — prepare only

**Acceptance criteria:** DEPLOY.md complete. Dockerfile builds locally.

---

## Ralph Loop Run Instructions

### Prerequisites

```bash
cd ~/projects/home-scout
python3 -m venv .venv
source .venv/bin/activate
cp .env.example .env
# fill in GEMINI_API_KEY and TAVILY_API_KEY
claude
```

---

### Run Phase 1 — CrewAI Backend + FastAPI SSE

```
/ralph-wiggum:ralph-loop "Read PRD.md and complete every unchecked task in Phase 1 in order.
Check off each task in PRD.md as you complete it.
After each task verify the acceptance criteria passes before moving on.
If blocked document it in BLOCKED.md and move to the next task.
Framework is CrewAI with sequential process.
LLM is Gemini Flash — model string: gemini/gemini-2.5-flash-lite.
All agents must be factory functions: create_brick(), create_scholar(), create_shield(), create_vibe(), create_gavel().
All tasks must be factory functions: create_[name]_task(agent, context=[]).
This is required for step_callback and task_callback wiring in crew.py.
Census Bureau ACS5 API is free — no key needed.
Overpass API and Nominatim are free — no key needed. Always sleep 1 second before requests.
server.py is a FastAPI SSE streaming endpoint — crew runs in background thread, events pushed to per-request queue.
Main CLI entry point is scout.py.
When all Phase 1 tasks are complete output HOME_SCOUT_COMPLETE." \
--completion-promise "HOME_SCOUT_COMPLETE" \
--max-iterations 25
```

---

### Run Phase 2 — Frontend + Docker + Railway Prep

```
/ralph-wiggum:ralph-loop "Read PRD.md and complete every unchecked task in Phase 2 in order.
Check off each task in PRD.md as you complete it.
After each task verify the acceptance criteria passes before moving on.
Frontend lives in ~/projects/home-scout/frontend/
FastAPI backend is server.py at project root — streams SSE events from CrewAI crew.
The live agent feed is the core UX — each step_callback event streams to the browser in real time.
Agent color coding: Brick=amber, Scholar=blue, Shield=red, Vibe=green, Gavel=purple, System=gray.
nginx.conf must have proxy_buffering off and chunked_transfer_encoding on for the /api/backend/ location.
nginx.conf must listen on port 8080. Dockerfile must EXPOSE 8080. Never port 80.
supervisord must pass GEMINI_API_KEY and TAVILY_API_KEY to the FastAPI process.
next.config.ts must expose BACKEND_URL to the Next.js standalone runtime.
Design: hs-forest (#1a3c34) primary, hs-cream (#f5f0e8) background, hs-amber (#d4a017) accent.
Serif display font (Playfair Display or Bitter). Calm, grounded, neighbourhood aesthetic.
Do not deploy to Railway — prepare Dockerfile and DEPLOY.md only.
When all Phase 2 tasks are complete output HOME_SCOUT_COMPLETE." \
--completion-promise "HOME_SCOUT_COMPLETE" \
--max-iterations 20
```

---

## Environment Variables Required

| Key | Where to get it |
|---|---|
| GEMINI_API_KEY | aistudio.google.com |
| TAVILY_API_KEY | app.tavily.com |

Census Bureau, Overpass, and Nominatim are all free — no keys, no billing.

---

## Success Definition

### Phase 1 complete when:
- python scout.py "location" runs end to end without errors
- All 5 agents visible in terminal with reasoning streamed
- Census tool returns demographic data for a test zip code
- Overpass tool returns POI counts for a test coordinate
- output/scorecard_*.md generated with all sections in the correct format
- server.py SSE endpoint streams events and terminates with done event + parsed scorecard
- parse_scorecard correctly extracts all score fields
- --dry-run runs Brick only and stops cleanly

### Phase 2 complete when:
- docker build completes without errors
- docker run -p 8080:8080 serves full app on localhost:8080
- Search → agent progress bar → live agent feed → scorecard flow works end to end
- SSE events reach browser without buffering — messages appear within 1-2 seconds per step
- Agent messages correctly color-coded in the feed
- Score badges and verdict callout color correctly
- Download button saves scorecard as .md file
- DEPLOY.md complete with Railway and DNS steps
