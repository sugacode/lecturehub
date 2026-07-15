import requests

CROSSREF_TIMEOUT_SECONDS = 8


class CrossRefLookupError(Exception):
    """Raised when a DOI can't be resolved via the CrossRef API."""


def fetch_doi_metadata(doi: str) -> dict:
    """Fetch and normalize metadata for a DOI from the public CrossRef API."""
    doi = doi.strip()
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=CROSSREF_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise CrossRefLookupError(f"Could not reach CrossRef for DOI '{doi}': {exc}") from exc

    message = response.json().get("message", {})

    authors = []
    for author in message.get("author", []):
        name = " ".join(filter(None, [author.get("given"), author.get("family")]))
        if name:
            authors.append(name)

    pub_type_map = {
        "journal-article": "journal_article",
        "proceedings-article": "conference_paper",
        "book": "book",
        "book-chapter": "book_chapter",
    }

    year = None
    for date_key in ("published-print", "published-online", "issued"):
        date_parts = message.get(date_key, {}).get("date-parts")
        if date_parts and date_parts[0]:
            year = date_parts[0][0]
            break

    return {
        "pub_type": pub_type_map.get(message.get("type"), "journal_article"),
        "title": (message.get("title") or [""])[0],
        "authors": ", ".join(authors),
        "venue": (message.get("container-title") or [""])[0],
        "year": year,
        "volume": message.get("volume", ""),
        "issue": message.get("issue", ""),
        "pages": message.get("page", ""),
        "doi": message.get("DOI", doi),
        "url": message.get("URL", ""),
        "citation_count": message.get("is-referenced-by-count", 0),
    }
