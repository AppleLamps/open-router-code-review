from __future__ import annotations

from typing import Dict, List, Optional


class CodeAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client
        self.max_tokens_per_request: int = 16000

    def analyze_codebase(self, files: List[Dict[str, object]]) -> Dict[str, object]:
        results: Dict[str, object] = {
            "security": {"critical": [], "high": [], "medium": [], "low": [], "info": []},
            "performance": {"high": [], "medium": [], "low": []},
            "architecture": [],
            "style": [],
            "general": [],
            "files_count": len(files),
            "overall_score": 100,
            "files_summary": [
                {"path": f.get("path"), "language": f.get("language"), "size": f.get("size")} for f in files
            ],
        }
        return results

    def prioritize_files(self, files: List[Dict[str, object]]) -> List[Dict[str, object]]:
        priority_order = ["main", "index", "app", "server", "config", "auth", "security", "database", "api"]

        def score(file_item: Dict[str, object]) -> int:
            name = str(file_item.get("name", "")).lower()
            for i, key in enumerate(priority_order):
                if key in name:
                    return len(priority_order) - i
            return 0

        return sorted(files, key=score, reverse=True)


