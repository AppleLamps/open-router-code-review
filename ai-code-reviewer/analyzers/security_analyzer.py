from __future__ import annotations

import json
from typing import Dict, Any, List


class SecurityAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client

    def analyze_security_vulnerabilities(self, code_content: str, file_path: str) -> Dict[str, Any]:
        prompt = (
            "Perform a comprehensive security analysis. Return JSON with severity, lines, description, remediation, and CWE."
        )
        if self.client is None:
            return {"findings": []}
        raw = self.client.analyze_code(prompt, code_content, "security")
        try:
            data = json.loads(raw)
        except Exception:
            data = {"findings": []}
        # Normalize output
        findings = data.get("findings") if isinstance(data, dict) else []
        if not isinstance(findings, list):
            findings = []
        return {"file": file_path, "findings": findings}


