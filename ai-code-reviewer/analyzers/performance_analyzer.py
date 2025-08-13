from __future__ import annotations

import json
from typing import Dict, Any


class PerformanceAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client

    def analyze_performance_issues(self, code_content: str, file_path: str) -> Dict[str, Any]:
        prompt = (
            "Analyze this code for performance issues. Return JSON with location, issue, recommendation, and estimated impact."
        )
        if self.client is None:
            return {"file": file_path, "suggestions": []}
        raw = self.client.analyze_code(prompt, code_content, "performance")
        try:
            data = json.loads(raw)
        except Exception:
            data = {"suggestions": []}
        suggestions = data.get("suggestions") if isinstance(data, dict) else []
        if not isinstance(suggestions, list):
            suggestions = []
        return {"file": file_path, "suggestions": suggestions}


