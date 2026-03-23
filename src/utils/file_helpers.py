"""File and path helpers. IMPLEMENTATION_REFERENCE §1."""
from pathlib import Path


def ensure_dir(path: str | Path) -> Path:
    """Create directory (and parents) if it does not exist. Return path."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p
