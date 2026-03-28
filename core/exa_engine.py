import json
import re
from pathlib import Path

from core.models import Company, ICPSignals
from services.exa_client import search
from services.llm_client import call_llm
from config.settings import MAX_COMPANIES_PER_ICP, MAX_COMPANIES_TOTAL

_PROMPT_PATH = Path(__file__).parent / "prompts" / "exa_processing_prompt.txt"


def find_companies_for_icp(icp_signals: ICPSignals) -> list[Company]:
    """
    Runs Exa queries for searchable signals of one ICP.
    Returns up to MAX_COMPANIES_PER_ICP companies.
    """
    system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")
    icp = icp_signals.icp
    all_signals = icp_signals.signals + icp_signals.hidden_signals
    searchable = [s for s in all_signals if s.searchable]

    companies: list[Company] = []

    for signal in searchable:
        if len(companies) >= MAX_COMPANIES_PER_ICP:
            break

        region = icp.geography or "USA"
        query = f"{signal.name} {icp.industry} {region} last 30 days"
        results = search(query, num_results=5)

        if not results:
            continue

        results_text = "\n\n".join([
            f"Title: {r['title']}\nURL: {r['url']}\nText: {r['text'][:500]}"
            for r in results
        ])

        user_prompt = (
            f"ICP: {icp.role} at {icp.company_type} in {icp.industry}\n"
            f"Signal: {signal.name} — {signal.description}\n\n"
            f"Search Results:\n{results_text}"
        )

        raw = call_llm(system_prompt, user_prompt, temperature=0.1)
        raw = _strip_fences(raw)

        try:
            items = json.loads(raw)
        except json.JSONDecodeError:
            continue

        for item in items:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            companies.append(Company(
                name=item["name"],
                signal=item.get("signal", signal.name),
                explanation=item.get("explanation", ""),
                source_url=item.get("source_url", ""),
                icp_ref=icp.role,
            ))
            if len(companies) >= MAX_COMPANIES_PER_ICP:
                break

    return companies


def find_all_opportunities(icp_signals_list: list[ICPSignals]) -> list[Company]:
    """
    Runs find_companies_for_icp for each ICP sequentially.
    Returns deduplicated list capped at MAX_COMPANIES_TOTAL.
    """
    all_companies: list[Company] = []
    seen_names: set[str] = set()

    for icp_signals in icp_signals_list:
        companies = find_companies_for_icp(icp_signals)
        for company in companies:
            name_key = company.name.lower().strip()
            if name_key not in seen_names:
                seen_names.add(name_key)
                all_companies.append(company)
            if len(all_companies) >= MAX_COMPANIES_TOTAL:
                break
        if len(all_companies) >= MAX_COMPANIES_TOTAL:
            break

    return all_companies


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
