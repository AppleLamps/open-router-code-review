from __future__ import annotations

from pathlib import Path
from typing import Optional


TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates" / "prompts"


def load_prompt(template_name: str) -> Optional[str]:
    path = TEMPLATES_DIR / template_name
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


