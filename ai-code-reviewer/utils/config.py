from __future__ import annotations

import os
from typing import Optional


def get_api_key() -> Optional[str]:
    return os.getenv("OPENROUTER_API_KEY")


