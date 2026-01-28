import re
from typing import List
from bs4 import BeautifulSoup


def strip_html(raw: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    if not raw:
        return ""
    text = BeautifulSoup(raw, "lxml").get_text(" ", strip=True)
    return collapse_spaces(text)


def collapse_spaces(text: str) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def sanitize_for_pipe(text: str) -> str:
    """Replace pipe characters that would break the delimiter."""
    if not text:
        return ""
    return text.replace("|", "/")


def clean_text(raw: str) -> str:
    return sanitize_for_pipe(collapse_spaces(raw))


def clean_list(items: List[str]) -> List[str]:
    if not items:
        return []
    return [clean_text(item) for item in items if item]
