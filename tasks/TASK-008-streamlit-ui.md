---
description: Streamlit UI — full 4-screen flow: input, ICP selection, loading, report
globs: ui/streamlit_app.py
alwaysApply: false
---

id: "TASK-008"
title: "Streamlit UI — 4-screen flow with session state"
status: "done"
priority: "P1"
labels: ["ui", "streamlit"]
dependencies: ["tasks/TASK-007-orchestrator.md"]
created: "2026-03-28"

# 1) High-Level Objective

Build the full Streamlit UI as a presentation layer only — all logic calls go through orchestrator. Four screens: input → ICP selection → loading → report. Must feel like a product, not a demo.

# 2) Background / Context

This is a lead magnet. The UI must create the feeling: "this is insight I'd pay for." Report must feel personalized, not generic. The CTA at the end books a call with Leo (cal.com/leonidshvorob/fit-check-call). URL supports `?url=`, `?name=`, `?company=` query params for personalized outreach links.

# 3) Assumptions & Constraints

- Constraint: UI is presentation only — no logic in streamlit_app.py except session state management
- Constraint: No hardcoded copy strings in UI file — all labels/text from config/settings.py
- Constraint: Must work on mobile (max 2 columns, cards not tables)
- Constraint: st.session_state manages all state between screens

# 4) Dependencies

- TASK-007 (orchestrator: generate_icp_only, run_full_analysis)
- TASK-001 (config/settings.py: BOOKING_URL, CONTACT_EMAIL, etc.)

# 5) Context Plan

**Beginning:**
- core/orchestrator.py _(read-only)_
- core/models.py _(read-only)_
- config/settings.py _(read-only)_

**End state:**
- ui/streamlit_app.py

# 6) Low-Level Steps

1. **Session state schema**

   - Initialize in app entry point:
     ```python
     defaults = {
         "step": "input",        # "input" | "icp" | "loading" | "report"
         "url": "",
         "name": "",             # from query param
         "company": "",          # from query param
         "icp_list": [],         # list[ICP] from generate_icp_only
         "selected_indices": [], # list[int]
         "report": None,         # Report dataclass
     }
     ```
   - Read query params on first load: `st.query_params` for `url`, `name`, `company`

2. **render_input()**

   - Personalized headline if `name` in session: "Hey {name}, here's where your next clients are"
   - Default headline: "Find companies already in hiring mode"
   - Pain statement: 1–2 lines (from config)
   - URL text input (pre-filled if `?url=` param present)
   - "Analyze" button — disabled if URL empty
   - On click: set `step = "icp"`, call `generate_icp_only(url)`, store in session

3. **render_icp_selection()**

   - Title: "Select the companies you serve best"
   - Render each ICP as a card using `st.checkbox` or custom HTML card
   - Card shows: bold role + company type, subtext: industry + geography
   - Live counter: "Selected: {n}/3"
   - Disable checkboxes beyond MAX_ICPS_SELECTABLE (3)
   - "Find Opportunities" button — disabled if fewer than MIN_ICPS_SELECTABLE (2) selected
   - On click: store selected_indices, set `step = "loading"`

4. **render_loading()**

   - Step indicator with 3 stages and rotating text:
     - Stage 1: "Analyzing your business"
     - Stage 2: "Identifying target companies"
     - Stage 3: "Finding live opportunities"
   - Progress bar (fake, increments over ~15 seconds)
   - Trigger `run_full_analysis(url, selected_indices)` → store in `report`
   - On completion: set `step = "report"`, rerun

5. **render_report()**

   Structure (top to bottom):
   - **Header**: "Here's where your next clients are coming from" (+ company name if available)
   - **ICP cards**: 3 cards in a row (or stacked mobile), each showing ICP role + company type
   - **Signals section**: tabs per ICP (`st.tabs`), inside each tab: 5 signals with expand for hidden ones. Each signal shows name + description. How-to-find in `st.expander` per signal.
   - **Live Opportunities**: cards (not table). Each card: Company name (bold), Signal detected, Why it matters. Source URL as small link if available.
   - **Action Block**: 3 columns — Who / Where / Angle. Plain bulleted text.
   - **Insight Block**: `st.info()` or custom styled container. "You're missing this:" + insight text.
   - **CTA**: headline + body copy (from config) + `st.link_button("Book a call", BOOKING_URL)`
   - **Reset**: small "Start over" button at bottom → clears session state, sets step = "input"

6. **App entry point**

   - File: `ui/streamlit_app.py`
   - Structure:
     ```python
     def main():
         init_session_state()
         read_query_params()
         step = st.session_state.step
         if step == "input":
             render_input()
         elif step == "icp":
             render_icp_selection()
         elif step == "loading":
             render_loading()
         elif step == "report":
             render_report()

     if __name__ == "__main__":
         main()
     ```

# 7) Types & Interfaces

N/A — UI only consumes Report, ICP, Signal, Company dataclasses from core/models.py

# 8) Acceptance Criteria

- `streamlit run ui/streamlit_app.py` launches without errors
- Full flow works: URL input → ICP selection (2–3) → loading screen → full report
- `?url=https://example.com&name=John` prefills URL and personalizes headline
- Report shows real company names from Exa (not placeholder text)
- "Book a call" button links to `cal.com/leonidshvorob/fit-check-call`
- "Start over" resets all state and returns to input screen

# 9) Testing Strategy

- Manual: run full flow with `https://systemhustle.com` — verify all sections render
- Manual: open with `?name=John&url=https://systemhustle.com` — verify personalization
- Manual: test on mobile viewport (375px) — verify no horizontal scroll, readable

# 10) Notes

- Use `st.rerun()` to transition between steps after state update
- For loading screen: run analysis in same thread (Streamlit doesn't support true background threads easily) — use st.spinner + progress bar visual
- Avoid st.experimental_rerun (deprecated) — use st.rerun()
