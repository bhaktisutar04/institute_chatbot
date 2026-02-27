import os #read environment variables (API keys)
import pandas as pd
from dotenv import load_dotenv #load .env file into environment

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from groq import Groq

load_dotenv()

# =========================
# GROQ CLIENT
# =========================
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# EMBEDDING MODEL (MiniLM)
# =========================
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================
# CREATE VECTOR STORE (FIXED)
# =========================
def create_vectorstore(uploaded_file):

    print("Reading Excel file...")
    df = pd.read_excel(uploaded_file)

    texts = []
    for _, row in df.iterrows():
        text = f"""
Category: {row.get('Category','')}
Topic: {row.get('Topic','')}
Information: {row.get('Information','')}
"""
        texts.append(text.strip())

    print("Total rows:", len(texts))

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )

    docs = splitter.create_documents(texts)
    print("Docs created:", len(docs))

    # =========================
    # CONNECT PINECONE
    # =========================
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX")

    index = pc.Index(index_name)

    # =========================
    # CLEAR OLD DATA (IMPORTANT FIX)
    # =========================
    print("Clearing old Pinecone vectors...")
    index.delete(delete_all=True)

    # =========================
    # UPLOAD NEW DATA
    # =========================
    print("Uploading new embeddings...")
    vectorstore = PineconeVectorStore.from_documents(
        docs,
        embeddings,
        index_name=index_name
    )

    print("Uploaded to Pinecone successfully!")
    return vectorstore


# =========================
# LOAD EXISTING VECTOR STORE
# =========================
# def load_vectorstore():

#     print("Loading existing Pinecone index...")

#     vectorstore = PineconeVectorStore(
#         index_name=os.getenv("PINECONE_INDEX"),
#         embedding=embeddings
#     )

#     return vectorstore


# =========================
# ASK QUESTION
# =========================
def ask(vectorstore, question):

    docs = vectorstore.similarity_search(question, k=5)

    if len(docs) == 0:
        return "No relevant data found in database."

    context = "\n\n".join([d.page_content for d in docs])

    prompt = f"""
You are a helpful institute assistant.

Rules:
- Answer using context if available
- If context weak, answer normally
- Keep answer simple

Context:
{context}

Question:
{question}

Answer:
"""

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content
