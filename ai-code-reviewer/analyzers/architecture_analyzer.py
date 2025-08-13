from __future__ import annotations

import json
from typing import List, Dict, Any


class ArchitectureAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client

    def analyze_architecture(self, files_context: List[Dict[str, object]], project_structure: str) -> Dict[str, Any]:
        prompt = (
            "Analyze architecture: SOLID, patterns, separation of concerns, coupling/cohesion, testing, scalability. "
            "Return JSON with issues, recommendations, and priorities."
        )
        context_snippets = []
        for f in files_context[:5]:
            path = str(f.get("path"))
            content = str(f.get("content", ""))[:1200]
            context_snippets.append(f"--- {path} ---\n{content}")
        code_context = "\n\n".join(context_snippets)
        if self.client is None:
            return {"issues": [], "recommendations": []}
        raw = self.client.analyze_code(prompt, code_context, "architecture")
        try:
            data = json.loads(raw)
        except Exception:
            data = {"issues": [], "recommendations": []}
        return data if isinstance(data, dict) else {"issues": [], "recommendations": []}


