from dotenv import load_dotenv
import os

from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.3,
)


def build_prompt(question, context):
    return f"""
You are an expert AI assistant.

Answer ONLY using the supplied context.

If the answer is not present, say:
'I couldn't find that information in the uploaded documents.'

Context:
{context}

Question:
{question}

Answer:
"""


def ask_llm(question, context):
    prompt = build_prompt(question, context)
    response = llm.invoke(prompt)
    return response.content


def stream_llm(question, context):
    prompt = build_prompt(question, context)
    return llm.stream(prompt)