from exa_py import Exa
from config.settings import EXA_API_KEY

_client = Exa(api_key=EXA_API_KEY)


def search(query: str, num_results: int = 5) -> list[dict]:
    """
    Runs neural search. Returns list of dicts with keys: title, url, text.
    Returns empty list on error.
    """
    try:
        results = _client.search_and_contents(
            query,
            num_results=num_results,
            text=True,
        )
        return [
            {"title": r.title or "", "url": r.url or "", "text": (r.text or "")[:2000]}
            for r in results.results
        ]
    except Exception:
        return []
