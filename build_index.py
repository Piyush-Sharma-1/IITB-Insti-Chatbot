import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import pickle

print("Loading embedding model...")
model = SentenceTransformer("all-MiniLM-L6-v2")

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

texts = [chunk["text"] for chunk in chunks]

print(f"Embedding {len(texts)} chunks...")
embeddings = model.encode(texts, show_progress_bar=True)
embeddings = np.array(embeddings).astype("float32")

dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, "vector_index.faiss")

with open("chunks_metadata.pkl", "wb") as f:
    pickle.dump(chunks, f)

print(f"Done. Index has {index.ntotal} vectors of dimension {dimension}.")