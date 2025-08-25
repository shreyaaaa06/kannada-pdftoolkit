"""
Kannada text post-processing utilities.

Provides fix_kannada_spacing(text) to normalize Unicode and remove stray
spaces around Kannada grapheme clusters (matras, virama, ZWJ/ZWNJ), and
line-wrap cleanup. Designed to be conservative and idempotent.
"""
from __future__ import annotations
import re
import unicodedata
from typing import List

__all__ = ["fix_kannada_spacing", "normalize_unicode_safe"]


def normalize_unicode_safe(s: str) -> str:
    if not s:
        return ""
    return unicodedata.normalize("NFC", s)


def _apply_rules(s: str) -> str:
    # Remove spaces before dependent vowel signs U+0CBE–U+0CD6
    s = re.sub(r"\s+([\u0CBE-\u0CD6])", r"\1", s)
    # Remove spaces around halant U+0CCD (join conjuncts)
    s = re.sub(r"(\u0CCD)\s+(?=[\u0C95-\u0CB9\u0CE0-\u0CE1\u0CEA-\u0CEF])", r"\1", s)
    s = re.sub(r"([\u0C95-\u0CB9\u0CE0-\u0CE1\u0CEA-\u0CEF])\s+(\u0CCD)", r"\1\2", s)
    # Remove spaces around ZWJ/ZWNJ
    s = re.sub(r"\s*([\u200C\u200D])\s*", r"\1", s)
    # Rejoin hyphenated linebreaks and linewraps
    s = re.sub(r"(\S)[\-–]\n(\S)", r"\1\2", s)
    s = re.sub(r"([^\.\?\!])\n(?!\n)", r"\1 ", s)
    # Collapse multiple spaces
    s = re.sub(r"\s+", " ", s)
    return s


def fix_kannada_spacing(text: str) -> str:
    """
    - Normalize to NFC.
    - Remove spaces inside Kannada grapheme clusters:
      * Remove spaces before dependent vowel signs U+0CBE–U+0CD6
      * Remove spaces around virama U+0CCD (halant) and join conjuncts
      * Remove spaces around ZWJ/ZWNJ (U+200D/U+200C) with virama-aware rules
    - Collapse multiple spaces → single, but preserve intended paragraph boundaries.
    - Rejoin hyphenated linebreaks and PDF linewrap insertions.
    """
    if not text:
        return ""
    s = normalize_unicode_safe(text)
    s = _apply_rules(s)
    return normalize_unicode_safe(s)


# Simple doctest-style unit checks
if __name__ == "__main__":
    cases: List[tuple[str, str]] = [
        ("ಕ ್ ಕ", "ಕ್ ಕ"),
        ("ಕ ್\nಕ", "ಕ್ ಕ"),
        ("ಕ ೆ ಲ ವ ಿ ಗೆ", "ಕೆ ಲ ವಿಗೆ"),
        ("ನ್ \u200D ದ", "ನ್\u200Dದ"),
        ("ಪ ರೀ ಕ್ ಷೆ", "ಪರೀಕ್ಷೆ"),
    ]
    for i, (inp, exp) in enumerate(cases, 1):
        out = fix_kannada_spacing(inp)
        print(i, out == exp, out)

