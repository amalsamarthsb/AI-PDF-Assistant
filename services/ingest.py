from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import VECTOR_DB_PATH, EMBEDDING_MODEL
from services.hybrid_retriever import initialize_bm25


def build_vector_database(pdf_paths):
    """
    Build a FAISS vector database from one or more PDFs.

    Args:
        pdf_paths (list[str]): List of PDF file paths.

    Returns:
        tuple:
            total_pages,
            total_chunks
    """

    all_documents = []

    # ---------------------------------------------------
    # Load PDFs
    # ---------------------------------------------------

    for pdf_path in pdf_paths:

        loader = PyPDFLoader(pdf_path)

        documents = loader.load()

        # Store original filename for citations
        filename = pdf_path.split("\\")[-1]

        for doc in documents:
            doc.metadata["source"] = filename

        all_documents.extend(documents)

    # ---------------------------------------------------
    # Split into chunks
    # ---------------------------------------------------

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )

    chunks = splitter.split_documents(all_documents)

    # ---------------------------------------------------
    # Initialize BM25
    # ---------------------------------------------------

    initialize_bm25(chunks)

    # ---------------------------------------------------
    # Create embeddings
    # ---------------------------------------------------

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    # ---------------------------------------------------
    # Create FAISS index
    # ---------------------------------------------------

    db = FAISS.from_documents(
        chunks,
        embeddings
    )

    db.save_local(VECTOR_DB_PATH)

    return len(all_documents), len(chunks)