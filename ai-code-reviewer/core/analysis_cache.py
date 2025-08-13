from __future__ import annotations

import json
import os
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional


class AnalysisCache:
    """Simple file-based cache for analysis results keyed by file hash and type."""

    def __init__(self, cache_dir: str | Path = "cache") -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_file_hash(content: str) -> str:
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    def _cache_path(self, file_hash: str, analysis_type: str) -> Path:
        subdir = self.cache_dir / analysis_type
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / f"{file_hash}.json"

    def cache_result(self, file_hash: str, analysis_type: str, result: Dict[str, Any]) -> None:
        path = self._cache_path(file_hash, analysis_type)
        path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_cached_result(self, file_hash: str, analysis_type: str) -> Optional[Dict[str, Any]]:
        path = self._cache_path(file_hash, analysis_type)
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None


