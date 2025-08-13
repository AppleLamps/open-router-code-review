from __future__ import annotations

import json
from typing import Dict, Any


class StyleAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client

    def analyze_style_issues(self, code_content: str, file_path: str) -> Dict[str, Any]:
        prompt = (
            "Review code style and maintainability. Return JSON with issues list including SEVERITY, lines, description, and recommendation."
        )
        if self.client is None:
            return {"file": file_path, "issues": []}
        raw = self.client.analyze_code(prompt, code_content, "style")
        try:
            data = json.loads(raw)
        except Exception:
            data = {"issues": []}
        issues = data.get("issues") if isinstance(data, dict) else []
        if not isinstance(issues, list):
            issues = []
        return {"file": file_path, "issues": issues}


