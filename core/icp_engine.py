import json
import re
from pathlib import Path

from core.models import ICP
from services.llm_client import call_llm

_PROMPT_PATH = Path(__file__).parent / "prompts" / "icp_prompt.txt"


def generate_icp(website_text: str) -> list[ICP]:
    """
    Calls LLM with icp_prompt.txt + website_text.
    Parses JSON response into list of ICP dataclasses.
    Raises ValueError if JSON parse fails or result is empty.
    """
    system_prompt = _PROMPT_PATH.read_text(encoding="utf-8")
    raw = call_llm(system_prompt, website_text, temperature=0.3)
    raw = _strip_fences(raw)

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"ICP engine: failed to parse LLM response as JSON: {e}\nRaw: {raw[:300]}")

    if not isinstance(data, list) or len(data) < 4:
        raise ValueError(f"ICP engine: expected list of 8-10 items, got: {len(data) if isinstance(data, list) else type(data)}")

    icps = []
    for item in data:
        if not isinstance(item, dict):
            continue
        if not item.get("role") or not item.get("company_type") or not item.get("industry"):
            continue
        icps.append(ICP(
            role=item["role"],
            company_type=item["company_type"],
            industry=item["industry"],
            geography=item.get("geography"),
        ))

    return icps


def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
