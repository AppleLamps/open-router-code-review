from __future__ import annotations

from typing import Dict, List, Optional, Any

from analyzers.security_analyzer import SecurityAnalyzer
from analyzers.performance_analyzer import PerformanceAnalyzer
from analyzers.architecture_analyzer import ArchitectureAnalyzer
from .smart_chunker import SmartChunker
from .analysis_cache import AnalysisCache


class CodeAnalyzer:
    def __init__(self, openrouter_client) -> None:  # type: ignore[no-untyped-def]
        self.client = openrouter_client
        self.max_tokens_per_request: int = 16000
        self.security_analyzer = SecurityAnalyzer(openrouter_client)
        self.performance_analyzer = PerformanceAnalyzer(openrouter_client)
        self.architecture_analyzer = ArchitectureAnalyzer(openrouter_client)
        self.chunker = SmartChunker()
        self.cache = AnalysisCache()

    def analyze_codebase(self, files: List[Dict[str, object]]) -> Dict[str, object]:
        results: Dict[str, Any] = {
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

        prioritized = self.prioritize_files(files)
        for file_info in prioritized:
            path = str(file_info.get("path"))
            content = str(file_info.get("content", ""))
            file_hash = self.cache.get_file_hash(content)

            # Security
            cached_sec = self.cache.get_cached_result(file_hash, "security")
            if cached_sec is None:
                sec_findings = self._analyze_security_with_chunking(content, path)
                self.cache.cache_result(file_hash, "security", sec_findings)
            else:
                sec_findings = cached_sec
            self._merge_security_results(results["security"], sec_findings)

            # Performance
            cached_perf = self.cache.get_cached_result(file_hash, "performance")
            if cached_perf is None:
                perf_suggestions = self._analyze_performance_with_chunking(content, path)
                self.cache.cache_result(file_hash, "performance", perf_suggestions)
            else:
                perf_suggestions = cached_perf
            self._merge_performance_results(results["performance"], perf_suggestions)

        # Architecture (cross-file)
        arch = self.architecture_analyzer.analyze_architecture(files, self._build_project_structure(files))
        results["architecture"] = arch

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

    def _analyze_security_with_chunking(self, content: str, path: str) -> Dict[str, Any]:
        chunks = self.chunker.chunk_by_context(content)
        all_findings: List[Dict[str, Any]] = []
        for chunk in chunks:
            res = self.security_analyzer.analyze_security_vulnerabilities(chunk, path)
            all_findings.extend(res.get("findings", []))
        return {"file": path, "findings": all_findings}

    def _analyze_performance_with_chunking(self, content: str, path: str) -> Dict[str, Any]:
        chunks = self.chunker.chunk_by_context(content)
        all_suggestions: List[Dict[str, Any]] = []
        for chunk in chunks:
            res = self.performance_analyzer.analyze_performance_issues(chunk, path)
            all_suggestions.extend(res.get("suggestions", []))
        return {"file": path, "suggestions": all_suggestions}

    def _merge_security_results(self, dest: Dict[str, List[Dict[str, Any]]], sec_result: Dict[str, Any]) -> None:
        for finding in sec_result.get("findings", []):
            severity = str(finding.get("SEVERITY", "info")).lower()
            if severity not in dest:
                severity = "info"
            dest[severity].append(finding)

    def _merge_performance_results(self, dest: Dict[str, List[Dict[str, Any]]], perf_result: Dict[str, Any]) -> None:
        for suggestion in perf_result.get("suggestions", []):
            impact = str(suggestion.get("impact", "low")).lower()
            if impact not in dest:
                impact = "low"
            dest[impact].append(suggestion)

    def _build_project_structure(self, files: List[Dict[str, object]]) -> str:
        paths = [str(f.get("path")) for f in files]
        return "\n".join(sorted(paths))


