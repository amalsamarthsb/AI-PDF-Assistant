print("Loading hybrid_retriever...")
from rank_bm25 import BM25Okapi

from services.retriever import retrieve

documents = []
tokenized_documents = []
bm25 = None


def initialize_bm25(chunks):

    global documents
    global tokenized_documents
    global bm25

    documents = chunks

    tokenized_documents = [
        chunk.page_content.lower().split()
        for chunk in chunks
    ]

    bm25 = BM25Okapi(tokenized_documents)


def hybrid_retrieve(question, top_k=4):

    semantic_docs = retrieve(question)

    if bm25 is None:
        return semantic_docs

    tokens = question.lower().split()

    scores = bm25.get_scores(tokens)

    ranked = sorted(
        zip(scores, documents),
        key=lambda x: x[0],
        reverse=True
    )

    keyword_docs = [
        doc
        for _, doc in ranked[:top_k]
    ]

    combined = []

    seen = set()

    for doc in semantic_docs + keyword_docs:

        text = doc.page_content

        if text not in seen:

            combined.append(doc)

            seen.add(text)

    return combined