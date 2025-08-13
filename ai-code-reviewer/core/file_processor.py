from __future__ import annotations

import io
import os
import zipfile
from typing import Dict, List, Optional


class FileProcessor:
    def __init__(self) -> None:
        self.supported_extensions: Dict[str, str] = {
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
            ".dockerfile": "docker",
        }

        self.ignore_dirs = {"node_modules", ".git", ".hg", ".svn", "__pycache__", "venv", ".venv", "dist", "build"}
        self.max_file_bytes: int = 1_500_000

    def extract_from_zip(self, zip_file) -> List[Dict[str, object]]:
        """Extract and categorize files from a ZIP upload (Streamlit UploadedFile or bytes)."""
        if zip_file is None:
            return []

        data: bytes
        if hasattr(zip_file, "read"):
            data = zip_file.read()  # Streamlit UploadedFile
        elif hasattr(zip_file, "getvalue"):
            data = zip_file.getvalue()
        elif isinstance(zip_file, (bytes, bytearray)):
            data = bytes(zip_file)
        else:
            raise TypeError("Unsupported zip_file type")

        files: List[Dict[str, object]] = []
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                path = info.filename
                if self._should_ignore_path(path):
                    continue
                try:
                    raw = zf.read(info)
                except Exception:
                    continue
                if len(raw) > self.max_file_bytes:
                    continue
                if self._is_probably_binary(raw):
                    continue
                language = self._detect_language_by_name(path)
                if language is None:
                    continue
                try:
                    text = raw.decode("utf-8", errors="ignore")
                except Exception:
                    continue
                files.append(
                    {
                        "name": os.path.basename(path),
                        "path": path,
                        "content": text,
                        "language": language,
                        "size": len(raw),
                    }
                )
        return files

    def extract_from_folder(self, folder_path: str) -> List[Dict[str, object]]:
        """Process a local folder and extract supported files."""
        if not folder_path or not os.path.isdir(folder_path):
            return []
        results: List[Dict[str, object]] = []
        for root, dirs, files in os.walk(folder_path):
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            for fname in files:
                full = os.path.join(root, fname)
                if self._should_ignore_path(full):
                    continue
                try:
                    size = os.path.getsize(full)
                except OSError:
                    continue
                if size > self.max_file_bytes:
                    continue
                language = self._detect_language_by_name(full)
                if language is None:
                    continue
                try:
                    with open(full, "rb") as f:
                        raw = f.read()
                except OSError:
                    continue
                if self._is_probably_binary(raw):
                    continue
                text = raw.decode("utf-8", errors="ignore")
                rel_path = os.path.relpath(full, folder_path)
                results.append(
                    {
                        "name": fname,
                        "path": rel_path,
                        "content": text,
                        "language": language,
                        "size": size,
                    }
                )
        return results

    def detect_project_type(self, files: List[Dict[str, object]]) -> str:
        names = {str(f.get("path", "")).lower() for f in files}
        if any("package.json" in n for n in names):
            return "nodejs"
        if any("requirements.txt" in n or "pyproject.toml" in n for n in names):
            return "python"
        if any("pom.xml" in n or "build.gradle" in n for n in names):
            return "java"
        if any("go.mod" in n for n in names):
            return "go"
        return "unknown"

    def create_file_tree(self, files: List[Dict[str, object]]) -> str:
        paths = sorted(str(f.get("path", "")) for f in files)
        return "\n".join(paths)

    def _detect_language_by_name(self, path: str) -> Optional[str]:
        base = os.path.basename(path)
        if base == "Dockerfile":
            return "docker"
        _, ext = os.path.splitext(base)
        return self.supported_extensions.get(ext)

    def _should_ignore_path(self, path: str) -> bool:
        parts = path.split("/")
        return any(p in self.ignore_dirs for p in parts)

    def _is_probably_binary(self, raw: bytes) -> bool:
        if not raw:
            return False
        # Heuristic: presence of NUL bytes or high non-text ratio
        if b"\x00" in raw:
            return True
        text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
        nontext = raw.translate(None, text_chars)
        return float(len(nontext)) / max(1, len(raw)) > 0.30


