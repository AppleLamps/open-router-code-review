from __future__ import annotations

from typing import Dict


class ReportGenerator:
    def generate_comprehensive_report(self, analysis_results: Dict[str, object]) -> Dict[str, object]:
        report = {
            "executive_summary": self.generate_executive_summary(analysis_results),
            "security_analysis": analysis_results.get("security", {}),
            "performance_analysis": analysis_results.get("performance", {}),
            "architecture_review": analysis_results.get("architecture", []),
            "recommendations": [],
            "action_items": [],
        }
        return report

    def generate_executive_summary(self, results: Dict[str, object]) -> str:
        security_count = sum(len(results.get("security", {}).get(k, [])) for k in ["critical", "high", "medium", "low", "info"])  # type: ignore[arg-type]
        perf_count = sum(len(results.get("performance", {}).get(k, [])) for k in ["high", "medium", "low"])  # type: ignore[arg-type]
        arch_count = len(results.get("architecture", []))  # type: ignore[arg-type]
        return (
            f"Codebase analyzed. Security issues: {security_count}. Performance issues: {perf_count}. "
            f"Architecture notes: {arch_count}."
        )


