from __future__ import annotations

from typing import Dict


class SecurityAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client

    def analyze_security_vulnerabilities(self, code_content: str, file_path: str) -> str:
        prompt = (
            "Perform a comprehensive security analysis. Return JSON with severity, lines, description, remediation, and CWE."
        )
        if self.client is None:
            return "{}"
        return self.client.analyze_code(prompt, code_content, "security")


