# Signal-Based Opportunity Finder — PRD

For recruiting & staffing agency owners looking to generate more high-quality client conversations, build a micro-SaaS lead magnet (Streamlit) that analyzes their positioning, identifies high-intent hiring signals, and surfaces real companies currently in hiring mode — converting users into booked discovery calls.

---

## Users & Value

- **Primary user / persona:** Recruiting / staffing agency owners and BD leads, primarily US, solo to mid-sized agencies, decision-maker is founder / head of BD / lead recruiter

- **Jobs-to-be-done (JTBD):**
  - When I need new clients, I want to identify companies already in hiring mode, so I can increase conversion rate and reduce wasted outreach.
  - When evaluating lead generation approaches, I want to see real opportunities and signals, so I can trust the method and take action.

---

## Core Value Proposition

"Find companies already in hiring mode — before they hit job boards."

The tool shows recruiters:
- who to target
- when to reach out
- why timing matters

---

## Success Metrics

- **Primary Goal:** Booked discovery calls from cold outreach traffic
- **Success Criteria:** CTA click rate >= 15–25%, call booking rate >= 5–10%

---

## User Flow

### Step 1 — Landing (Input)

- Headline (signal-based hiring insight)
- Short pain statement (1–2 lines)
- URL input field
- CTA button (disabled until field filled)
- Optional: `?name=John&company=XYZ` prefill for personalization

### Step 2 — ICP Generation

Input: company website URL

System:
- Scrapes website
- LLM extracts positioning
- Generates 8–10 ICPs sorted by relevance (no numeric scoring)

ICP format:
- Role (e.g., Head of Talent, Founder)
- Company type (e.g., Series A/B, mid-size)
- Industry
- Geography (only if confident)

### Step 3 — ICP Selection

- User selects minimum 2, maximum 3 ICPs
- No editing in MVP
- Show live counter: "Selected: 2/3"

### Step 4 — Signal Generation (parallel per ICP)

- Separate LLM call per ICP
- LLM selects signals from signals library (no hallucination)
- Output: top 5 visible signals + additional under expand
- Each signal: name, explanation, how-to-find (on hover/tooltip)

### Step 5 — Live Opportunities (Exa layer)

- Only signals with `searchable: true` used
- Exa query formula: `[signal] + [industry] + [region] + [timeframe]`
- Output: 3–6 real companies total (2–3 per ICP max)
- Each company: name, signal detected, short explanation, optional source

### Step 6 — Action Block

- Who to target (specific roles, prioritized)
- Where to find (LinkedIn search patterns, job boards, signal sources)
- Outreach angle (1–2 short examples based on signal context)

### Step 7 — Insight Block

"You're missing this" section.

Format: current behavior vs better approach.

Example: "You're likely targeting general hiring needs, but the highest conversion comes from companies showing expansion and funding signals."

### Step 8 — CTA

Headline: "Turn these signals into consistent client conversations"

Body: "You can do this manually — but it means checking multiple sources and still missing timing. We monitor these signals continuously and connect you with companies already hiring."

CTA button: "Book a call"

---

## Scope

| Must-have (MVP) | Nice-to-have (Later) | Explicitly Out |
| --------------- | -------------------- | -------------- |
| ICP generation from URL | Hidden/expandable signals | Full CRM |
| ICP selection (2–3) | PDF report download | Contact scraping |
| Signal engine (per ICP, parallel) | Personal accounts | Automation UI |
| Exa company discovery | Advanced filtering | Multi-user system |
| Action block + Insight block | A/B tested prompts | Database / auth |
| CTA with booking link | PostHog analytics | Payment integration |

- **Definition of Done (MVP):**
  - [ ] User inputs website URL and gets ICP list
  - [ ] User selects 2–3 ICPs
  - [ ] Signals generated per ICP (parallel calls)
  - [ ] Exa returns real companies matched to signals
  - [ ] Full report renders cleanly (action + insight + CTA)
  - [ ] CTA present and functional
  - [ ] CLI mode works: `python main.py --url="..."`

---

## Tech Stack

- **Frontend:** Streamlit (MVP); architecture must support swap to Next.js
- **Backend:** Python
- **Database:** None (stateless, no persistence in MVP)
- **LLM:** Groq / OpenRouter
- **Web research:** Exa AI
- **Scraping:** requests + BeautifulSoup
- **Analytics:** PostHog (event-based, minimal setup)
- **Deployment:** Local / Streamlit Cloud (TBD)

---

## Architecture

### Principle

Clear separation between core logic and interface layer — Streamlit is only a presentation shell.

### Project Structure

```
project-root/
│
├── core/
│   ├── icp_engine.py
│   ├── signal_engine.py
│   ├── exa_engine.py
│   ├── signals_library.py
│   ├── orchestrator.py
│   └── models.py
│
├── core/prompts/
│   ├── icp_prompt.txt
│   ├── signal_prompt.txt
│   ├── exa_processing_prompt.txt
│   ├── action_prompt.txt
│   └── system_context.txt
│
├── ui/
│   └── streamlit_app.py
│
├── services/
│   ├── llm_client.py
│   └── exa_client.py
│
├── analytics/
│   └── tracking.py
│
├── utils/
│   ├── scraper.py
│   └── formatter.py
│
├── config/
│   └── settings.py
│
└── main.py
```

### Orchestrator Responsibilities (`orchestrator.py`)

- Manage full pipeline
- Coordinate: scraping → ICP generation → signal generation (parallel) → Exa queries → aggregation

Required functions:
```
run_full_analysis(input_data) -> report_json
generate_icp(context) -> icp_list
generate_signals(icp) -> signals
find_opportunities(icp, signals) -> companies
build_report(...) -> structured output
```

### Output Format (strict JSON)

```json
{
  "icp": [],
  "signals": [],
  "companies": [],
  "insight": "",
  "action_plan": [],
  "cta": ""
}
```

### Execution Modes

1. **CLI:** `python main.py --url="https://example.com"` → structured JSON output
2. **UI:** `streamlit run ui/streamlit_app.py` → Streamlit calls orchestrator functions only

---

## Prompts

All prompts live in `core/prompts/` as `.txt` files. Never inline prompts in code.

Reason: iterative improvement, A/B testing, niche scaling without touching logic.

---

## Signals Library

All signals live in `core/signals_library.py`. LLM selects from this library — no hallucination of new signals.

### Signal Schema

```python
{
  "name": "",
  "description": "",
  "category": "early | late | structural",
  "searchable": True | False,
  "sources": ["LinkedIn", "Crunchbase", "News", "Job Boards"]
}
```

### Signal Catalog

| # | Signal | Category | Searchable | Sources |
|---|--------|----------|------------|---------|
| 1 | Hiring Spike (5–20+ roles at once) | late | false | LinkedIn Jobs, Indeed |
| 2 | Long-Open Roles (30+ days) | late | false | LinkedIn Jobs, Indeed |
| 3 | Leadership Change (Head of Talent / VP Eng / Head of Sales hired) | structural | true | LinkedIn, news |
| 4 | Funding Event (Seed / Series A–C) | early | true | Crunchbase, news |
| 5 | Geographic / Operational Expansion | early | true | news, press releases |
| 6 | M&A (merger or acquisition) | structural | true | news |
| 7 | New Product / Business Unit Launch | early | true | company blog, news |
| 8 | Role-Specific Hiring Surge (10+ same function) | late | false | job boards |
| 9 | Career Page Expansion | late | false | company website |
| 10 | Public Hiring Announcements (CEO/HR posts) | late | true | LinkedIn |
| 11 | High Turnover Signals | structural | false | LinkedIn |
| 12 | Compliance / Regulatory Pressure (healthcare, finance) | structural | true | regulatory news |
| 13 | New Large Contract Signed | early | true | news |
| 14 | Tech Stack Change / Transformation | structural | true | engineering blogs, news |
| 15 | Layoffs → Rebuild Phase | structural | true | news |

---

## UI Design (Streamlit)

### Principle

One screen = one meaning. Flow, not dashboard.

### Screen Structure

**Screen 1 — Input**
- Headline (1 line)
- Pain statement (1–2 lines)
- URL field (autofocus, button disabled until filled)
- Optional: prefill from query params

**Screen 2 — ICP Selection**
- 8–10 cards (selectable)
- Card: bold role + company type, subtext: industry + geo
- Live counter: "Selected: 2/3", max 3

**Screen 3 — Processing**
- Step indicator with status:
  - "Analyzing your business"
  - "Identifying target companies"
  - "Finding live opportunities"
- Progress bar (fake acceptable)
- Text rotates every 2–3 seconds

**Screen 4 — Report**
1. Header: "Here's where your next clients are coming from"
2. ICP cards (3)
3. Signals — tabs per ICP, 5 signals each, hover = how to find
4. Live Opportunities — cards with: Company / Signal / Why it matters (most important visual block)
5. Action Block: Who / Where / Angle
6. Insight Block: highlighted/colored, "You're missing this" format
7. CTA: button + short copy

### Required UI Features

- `st.session_state` for step management and data persistence
- Step navigation: `step = "input" | "icp" | "report"`
- Skeleton loading (grey placeholders while processing)
- Error handling: "Couldn't analyze this site — try another URL"
- Reset button: "Start over"
- Copy button for outreach text

### UI Code Structure

```python
def render_input(): ...
def render_icp_selection(): ...
def render_loading(): ...
def render_report(): ...
```

### Mobile

- Max 1–2 columns
- Cards instead of tables always
- Use `st.container()` and `st.expander()`
- No complex grids

### Visual Style

- Theme: clean, minimal, white background
- One accent color
- Bold headings
- No charts for the sake of charts
- Report-style layout, not dashboard

### What NOT to build

- Filters
- Dropdowns for settings
- Multiple config options
- Heavy navigation

---

## Content

All UI copy lives in `core/prompts/` (system messages, output templates) and `config/settings.py` (labels, CTA text, step messages). No hardcoded strings in UI components.

---

## Key Constraints

1. No database in MVP — stateless execution only
2. No authentication
3. No fake data — Exa must return real companies or show nothing
4. Max total response time: ~20 seconds
5. Core must not depend on Streamlit — must support REST API wrapper and Next.js frontend without rewriting logic
6. No inline prompts — all prompts in `core/prompts/`

---

## Quality Bar

The product must NOT:
- Feel like generic GPT output
- Show hallucinated or fake companies
- Overload users with data or options
- Mix UI logic with core logic

The product MUST:
- Feel personalized to the agency's niche
- Show only real, sourced opportunities
- Deliver actionable insight within 60 seconds
- Create desire for a done-for-you solution
- Be structured so any component (UI, LLM, data source) can be swapped independently

---

## Positioning Summary

This is not a lead database. This is not a scraping tool.

This is a signal-driven opportunity engine for recruiting revenue.
