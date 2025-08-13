from core.file_processor import FileProcessor
from core.code_analyzer import CodeAnalyzer


def test_file_processor_initializes():
    fp = FileProcessor()
    assert ".py" in fp.supported_extensions


def test_code_analyzer_returns_structure():
    analyzer = CodeAnalyzer(openrouter_client=None)
    results = analyzer.analyze_codebase([])
    assert "overall_score" in results
    assert "files_count" in results


