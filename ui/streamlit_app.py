import time
import streamlit as st

from core.orchestrator import generate_icp_only, run_full_analysis
from config.settings import (
    BOOKING_URL,
    MAX_ICPS_SELECTABLE,
    MIN_ICPS_SELECTABLE,
)

st.set_page_config(
    page_title="Signal Finder | System Hustle",
    page_icon="",
    layout="centered",
)

_LOADING_STEPS = [
    "Analyzing your business...",
    "Identifying your ideal client profiles...",
    "Matching hiring signals...",
    "Finding live opportunities...",
    "Building your action plan...",
]


def init_session_state():
    defaults = {
        "step": "input",
        "url": "",
        "name": "",
        "company": "",
        "icp_list": [],
        "selected_indices": [],
        "report": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def read_query_params():
    params = st.query_params
    if "url" in params and not st.session_state.url:
        st.session_state.url = params["url"]
    if "name" in params and not st.session_state.name:
        st.session_state.name = params["name"]
    if "company" in params and not st.session_state.company:
        st.session_state.company = params["company"]


def render_input():
    st.markdown("<br>", unsafe_allow_html=True)

    name = st.session_state.name
    if name:
        st.markdown(f"## Hey {name}, here's where your next clients are")
    else:
        st.markdown("## Find companies already in hiring mode")

    st.markdown(
        "Most recruiters wait for job postings. "
        "This tool identifies companies showing hiring signals **before** they hit job boards."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    url = st.text_input(
        "Your agency website URL",
        value=st.session_state.url,
        placeholder="https://youragency.com",
    )
    st.session_state.url = url

    st.markdown("<br>", unsafe_allow_html=True)

    btn_disabled = not url.strip()
    if st.button("Find Opportunities", disabled=btn_disabled, type="primary", use_container_width=True):
        with st.spinner("Analyzing your website..."):
            try:
                icps = generate_icp_only(url.strip())
                st.session_state.icp_list = icps
                st.session_state.step = "icp"
                st.rerun()
            except ValueError as e:
                st.error(f"Couldn't analyze this site — try another URL. ({e})")


def render_icp_selection():
    st.markdown("## Select the companies you serve best")
    st.markdown(f"Choose **{MIN_ICPS_SELECTABLE}–{MAX_ICPS_SELECTABLE}** profiles that best match your niche.")

    st.markdown("<br>", unsafe_allow_html=True)

    selected = list(st.session_state.selected_indices)
    icps = st.session_state.icp_list

    for i, icp in enumerate(icps):
        geo = f" · {icp.geography}" if icp.geography else ""
        label = f"**{icp.role}** at {icp.company_type}"
        subtext = f"{icp.industry}{geo}"
        checked = i in selected
        at_max = len(selected) >= MAX_ICPS_SELECTABLE and not checked
        new_val = st.checkbox(f"{label}  \n_{subtext}_", value=checked, key=f"icp_{i}", disabled=at_max)
        if new_val and i not in selected:
            selected.append(i)
        elif not new_val and i in selected:
            selected.remove(i)

    st.session_state.selected_indices = selected

    count = len(selected)
    st.markdown(f"**Selected: {count}/{MAX_ICPS_SELECTABLE}**")

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Back", use_container_width=True):
            st.session_state.step = "input"
            st.rerun()
    with col2:
        btn_disabled = count < MIN_ICPS_SELECTABLE
        if st.button("Find Opportunities", disabled=btn_disabled, type="primary", use_container_width=True):
            st.session_state.step = "loading"
            st.rerun()


def render_loading():
    st.markdown("## Analyzing your market...")
    st.markdown("<br>", unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_steps = len(_LOADING_STEPS)
    step_duration = 3

    def update_progress(step_index: int):
        progress = int((step_index + 1) / total_steps * 100)
        progress_bar.progress(progress)
        status_text.markdown(f"_{_LOADING_STEPS[step_index]}_")

    update_progress(0)

    import threading
    result_container = {"report": None, "error": None}

    def run_analysis():
        try:
            report = run_full_analysis(
                st.session_state.url,
                st.session_state.selected_indices,
            )
            result_container["report"] = report
        except Exception as e:
            result_container["error"] = str(e)

    thread = threading.Thread(target=run_analysis)
    thread.start()

    step = 1
    while thread.is_alive():
        time.sleep(step_duration)
        if step < total_steps - 1:
            update_progress(step)
            step += 1

    thread.join()
    update_progress(total_steps - 1)
    time.sleep(0.5)

    if result_container["error"]:
        st.error(f"Something went wrong: {result_container['error']}")
        if st.button("Try again"):
            st.session_state.step = "input"
            st.rerun()
        return

    st.session_state.report = result_container["report"]
    st.session_state.step = "report"
    st.rerun()


def render_report():
    report = st.session_state.report
    company_name = st.session_state.company

    heading = (
        f"Here's where **{company_name}'s** next clients are coming from"
        if company_name else
        "Here's where your next clients are coming from"
    )
    st.markdown(f"## {heading}")
    st.markdown("<br>", unsafe_allow_html=True)

    # ICP cards
    st.markdown("### Your Target Profiles")
    cols = st.columns(len(report.icp_signals))
    for col, ics in zip(cols, report.icp_signals):
        with col:
            geo = f"\n_{ics.icp.geography}_" if ics.icp.geography else ""
            st.info(f"**{ics.icp.role}**\n\n{ics.icp.company_type}\n\n_{ics.icp.industry}_{geo}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Signals per ICP
    st.markdown("### Hiring Signals to Watch")
    tab_labels = [ics.icp.role for ics in report.icp_signals]
    tabs = st.tabs(tab_labels)
    for tab, ics in zip(tabs, report.icp_signals):
        with tab:
            for signal in ics.signals:
                source_str = ", ".join(signal.sources)
                search_label = "Searchable via web" if signal.searchable else "Manual research"
                with st.expander(f"**{signal.name}** · _{signal.category}_"):
                    st.markdown(signal.description)
                    st.caption(f"How to find: {source_str} · {search_label}")
            if ics.hidden_signals:
                with st.expander(f"+ {len(ics.hidden_signals)} more signals"):
                    for signal in ics.hidden_signals:
                        source_str = ", ".join(signal.sources)
                        st.markdown(f"**{signal.name}** — {signal.description}")
                        st.caption(f"How to find: {source_str}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Live Opportunities
    st.markdown("### Live Opportunities Right Now")
    if report.companies:
        for company in report.companies:
            with st.container():
                col1, col2 = st.columns([2, 3])
                with col1:
                    st.markdown(f"**{company.name}**")
                    st.caption(f"Signal: {company.signal}")
                with col2:
                    st.markdown(company.explanation)
                    if company.source_url:
                        st.caption(f"[Source]({company.source_url})")
                st.divider()
    else:
        st.info("Live company search requires Groq API — run locally to see results.")

    st.markdown("<br>", unsafe_allow_html=True)

    # Action Block
    st.markdown("### Your Action Plan")
    action = report.action_plan
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Who to target**")
        for role in action.who_to_target:
            st.markdown(f"- {role}")
    with col2:
        st.markdown("**Where to find**")
        for source in action.where_to_find:
            st.markdown(f"- {source}")
    with col3:
        st.markdown("**Outreach angle**")
        for angle in action.outreach_angles:
            st.markdown(f"- {angle}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Insight Block
    if report.insight:
        st.markdown("### You're Missing This")
        st.info(report.insight)

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA
    st.markdown("---")
    st.markdown("### Turn these signals into consistent client conversations")
    st.markdown(
        "You can do this manually — but it means checking multiple sources daily "
        "and still missing the timing window. We monitor these signals continuously "
        "and connect you with companies already in hiring mode."
    )
    st.link_button("Book a Call", BOOKING_URL, type="primary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Start over", use_container_width=False):
        for key in ["step", "url", "name", "company", "icp_list", "selected_indices", "report"]:
            del st.session_state[key]
        st.rerun()


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
