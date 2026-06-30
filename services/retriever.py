from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from config import VECTOR_DB_PATH, EMBEDDING_MODEL, TOP_K


def retrieve(question):

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    db = FAISS.load_local(
        VECTOR_DB_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return db.similarity_search(
        question,
        k=TOP_K
    )