from __future__ import annotations

from typing import Optional

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency for scaffolding
    OpenAI = None  # type: ignore[assignment]


class OpenRouterClient:
    def __init__(self, api_key: str) -> None:
        if OpenAI is None:
            raise ImportError(
                "openai package is required. Please install dependencies: `pip install -r ai-code-reviewer/requirements.txt`"
            )
        self.client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
        self.model = "x-ai/grok-4"

    def analyze_code(self, prompt: str, code_content: str, analysis_type: str = "general") -> str:
        response = self.client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://your-app-url.com",
                "X-Title": "Ultimate AI Code Reviewer",
            },
            model=self.model,
            messages=[
                {"role": "system", "content": self.get_system_prompt(analysis_type)},
                {"role": "user", "content": f"Analyze this code:\n\n```\n{code_content}\n```\n\n{prompt}"},
            ],
            temperature=0.1,
            max_tokens=4000,
        )
        return response.choices[0].message.content or ""

    def get_system_prompt(self, analysis_type: str) -> str:
        if analysis_type == "security":
            return (
                "You are a world-class security reviewer. Identify vulnerabilities with clear severity, exact lines, and fixes."
            )
        if analysis_type == "performance":
            return "You are a performance expert. Find bottlenecks and propose concrete optimizations with estimates."
        if analysis_type == "architecture":
            return "You are an experienced software architect. Evaluate design, coupling, cohesion, and maintainability."
        if analysis_type == "style":
            return "You are a code quality reviewer. Enforce style, naming, formatting, and idiomatic patterns."
        return "You are a senior software engineer performing a thorough general code review."


