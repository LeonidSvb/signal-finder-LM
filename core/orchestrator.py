import json
import re
from pathlib import Path

from core.models import ICP, ActionPlan, Report
from core.icp_engine import generate_icp
from core.signal_engine import generate_signals_parallel
from core.exa_engine import find_all_opportunities
from services.llm_client import call_llm
from utils.scraper import scrape_website
from config.settings import BOOKING_URL

_ACTION_PROMPT_PATH = Path(__file__).parent / "prompts" / "action_prompt.txt"
_SYSTEM_CONTEXT_PATH = Path(__file__).parent / "prompts" / "system_context.txt"


def generate_icp_only(url: str) -> list[ICP]:
    """
    Step 1 of UI flow: scrape + generate ICPs only.
    Returns list of ICP dataclasses for user selection.
    """
    website_text = scrape_website(url)
    return generate_icp(website_text)


def run_full_analysis(url: str, selected_indices: list[int]) -> Report:
    """
    Full pipeline. selected_indices are indices into icp_list from generate_icp_only().
    Returns Report dataclass.
    """
    website_text = scrape_website(url)
    all_icps = generate_icp(website_text)
    selected_icps = [all_icps[i] for i in selected_indices if i < len(all_icps)]

    icp_signals = generate_signals_parallel(selected_icps)
    companies = find_all_opportunities(icp_signals)

    action_plan, insight = _generate_action_and_insight(selected_icps, icp_signals, companies)

    return Report(
        icp_list=all_icps,
        icp_signals=icp_signals,
        companies=companies,
        insight=insight,
        action_plan=action_plan,
        cta_url=BOOKING_URL,
    )


def _generate_action_and_insight(selected_icps, icp_signals, companies):
    system_context = _SYSTEM_CONTEXT_PATH.read_text(encoding="utf-8")
    action_prompt = _ACTION_PROMPT_PATH.read_text(encoding="utf-8")
    full_system = f"{system_context}\n\n{action_prompt}"

    icp_summary = "\n".join([
        f"- {icp.role} at {icp.company_type} ({icp.industry})"
        for icp in selected_icps
    ])

    signals_summary = "\n".join([
        f"- ICP '{ics.icp.role}': {', '.join(s.name for s in ics.signals)}"
        for ics in icp_signals
    ])

    companies_summary = "\n".join([
        f"- {c.name}: {c.signal} ({c.explanation})"
        for c in companies
    ]) or "No companies found yet."

    user_prompt = (
        f"ICPs:\n{icp_summary}\n\n"
        f"Signals per ICP:\n{signals_summary}\n\n"
        f"Live companies found:\n{companies_summary}"
    )

    raw = call_llm(full_system, user_prompt, temperature=0.4)
    raw = _strip_fences(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    action_plan = ActionPlan(
        who_to_target=data.get("who_to_target", []),
        where_to_find=data.get("where_to_find", []),
        outreach_angles=data.get("outreach_angles", []),
    )
    insight = data.get("insight", "")

    return action_plan, insight


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
