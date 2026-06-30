from services.logger import (initialize_logger, log_interaction)
import os
import time
import tempfile
import streamlit as st

from services.chat_history import (
    initialize_database,
    save_message,
    load_messages,
    clear_messages,
)

from services.ingest import build_vector_database
from services.hybrid_retriever import hybrid_retrieve
from services.llm import stream_llm


# ---------------------------------------------------
# Page Configuration
# ---------------------------------------------------

st.set_page_config(
    page_title="AI PDF Assistant Pro",
    page_icon="📄",
    layout="wide"
)

initialize_database()
initialize_logger()
# ---------------------------------------------------
# Session State
# ---------------------------------------------------
# NOTE: all session_state keys must be initialized BEFORE
# anything else in the script reads them, since Streamlit
# re-runs this file top-to-bottom on every interaction.

if "messages" not in st.session_state:
    st.session_state.messages = load_messages()

if "pdf_processed" not in st.session_state:
    st.session_state.pdf_processed = False

if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "documents": 0,
        "pages": 0,
        "chunks": 0,
        "questions": 0,
        "retrieved_chunks": 0,
        "last_response_time": 0,
        "average_response_time": 0
    }

if "retrieval_details" not in st.session_state:
    st.session_state.retrieval_details = []

if "sources" not in st.session_state:
    st.session_state.sources = []


# ---------------------------------------------------
# Top Status Banner
# ---------------------------------------------------

if st.session_state.pdf_processed:
    st.success("🟢 Vector Database Ready")
else:
    st.warning("🟡 Waiting for PDFs")

st.title("📄 AI PDF Assistant Pro")
st.caption("Powered by Gemini • LangChain • FAISS • HuggingFace")


# ---------------------------------------------------
# Sidebar
# ---------------------------------------------------

with st.sidebar:

    st.header("📚 AI PDF Assistant")

    st.markdown("""
### Features

✅ Multiple PDF Support

✅ Gemini 2.5 Flash

✅ FAISS Hybrid Search

✅ Streaming Responses

✅ Source Citations
""")

    st.divider()
    st.subheader("📊 RAG Evaluation")

    m = st.session_state.metrics

    st.metric("Documents", m["documents"])
    st.metric("Pages", m["pages"])
    st.metric("Chunks", m["chunks"])
    st.metric("Questions", m["questions"])
    st.metric("Retrieved Chunks", m["retrieved_chunks"])
    st.metric("Last Response", f'{m["last_response_time"]} sec')
    st.metric("Average Response", f'{m["average_response_time"]} sec')

    st.divider()
    if os.path.exists("logs/rag_logs.csv"):

     with open("logs/rag_logs.csv", "rb") as file:

        st.download_button(
            "📥 Download Logs",
            file,
            file_name="rag_logs.csv"
        )
    if st.button("🗑️ Clear Chat"):
        clear_messages()
        st.session_state.messages = []
        st.rerun()

    with st.expander("🔍 Retrieval Inspector"):

        # Reads the most recently retrieved chunks, persisted in
        # session_state from the last question that was asked.
        # The sidebar renders before the chat input each run, so
        # we can't reference this-run's `docs`/`question` here.
        if st.session_state.retrieval_details:
            for i, item in enumerate(st.session_state.retrieval_details, start=1):
                st.markdown(f"### Chunk {i}")
                st.write(f"📄 File: {item['source']}")
                st.write(f"📑 Page: {item['page']}")
                st.code(item["preview"])
        else:
            st.caption("Ask a question to see retrieved chunks here.")


# ---------------------------------------------------
# Upload PDFs
# ---------------------------------------------------

uploaded_files = st.file_uploader(
    "Upload PDF(s)",
    type=["pdf"],
    accept_multiple_files=True,
)

if uploaded_files:

    st.success(f"{len(uploaded_files)} PDF(s) selected")

    if st.button("📄 Process PDFs"):

        temp_paths = []

        try:
            for uploaded_file in uploaded_files:
                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=".pdf"
                ) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    temp_paths.append(tmp.name)

            with st.spinner("Creating Vector Database..."):
                total_pages, total_chunks = build_vector_database(temp_paths)
                st.session_state.metrics["documents"] = len(uploaded_files)
                st.session_state.metrics["pages"] = total_pages
                st.session_state.metrics["chunks"] = total_chunks

            st.session_state.pdf_processed = True

            st.success("✅ PDFs processed successfully!")

            st.info(
                f"""
📄 Documents : {len(uploaded_files)}

📑 Pages : {total_pages}

🧩 Chunks : {total_chunks}
"""
            )

        except Exception as e:
            st.error(str(e))

        finally:
            for path in temp_paths:
                if os.path.exists(path):
                    os.remove(path)


# ---------------------------------------------------
# Display Chat History
# ---------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ---------------------------------------------------
# Chat Input
# ---------------------------------------------------

question = st.chat_input(
    "Ask a question about your documents..."
)

if question:

    if not st.session_state.pdf_processed:
        st.warning("Please upload and process your PDF(s) first.")
        st.stop()

    # ---------------- User ----------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    save_message("user", question)

    with st.chat_message("user"):
        st.markdown(question)

    # ---------------- Retrieval ----------------

    with st.spinner("Searching documents..."):
        docs = hybrid_retrieve(question)

    context = "\n\n".join(
        doc.page_content
        for doc in docs
    )

    # Build retrieval details + source citations from `docs`
    # before generation, so both are ready the moment streaming ends.

    retrieval_details = []
    sources = []

    for doc in docs:
        source = os.path.basename(
            doc.metadata.get("source", "Unknown")
        )
        page = doc.metadata.get("page", 0) + 1

        retrieval_details.append({
            "source": source,
            "page": page,
            "preview": doc.page_content[:150]
        })

        citation = f"{source} (Page {page})"
        if citation not in sources:
            sources.append(citation)

    # Persist for the sidebar's Retrieval Inspector, which is
    # rendered at the top of the script on the *next* run.
    st.session_state.retrieval_details = retrieval_details
    st.session_state.sources = sources

    # ---------------- Assistant ----------------

    with st.chat_message("assistant"):

        placeholder = st.empty()
        full_response = ""

        start_time = time.time()

        # Stream Gemini response
        for chunk in stream_llm(question, context):
            if hasattr(chunk, "content") and chunk.content:
                full_response += chunk.content
                placeholder.markdown(full_response + "▌")

        elapsed = round(time.time() - start_time, 2)

        # Append source citations before the final render, so they
        # show up immediately in this run instead of after a rerun.
        if sources:
            full_response += "\n\n---\n"
            full_response += "### 📚 Sources\n\n"
            for source in sources:
                full_response += f"- {source}\n"

        # Remove cursor, show final response (with sources)
        placeholder.markdown(full_response)

        # ---------------- Metrics ----------------

        st.session_state.metrics["questions"] += 1
        st.session_state.metrics["retrieved_chunks"] = len(docs)
        st.session_state.metrics["last_response_time"] = elapsed

        q = st.session_state.metrics["questions"]
        old_avg = st.session_state.metrics["average_response_time"]
        new_avg = ((old_avg * (q - 1)) + elapsed) / q
        st.session_state.metrics["average_response_time"] = round(new_avg, 2)

    # ---------------- Save Chat ----------------

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response
        }
    )

    save_message("assistant", full_response)
    log_interaction(
    question=question,
    answer=full_response,
    retrieved_chunks=len(docs),
    sources=sources,
    response_time=elapsed
)