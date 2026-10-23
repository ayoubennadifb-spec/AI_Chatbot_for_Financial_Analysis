"""
NLP Entity Extractor
====================
Extracts company names and fiscal years from raw user queries
using regex patterns + fuzzy substring matching.
"""

import re
from data.financial_data import COMPANIES, YEARS

# Map lowercase aliases to canonical company names
_ALIASES = {
    'microsoft': 'Microsoft', 'msft': 'Microsoft', 'ms': 'Microsoft',
    'tesla':     'Tesla',     'tsla': 'Tesla',
    'apple':     'Apple',     'aapl': 'Apple',
}

_YEAR_PATTERN = re.compile(r'\b(202[123])\b')


def extract_company(query: str) -> str | None:
    """Return canonical company name found in query, or None."""
    q = query.lower()
    for alias, canonical in _ALIASES.items():
        if alias in q:
            return canonical
    return None


def extract_year(query: str) -> int | None:
    """Return fiscal year (int) mentioned in query, or None."""
    match = _YEAR_PATTERN.search(query)
    return int(match.group(1)) if match else None


def extract_entities(query: str) -> dict:
    """Return {'company': str|None, 'year': int|None}."""
    return {
        'company': extract_company(query),
        'year':    extract_year(query),
    }
