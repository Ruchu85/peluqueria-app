"""
Phone number discovery module.

Strategy:
1. Return the phone already stored (from Google Places) if present.
2. Scrape tel: links from the business website — most reliable.
3. Regex scan for Spanish phone patterns in visible text.

Only reads publicly visible contact info the business has published.
"""
from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

# Spanish landlines (8xx, 9xx) and mobiles (6xx, 7xx) — 9 digits
_PHONE_PATTERN = re.compile(r"\b(?:\+34|0034)?[\s\-]?([6789]\d{2})[\s\-]?(\d{3})[\s\-]?(\d{3})\b")

_CONTACT_PAGE_PATHS = [
    "/contacto", "/contactar", "/contact", "/contact-us",
    "/sobre-nosotros", "/about",
]


def find_phone(website: str | None) -> str | None:
    """
    Try to find a public phone number for the business.
    Returns a normalized E.164 phone (+34xxxxxxxxx) or None.
    """
    if not website:
        return None
    return _scrape_website_phone(website)


def _scrape_website_phone(website: str) -> str | None:
    base = _get_base_url(website)
    urls_to_check = [website] + [urljoin(base, path) for path in _CONTACT_PAGE_PATHS[:3]]

    for url in urls_to_check:
        try:
            html = _fetch_html(url)
            phone = _extract_phone_from_html(html)
            if phone:
                return phone
        except Exception:
            continue

    return None


@retry(stop=stop_after_attempt(2), wait=wait_fixed(2))
def _fetch_html(url: str) -> str:
    with httpx.Client(
        timeout=10.0,
        follow_redirects=True,
        headers={"User-Agent": "Mozilla/5.0 (compatible; prospecting-bot/1.0)"},
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def _extract_phone_from_html(html: str) -> str | None:
    soup = BeautifulSoup(html, "html.parser")

    # tel: links are the most reliable source
    for a in soup.find_all("a", href=re.compile(r"^tel:", re.I)):
        raw = a["href"].replace("tel:", "").strip()
        normalized = _normalize_phone(raw)
        if normalized:
            return normalized

    # Regex scan over visible text as fallback
    text = soup.get_text(separator=" ")
    for match in _PHONE_PATTERN.finditer(text):
        digits = match.group(1) + match.group(2) + match.group(3)
        normalized = _normalize_phone(digits)
        if normalized:
            return normalized

    return None


def _normalize_phone(raw: str) -> str | None:
    """Strip spaces/dashes, validate 9 Spanish digits, return +34xxxxxxxxx."""
    digits = re.sub(r"[\s\-\.\(\)]", "", raw)
    # Remove leading +34 or 0034
    digits = re.sub(r"^(\+34|0034)", "", digits)
    if len(digits) == 9 and digits[0] in "6789":
        return f"+34{digits}"
    return None


def _get_base_url(url: str) -> str:
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"
