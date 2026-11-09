"""
Text processing utilities for dark pattern detection.
Provides text normalization, sentence splitting, and keyword extraction.
"""

import re
from typing import Sequence


def normalize_text(text: str) -> str:
    """Lowercase, strip, and collapse whitespace in text."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def split_sentences(text: str) -> list[str]:
    """Split text into sentences, keeping non-empty ones."""
    # Split on sentence-ending punctuation followed by whitespace or end-of-string
    raw = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in raw if s.strip()]


def extract_price_values(text: str) -> list[float]:
    """Extract numeric price values from text (e.g., '$9.99', '€15')."""
    matches = re.findall(r"[\$€£¥]\s*(\d+(?:[.,]\d{1,2})?)", text)
    results: list[float] = []
    for m in matches:
        try:
            results.append(float(m.replace(",", ".")))
        except ValueError:
            continue
    return results


def text_contains_any(text: str, keywords: Sequence[str]) -> list[str]:
    """Return which keywords appear in the text (case-insensitive)."""
    lower = text.lower()
    return [kw for kw in keywords if kw.lower() in lower]


def text_matches_any_pattern(text: str, patterns: Sequence[str]) -> list[re.Match]:
    """Return regex match objects for patterns that match in text."""
    matches: list[re.Match] = []
    for pattern in patterns:
        found = re.search(pattern, text, re.IGNORECASE)
        if found:
            matches.append(found)
    return matches


def chunk_text(text: str, max_chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Split text into overlapping chunks for NLP processing."""
    if len(text) <= max_chunk_size:
        return [text] if text.strip() else []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + max_chunk_size, len(text))
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap if end < len(text) else end
    return chunks
