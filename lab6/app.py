import os
from pathlib import Path
from typing import List

import pandas as pd
import requests
import streamlit as st

DATA_PATH = Path(__file__).parent / "data" / "labeled_esg_data.csv"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "deepseek-r1:1.5b")

st.set_page_config(page_title="ESG Translator & Analyst", layout="wide")

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Could not find dataset at {path}")
    return pd.read_csv(path, sep=";")


def call_ollama(prompt: str, *, system: str | None = None, timeout: int = 120) -> str:
    url = f"{OLLAMA_HOST.rstrip('/')}/api/generate"
    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}
    if system:
        payload["system"] = system
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Ollama request failed: {exc}") from exc
    data = response.json()
    if "error" in data:
        raise RuntimeError(f"Ollama error: {data['error']}")
    return data.get("response", "").strip()


def translate_text(text: str) -> str:
    cache = st.session_state.setdefault("translation_cache", {})
    if text in cache:
        return cache[text]
    prompt = (
        "Translate the following text into English. "
        "Return only the translation with no explanations.\n\n"
        f"Text: {text.strip()}"
    )
    translation = call_ollama(prompt)
    cache[text] = translation
    return translation


def translate_subset(df: pd.DataFrame) -> pd.DataFrame:
    subset = df.copy()
    total = len(subset)
    if total == 0:
        return subset
    
    # Get all columns to translate
    columns_to_translate = list(subset.columns)
    total_translations = total * len(columns_to_translate)
    
    progress = st.progress(0, text="Starting translation")
    status = st.empty()
    
    # Translate each column
    for col_idx, column in enumerate(columns_to_translate):
        translated_col_name = f"translated_{column}"
        translations: List[str] = []
        
        for row_idx, text in enumerate(subset[column], start=1):
            translation = translate_text(str(text))
            translations.append(translation)
            
            # Update progress across all columns
            current_progress = (col_idx * total + row_idx) / total_translations
            progress.progress(current_progress, text=f"Translating {column}: {row_idx}/{total}")
            status.caption(f"Latest translation ({column}): {translation[:80]}..." if len(translation) > 80 else f"Latest translation ({column}): {translation}")
        
        subset[translated_col_name] = translations
    
    progress.empty()
    status.empty()
    return subset


def summarize_translations(df: pd.DataFrame) -> str:
    rows = [
        f"Row {i + 1} | Label: {row.get('translated_label', row.get('label', 'N/A'))} | Quality: {row.get('translated_quality', row.get('quality', 'N/A'))} | Text: {row.get('translated_sentences', 'N/A')}"
        for i, row in df.iterrows()
    ]
    context = "\n".join(rows)
    prompt = (
        "You are an ESG analyst. Review the translated statements below and summarize the key "
        "themes you observe across Environmental, Social, and Governance dimensions. Highlight "
        "repeated commitments or issues, and mention any notable gaps. Provide the summary as "
        "2-3 short bullet lists grouped by ESG dimension.\n\n"
        f"Translated statements:\n{context}"
    )
    system = (
        "Stay focused on ESG insights from the provided statements. Do not invent facts and keep "
        "the tone analytical."
    )
    return call_ollama(prompt, system=system)


def answer_question(question: str, summary: str, df: pd.DataFrame) -> str:
    max_context = 120
    context_rows = df.head(max_context)
    context_lines = [
        f"Row {i + 1}: {row.get('translated_sentences', 'N/A')} (Label={row.get('translated_label', row.get('label', 'N/A'))}, Quality={row.get('translated_quality', row.get('quality', 'N/A'))})"
        for i, row in context_rows.iterrows()
    ]
    context_block = "\n".join(context_lines)
    prompt = (
        "Use the ESG summary and translated entries to answer the question. Cite row numbers "
        "when referencing specific statements.\n\n"
        f"ESG summary:\n{summary}\n\nTranslated entries:\n{context_block}\n\n"
        f"Question: {question}\n\nAnswer:" 
    )
    system = (
        "You are an ESG research assistant. Base your answer strictly on the provided summary and "
        "entries. If the information is unavailable, say so explicitly."
    )
    return call_ollama(prompt, system=system)


def main() -> None:
    st.title("ESG Data Translator and Analyst")
    st.write("Translate ESG statements to English, summarize them, and ask follow-up questions using DeepSeek via Ollama.")

    try:
        df = load_data(DATA_PATH)
    except Exception as exc:
        st.error(f"Failed to load data: {exc}")
        st.stop()

    total_rows = len(df)
    st.sidebar.header("Configuration")
    st.sidebar.caption(f"Dataset rows available: {total_rows}")
    n_rows = st.sidebar.slider(
        "Number of rows to translate", min_value=10, max_value=min(200, total_rows), value=50, step=5
    )
    st.sidebar.caption("Increase the limit for deeper context (slower).")
    run_analysis = st.sidebar.button("Translate & Analyze", use_container_width=True)

    if "translated_df" not in st.session_state:
        st.session_state.translated_df = None
    if "analysis_summary" not in st.session_state:
        st.session_state.analysis_summary = ""
    if "last_n_rows" not in st.session_state:
        st.session_state.last_n_rows = 0

    if run_analysis:
        subset = df.head(n_rows)
        with st.spinner("Translating entries with DeepSeek..."):
            try:
                translated = translate_subset(subset)
            except RuntimeError as exc:
                st.error(exc)
                st.stop()
        with st.spinner("Creating ESG summary..."):
            try:
                summary = summarize_translations(translated)
            except RuntimeError as exc:
                st.error(exc)
                st.stop()
        st.session_state.translated_df = translated
        st.session_state.analysis_summary = summary
        st.session_state.last_n_rows = n_rows

    translated_df = st.session_state.get("translated_df")
    summary = st.session_state.get("analysis_summary", "")

    if translated_df is not None:
        if st.session_state.last_n_rows != n_rows:
            st.info("The view below reflects the most recent run. Adjust rows and click 'Translate & Analyze' to refresh.")
        st.subheader("Translated Sample")
        st.dataframe(translated_df)

    if summary:
        st.subheader("LLM Summary")
        st.markdown(summary)

    st.subheader("Ask Questions")
    if translated_df is None or not summary:
        st.caption("Run the translation and summary first to enable Q&A.")
    question = st.text_area("Question", placeholder="e.g. What social initiatives stand out?", disabled=translated_df is None)
    ask = st.button("Ask DeepSeek", disabled=translated_df is None or not question.strip())
    if ask and question.strip():
        with st.spinner("Querying DeepSeek..."):
            try:
                answer = answer_question(question.strip(), summary, translated_df)
            except RuntimeError as exc:
                st.error(exc)
            else:
                st.markdown(answer)


if __name__ == "__main__":
    main()
