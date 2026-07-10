import streamlit as st
import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI
from pypdf import PdfReader
import os

st.set_page_config(page_title="IITB Academic Assistant")

st.markdown("""
<style>
    h1, h2, h3 {
        color: #8B0000 !important;
        font-family: Georgia, serif;
    }
    .stApp {
        font-family: Georgia, serif;
    }
</style>
""", unsafe_allow_html=True)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K = 4
HISTORY_TURNS_FOR_CONTEXT = 3

@st.cache_resource
def load_resources():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    index = faiss.read_index("vector_index.faiss")
    with open("chunks_metadata.pkl", "rb") as f:
        chunks = pickle.load(f)
    client = OpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
    return model, index, chunks, client

model, base_index, base_chunks, client = load_resources()

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_uploaded_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    pieces = chunk_text(full_text)
    new_chunks = []
    for i, piece in enumerate(pieces):
        new_chunks.append({
            "source": uploaded_file.name,
            "chunk_id": f"{uploaded_file.name}_{i}",
            "text": piece
        })

    new_texts = [c["text"] for c in new_chunks]
    new_embeddings = model.encode(new_texts).astype("float32")

    return new_chunks, new_embeddings

def build_combined_index():
    if "uploaded_embeddings" not in st.session_state or len(st.session_state.uploaded_embeddings) == 0:
        return base_index, base_chunks

    dimension = st.session_state.uploaded_embeddings[0].shape[0]
    combined_index = faiss.IndexFlatL2(dimension)

    base_vectors = base_index.reconstruct_n(0, base_index.ntotal)
    combined_index.add(base_vectors)
    combined_index.add(np.array(st.session_state.uploaded_embeddings).astype("float32"))

    combined_chunks = base_chunks + st.session_state.uploaded_chunks
    return combined_index, combined_chunks

def retrieve(query, index, chunks):
    query_vector = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vector, TOP_K)
    return [chunks[idx] for idx in indices[0]]

def rewrite_query_with_history(query, history):
    if not history:
        return query

    recent = history[-(HISTORY_TURNS_FOR_CONTEXT * 2):]
    history_text = ""
    for turn in recent:
        history_text += f"{turn['role'].upper()}: {turn['content']}\n"

    rewrite_prompt = f"""Given this conversation history and a new follow-up question, rewrite the follow-up question to be fully self-contained (understandable without the history). If the new question is already self-contained, return it unchanged. Respond with ONLY the rewritten question, nothing else.

HISTORY:
{history_text}

NEW QUESTION: {query}

REWRITTEN QUESTION:"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": rewrite_prompt}]
    )
    return response.choices[0].message.content.strip()

def build_prompt(query, retrieved_chunks, history):
    context_text = ""
    for chunk in retrieved_chunks:
        context_text += f"[Source: {chunk['source']}]\n{chunk['text']}\n\n"

    history_text = ""
    if history:
        recent = history[-(HISTORY_TURNS_FOR_CONTEXT * 2):]
        for turn in recent:
            history_text += f"{turn['role'].upper()}: {turn['content']}\n"

    return f"""You are an assistant that answers questions about IIT Bombay academics using ONLY the context provided below.

Rules:
1. If the context contains enough information to answer the question, answer it clearly and directly using only that information. Do not mention file names, document names, or write things like "(Source: ...)" anywhere in your answer.
2. If the context does NOT contain enough information to answer the question, respond with EXACTLY this text and nothing else: NOT_FOUND_IN_DOCUMENTS
3. Use the conversation history only to understand what the user is referring to. Do not answer from the history itself unless it is also supported by the context.

CONVERSATION HISTORY:
{history_text}

CONTEXT:
{context_text}

QUESTION: {query}

ANSWER:"""

def ask(query, index, chunks, history):
    search_query = rewrite_query_with_history(query, history)
    retrieved_chunks = retrieve(search_query, index, chunks)
    prompt = build_prompt(query, retrieved_chunks, history)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    if "NOT_FOUND_IN_DOCUMENTS" in answer:
        answer = "I don't know based on the available documents."
        sources = []
    else:
        sources = list(set(chunk["source"] for chunk in retrieved_chunks))

    return answer, sources, retrieved_chunks

st.title("IITB Academic Helper")
st.caption("Ask about grading, registration, and exam rules at IIT Bombay")

if "uploaded_chunks" not in st.session_state:
    st.session_state.uploaded_chunks = []
    st.session_state.uploaded_embeddings = []
    st.session_state.uploaded_filenames = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_sources" not in st.session_state:
    st.session_state.last_sources = {}

st.subheader("Add your own document (optional)")
uploaded_file = st.file_uploader("Upload a PDF to add it to this session's knowledge base", type=["pdf"])

if uploaded_file is not None and uploaded_file.name not in st.session_state.uploaded_filenames:
    with st.spinner("Reading and indexing your PDF..."):
        new_chunks, new_embeddings = process_uploaded_pdf(uploaded_file)
        st.session_state.uploaded_chunks.extend(new_chunks)
        for emb in new_embeddings:
            st.session_state.uploaded_embeddings.append(emb)
        st.session_state.uploaded_filenames.append(uploaded_file.name)
    st.success(f"Added {uploaded_file.name} ({len(new_chunks)} chunks) to this session.")

if st.session_state.uploaded_filenames:
    st.caption("Session documents: " + ", ".join(st.session_state.uploaded_filenames))

st.subheader("Chat")

for i, turn in enumerate(st.session_state.chat_history):
    with st.chat_message(turn["role"]):
        st.write(turn["content"])
        if turn["role"] == "assistant" and i in st.session_state.last_sources:
            sources = st.session_state.last_sources[i]
            if sources:
                st.caption("Sources: " + ", ".join(sources))

query = st.chat_input("Ask a question about IITB academics:")

if query:
    st.session_state.chat_history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching documents and generating answer..."):
            current_index, current_chunks = build_combined_index()
            answer, sources, retrieved_chunks = ask(
                query, current_index, current_chunks, st.session_state.chat_history[:-1]
            )
        st.write(answer)
        if sources:
            st.caption("Sources: " + ", ".join(sources))

    st.session_state.chat_history.append({"role": "assistant", "content": answer})
    st.session_state.last_sources[len(st.session_state.chat_history) - 1] = sources

if st.button("Clear conversation"):
    st.session_state.chat_history = []
    st.session_state.last_sources = {}
    st.rerun()