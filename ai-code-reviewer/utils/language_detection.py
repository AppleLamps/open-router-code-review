from __future__ import annotations

import os
from typing import Optional


DEFAULT_EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".go": "go",
    ".rs": "rust",
    ".php": "php",
    ".rb": "ruby",
    ".cs": "csharp",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".html": "html",
    ".css": "css",
    ".sql": "sql",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".xml": "xml",
    ".sh": "bash",
}


def detect_language_by_path(path: str, ext_to_lang: Optional[dict] = None) -> Optional[str]:
    mapping = ext_to_lang or DEFAULT_EXT_TO_LANG
    base = os.path.basename(path)
    if base == "Dockerfile":
        return "docker"
    _, ext = os.path.splitext(base)
    return mapping.get(ext)


