"""
Streamlit demo: question input -> answer + sources. RAG_SYSTEM_DESIGN §8.
Run: streamlit run src/demo/streamlit_app.py
"""
import streamlit as st
from src.api.service import ask

st.set_page_config(page_title="RAG Document QA", layout="centered")
st.title("Document QA")
st.caption("Ask a question about the document collection. Answers are grounded in retrieved chunks.")

question = st.text_input("Question", placeholder="e.g. What is the cancellation policy?")
if st.button("Ask"):
    if not (question or "").strip():
        st.warning("Enter a question.")
    else:
        with st.spinner("Searching and generating answer..."):
            try:
                result = ask(question.strip())
                st.subheader("Answer")
                st.write(result["answer"])
                st.subheader("Sources")
                for s in result["sources"]:
                    st.write(f"- **{s['document']}** (page {s['page']}) — `{s['chunk_id']}`")
            except Exception as e:
                st.error(str(e))
