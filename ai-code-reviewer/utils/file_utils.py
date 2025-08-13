from __future__ import annotations


def is_probably_binary(raw: bytes) -> bool:
    if not raw:
        return False
    if b"\x00" in raw:
        return True
    text_chars = bytearray({7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)))
    nontext = raw.translate(None, text_chars)
    return float(len(nontext)) / max(1, len(raw)) > 0.30


