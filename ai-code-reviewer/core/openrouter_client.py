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
        self.model = "moonshotai/kimi-k2"

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
                "ROLE: You are a world-class application security engineer and code reviewer.\n"
                "OUTPUT: When the user prompt requests a structured result, return ONLY a single JSON object — no prose, no markdown, no code fences.\n"
                "SCOPE: Analyze only the provided code/context; avoid assumptions about external config or infrastructure.\n"
                "PRIORITIES: (1) correctness (low false positives), (2) actionable fixes, (3) clear evidence and exact lines.\n"
                "CHECKLIST: Input validation, authN/authZ, crypto, secret management, data protection, deserialization, SSRF/RCE, path traversal, injections (SQL/XSS/Command), insecure dependencies, misconfig, error handling and logging, insecure defaults.\n"
                "SCHEMA: {\"findings\": [{\"SEVERITY\": \"Critical|High|Medium|Low|Info\", \"LINE_NUMBER\": \"n or n-m or null\", \"VULNERABILITY_TYPE\": \"...\", \"DESCRIPTION\": \"...\", \"IMPACT\": \"...\", \"REMEDIATION\": \"...\", \"CWE_ID\": \"CWE-### or null\", \"CONFIDENCE\": \"High|Medium|Low\"}]}\n"
                "RULES: Cite exact evidence from the code. If uncertain about lines, set LINE_NUMBER=null and explain briefly. Prefer practical, least-invasive fixes with secure defaults. Reference OWASP Top 10/ASVS where relevant."
            )
        if analysis_type == "performance":
            return (
                "ROLE: You are a senior performance engineer.\n"
                "OUTPUT: If the user prompt asks for a structured result, return ONLY one JSON object.\n"
                "SCOPE: Focus on time/space complexity, I/O, database access, concurrency, caching, batching, and algorithmic choices.\n"
                "SCHEMA: {\"suggestions\": [{\"location\": {\"lines\": \"n or n-m or null\"}, \"issue\": \"...\", \"recommendation\": \"...\", \"impact\": \"high|medium|low\", \"snippet\": \"minimal code showing the change\"}]}\n"
                "RULES: Provide concrete, local changes with rationale. Use \"impact\" exactly as high|medium|low to indicate expected benefit. Avoid speculative system-wide assumptions."
            )
        if analysis_type == "architecture":
            return (
                "ROLE: You are an experienced software architect.\n"
                "OUTPUT: Prefer a structured JSON response when requested.\n"
                "FOCUS: Cohesion/coupling, layering and boundaries, domain modeling, error handling/observability, configuration/secrets, testing strategy, scalability and maintainability.\n"
                "SCHEMA: {\"issues\": [{\"category\": \"coupling|cohesion|boundary|config|error-handling|testing|scalability|other\", \"description\": \"...\", \"evidence\": \"...\", \"severity\": \"high|medium|low\"}], \"recommendations\": [{\"title\": \"...\", \"description\": \"...\", \"rationale\": \"...\", \"steps\": [\"step 1\", \"step 2\"], \"effort\": \"S|M|L\", \"impact\": \"high|medium|low\"}]}\n"
                "RULES: Propose incremental, low-risk refactors with clear steps, avoiding rewrites unless necessary."
            )
        if analysis_type == "style":
            return (
                "ROLE: You are a code quality reviewer focused on readability, maintainability, and idiomatic style.\n"
                "OUTPUT: Return ONLY JSON when requested.\n"
                "GUIDELINES: Naming, formatting, dead code, duplication, long functions, magic numbers, error handling, logging clarity, idiomatic patterns.\n"
                "SCHEMA: {\"issues\": [{\"SEVERITY\": \"High|Medium|Low|Info\", \"lines\": \"n or n-m or null\", \"description\": \"...\", \"recommendation\": \"...\", \"rule\": \"lint rule or pattern if applicable\"}]}\n"
                "RULES: Prefer small, mechanical edits with before/after snippets when impactful. Avoid subjective nits unless they improve clarity."
            )
        return (
            "ROLE: You are a senior software engineer performing a thorough general code review.\n"
            "OUTPUT: Match the requested format; if JSON is asked for, return ONLY JSON.\n"
            "FOCUS: Correctness, edge cases, error handling, tests, security/privacy, readability, and maintainability.\n"
            "RULES: Be concise, specific, and actionable with prioritized fixes."
        )


