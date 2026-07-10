import json
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from openai import OpenAI

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("vector_index.faiss")

with open("chunks_metadata.pkl", "rb") as f:
    chunks = pickle.load(f)

import os
client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1"
)

TOP_K = 4

def retrieve(query):
    query_vector = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vector, TOP_K)
    results = []
    for idx in indices[0]:
        results.append(chunks[idx])
    return results

def build_prompt(query, retrieved_chunks):
    context_text = ""
    for i, chunk in enumerate(retrieved_chunks):
        context_text += f"[Source: {chunk['source']}]\n{chunk['text']}\n\n"

    prompt = f"""You are an assistant that answers questions about IIT Bombay academics using ONLY the context provided below.

If the answer is not contained in the context, say "I don't know based on the available documents." Do not make up information.

CONTEXT:
{context_text}

QUESTION: {query}

ANSWER:"""
    return prompt

def ask(query):
    retrieved_chunks = retrieve(query)
    prompt = build_prompt(query, retrieved_chunks)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content
    if "i don't know" in answer.lower():
        sources = []
    else:
        sources = list(set(chunk["source"] for chunk in retrieved_chunks))

    return answer, sources
if __name__ == "__main__":
    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() == "exit":
            break
        answer, sources = ask(query)
        print(f"\nAnswer: {answer}")
        print(f"Sources: {sources}")