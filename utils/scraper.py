import requests
from bs4 import BeautifulSoup
from exa_py import Exa
from config.settings import EXA_API_KEY

_exa = Exa(api_key=EXA_API_KEY)

SUMMARY_QUERY = (
    "What does this company do, who are their target clients, "
    "what industries do they serve, what is their value proposition, "
    "what services or products do they offer"
)


def scrape_website(url: str) -> str:
    """
    Primary: Exa get_contents with LLM summary.
    Fallback: requests + BeautifulSoup if Exa returns empty or throws.
    Returns clean plain text focused on positioning/services/clients.
    Raises ValueError if both methods fail.
    """
    if not url.startswith("http"):
        url = "https://" + url

    text = _scrape_with_exa(url)

    if len(text) < 200:
        text = _scrape_with_bs4(url)

    if len(text) < 100:
        raise ValueError(f"Could not extract content from: {url}")

    return text[:16000]


def _scrape_with_exa(url: str) -> str:
    try:
        results = _exa.get_contents(
            urls=[url],
            summary={"query": SUMMARY_QUERY},
            subpages=2,
            subpage_target=["about", "services"],
        )
        parts = []
        for item in results.results:
            if item.summary:
                parts.append(item.summary)
        return "\n\n".join(parts).strip()
    except Exception:
        return ""


def _scrape_with_bs4(url: str) -> str:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        base_url = url.rstrip("/")
        pages = [base_url, f"{base_url}/about", f"{base_url}/services"]
        parts = []
        for page_url in pages:
            try:
                resp = requests.get(page_url, headers=headers, timeout=10)
                if resp.status_code != 200:
                    continue
                soup = BeautifulSoup(resp.text, "html.parser")
                parts.append(_clean_html(soup))
            except Exception:
                continue
        return "\n\n".join(parts).strip()[:16000]
    except Exception:
        return ""


def _clean_html(soup: BeautifulSoup) -> str:
    for tag in soup(["nav", "footer", "header", "script", "style", "form"]):
        tag.decompose()
    tags = soup.find_all(["title", "h1", "h2", "h3", "p", "li"])
    texts = [t.get_text(separator=" ", strip=True) for t in tags if t.get_text(strip=True)]
    return " ".join(texts)
