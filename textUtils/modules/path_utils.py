"""
path_utils.py
- Centralized helpers to resolve paths relative to textUtils and to fix
  GOOGLE_APPLICATION_CREDENTIALS when it is given as a relative path.
"""
from pathlib import Path
import os

# textUtils root directory (…/kannada-pdftoolkit/textUtils)
_TEXTUTILS_DIR = Path(__file__).resolve().parents[1]


def resolve_under_textutils(*parts) -> str:
    """Return absolute path under textUtils directory."""
    return str((_TEXTUTILS_DIR.joinpath(*parts)).resolve())


def resolve_service_account_from_env() -> str:
    """Return absolute path for GOOGLE_APPLICATION_CREDENTIALS.
    If env value is relative, resolve relative to textUtils/.
    Returns empty string if env is not set.
    """
    p = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if not p:
        return ""
    pth = Path(p)
    if not pth.is_absolute():
        pth = _TEXTUTILS_DIR.joinpath(p).resolve()
    return str(pth)