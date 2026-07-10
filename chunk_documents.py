import os
from pypdf import PdfReader
import json

DOCS_FOLDER = "docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

def extract_all_pdfs():
    all_documents = []
    for filename in os.listdir(DOCS_FOLDER):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DOCS_FOLDER, filename)
            reader = PdfReader(filepath)
            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"
            all_documents.append({"source": filename, "text": full_text})
    return all_documents

def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

def build_chunks():
    documents = extract_all_pdfs()
    all_chunks = []
    for doc in documents:
        pieces = chunk_text(doc["text"])
        for i, piece in enumerate(pieces):
            all_chunks.append({
                "source": doc["source"],
                "chunk_id": f"{doc['source']}_{i}",
                "text": piece
            })
    return all_chunks

if __name__ == "__main__":
    chunks = build_chunks()
    print(f"Total chunks created: {len(chunks)}")

    with open("chunks.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)
    print("Saved to chunks.json")