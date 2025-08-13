import streamlit as st
from core.file_processor import FileProcessor
from core.code_analyzer import CodeAnalyzer
from utils.config import get_api_key
from core.openrouter_client import OpenRouterClient


def main() -> None:
    st.set_page_config(page_title="Ultimate AI Code Reviewer", page_icon="AI", layout="wide")

    st.title("Ultimate AI Code Reviewer")
    st.caption("Powered by OpenRouter & Grok-4")

    with st.sidebar:
        env_api_key = get_api_key() or ""
        api_key = st.text_input("OpenRouter API Key", type="password", value=env_api_key)
        analysis_depth = st.selectbox("Analysis Depth", ["Quick", "Standard", "Deep"], index=1)
        analysis_types = st.multiselect(
            "Analysis Types",
            ["Security", "Performance", "Architecture", "Style", "General"],
            default=["Security", "Performance", "Architecture"],
        )

    col1, col2 = st.columns([1, 1])

    upload_type = None
    uploaded_file = None
    github_url = None
    folder_path = None

    with col1:
        st.header("Upload Code")
        upload_type = st.radio("Upload Type", ["Zip File", "GitHub URL", "Folder"], index=0)

        if upload_type == "Zip File":
            uploaded_file = st.file_uploader("Choose ZIP file", type=["zip"])  # type: ignore[assignment]
        elif upload_type == "GitHub URL":
            github_url = st.text_input("GitHub Repository URL")
        else:
            folder_path = st.text_input("Local Folder Path")

    with col2:
        st.header("Analysis Settings")
        st.write(f"Depth: {analysis_depth}")
        st.write(f"Selected: {', '.join(analysis_types) if analysis_types else 'None'}")

    effective_api_key = api_key or env_api_key
    disabled = not effective_api_key or (upload_type == "Zip File" and uploaded_file is None)

    if st.button("Start Analysis", type="primary", disabled=disabled):
        analyze_codebase(upload_type, uploaded_file, github_url, folder_path, effective_api_key, analysis_types)


def analyze_codebase(upload_type, uploaded_file, github_url, folder_path, api_key, analysis_types):
    with st.spinner("Processing files..."):
        processor = FileProcessor()
        files = []
        if upload_type == "Zip File" and uploaded_file is not None:
            files = processor.extract_from_zip(uploaded_file)
        elif upload_type == "Folder" and folder_path:
            files = processor.extract_from_folder(folder_path)
        else:
            st.warning("GitHub URL and advanced sources are not implemented yet.")

    with st.spinner("Analyzing code..."):
        client = OpenRouterClient(api_key)
        analyzer = CodeAnalyzer(openrouter_client=client)
        results = analyzer.analyze_codebase(files, analysis_types)

    display_results(results)


def display_results(results):
    st.header("Executive Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        critical_high = len(results.get("security", {}).get("critical", [])) + len(results.get("security", {}).get("high", []))
        st.metric("Security Issues", critical_high)
    with col2:
        st.metric("Performance Issues", len(results.get("performance", {}).get("high", [])))
    with col3:
        st.metric("Code Quality Score", f"{results.get('overall_score', 0)}/100")
    with col4:
        st.metric("Files Analyzed", results.get("files_count", 0))

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Security", "Performance", "Architecture", "Style", "Summary"])

    with tab1:
        display_security_results(results.get("security", {}))
    with tab2:
        display_performance_results(results.get("performance", {}))
    with tab3:
        st.write("Architecture analysis will appear here.")
    with tab4:
        st.write("Style analysis will appear here.")
    with tab5:
        st.json({"files_summary": results.get("files_summary", [])})


def display_security_results(security_results):
    if not security_results:
        st.success("No security issues detected in this stub run.")
        return
    for severity in ["critical", "high", "medium", "low", "info"]:
        findings = security_results.get(severity, [])
        if findings:
            with st.expander(f"{severity.title()} ({len(findings)})"):
                for f in findings:
                    st.write(f)


def display_performance_results(perf_results):
    if not perf_results:
        st.info("No performance issues detected in this stub run.")
        return
    for level in ["high", "medium", "low"]:
        items = perf_results.get(level, [])
        if items:
            with st.expander(f"{level.title()} ({len(items)})"):
                for it in items:
                    st.write(it)


if __name__ == "__main__":
    main()


