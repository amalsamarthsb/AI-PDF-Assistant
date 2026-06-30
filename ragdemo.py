from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Create embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Load FAISS database
db = FAISS.load_local(
    "vectorstore",
    embeddings,
    allow_dangerous_deserialization=True
)

# Ask the user a question
question = input("Ask a question: ")

# Retrieve top 3 similar chunks
results = db.similarity_search(question, k=3)

# Display the retrieved chunks
for i, doc in enumerate(results, start=1):
    print(f"\nResult {i}")
    print("=" * 60)

    print("Page:", doc.metadata.get("page"))

    print()

    print(doc.page_content)