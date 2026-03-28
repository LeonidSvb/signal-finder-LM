import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from core.models import ICP, ICPSignals
from core.signals_library import get_signal_by_name, signals_as_context_string
from services.llm_client import call_llm

_PROMPT_PATH = Path(__file__).parent / "prompts" / "signal_prompt.txt"


def generate_signals_for_icp(icp: ICP) -> ICPSignals:
    """
    Single LLM call for one ICP.
    Returns ICPSignals with signals split: first 5 visible, rest hidden.
    """
    system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")
    library_context = signals_as_context_string()
    full_system = f"{system_prompt}\n\n{library_context}"

    icp_description = (
        f"Role: {icp.role}\n"
        f"Company Type: {icp.company_type}\n"
        f"Industry: {icp.industry}\n"
        + (f"Geography: {icp.geography}\n" if icp.geography else "")
    )

    raw = call_llm(full_system, icp_description, temperature=0.2)
    raw = _strip_fences(raw)

    try:
        names = json.loads(raw)
    except json.JSONDecodeError:
        names = []

    signals = []
    for name in names:
        signal = get_signal_by_name(name)
        if signal:
            signals.append(signal)

    visible = signals[:5]
    hidden = signals[5:]

    return ICPSignals(icp=icp, signals=visible, hidden_signals=hidden)


def generate_signals_parallel(icps: list[ICP]) -> list[ICPSignals]:
    """
    Runs generate_signals_for_icp for each ICP in parallel.
    Returns list preserving input order.
    """
    results = [None] * len(icps)
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_index = {
            executor.submit(generate_signals_for_icp, icp): i
            for i, icp in enumerate(icps)
        }
        for future in as_completed(future_to_index):
            i = future_to_index[future]
            results[i] = future.result()
    return results


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
