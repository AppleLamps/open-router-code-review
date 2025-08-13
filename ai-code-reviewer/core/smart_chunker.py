from __future__ import annotations

from typing import Dict, List


class SmartChunker:
    """Break large files into manageable chunks based on simple heuristics.

    For initial implementation, chunk by lines with soft boundaries around function-like markers.
    """

    def chunk_by_context(self, code_content: str, max_chars: int = 8000) -> List[str]:
        if len(code_content) <= max_chars:
            return [code_content]
        lines = code_content.splitlines()
        chunks: List[str] = []
        current: List[str] = []
        current_len = 0
        for line in lines:
            add_len = len(line) + 1
            if current_len + add_len > max_chars and current:
                chunks.append("\n".join(current))
                current = []
                current_len = 0
            current.append(line)
            current_len += add_len
        if current:
            chunks.append("\n".join(current))
        return chunks


