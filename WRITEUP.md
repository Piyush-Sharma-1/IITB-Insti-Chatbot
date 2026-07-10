# IITB Insti-Assist — Project Write-up

## 1. Chosen Scope and Why

I chose the **Academic Assistant** scope, which focuses on course registration, grading policies, examination rules, and the academic calendar. Initially, I planned to build the **Hostel & Campus Life Assistant**, but after reviewing the available data sources, I found that the academic documents contained much more structured and precise information.

The rulebooks include well-defined policies such as grade codes (`DD`, `FF`, `FR`, `DX`), attendance requirements, registration rules, and exact penalties for academic malpractice. This type of factual, reference-based content is well suited for a Retrieval-Augmented Generation (RAG) system because retrieved answers can be easily verified against the original documents.

---

## 2. Data Sources Used

I used six official IIT Bombay documents obtained directly from the `acad.iitb.ac.in` and `iitb.ac.in` domains.

1. **UG Rule Book (Academic Office)** – Registration categories, attendance rules, examination policies, and grading.
2. **Academic Calendar 2026–27** – Semester schedule, registration dates, and important academic deadlines.
3. **Grading System Document** – Meanings of letter grades such as `DD`, `FF`, `FR`, `DX`, `II`, and `AU`.
4. **M.Tech/MPP/M.Des/MBA Academic Rules** – Postgraduate regulations including NPTEL/SWAYAM courses and course withdrawal.
5. **UG Rule Book (Older Version)** – Additional undergraduate regulations and academic malpractice policies.
6. **Disciplinary Actions for Academic Malpractice** – Official penalties for examination violations (e.g., carrying a mobile phone during an exam results in an `FR` grade).

I intentionally limited the dataset to these six documents because many other rulebooks available online were near-duplicates. Including them would have increased retrieval redundancy without providing significant new information.

---

## 3. Chunking Strategy

The documents were split using **fixed-size character chunking**, with each chunk containing **1000 characters** and an **overlap of 200 characters** between consecutive chunks.

I selected fixed-size chunking because the extracted PDF text did not preserve a reliable document structure. Section headers, bullet points, and numbered lists were often flattened during PDF extraction, making structure-aware chunking unreliable without significant preprocessing.

The 200-character overlap helps preserve information that might otherwise be split across chunk boundaries. This ensures that important facts remain complete in at least one retrieved chunk.

Across all six documents (approximately **257,000 characters**), this process generated **324 chunks**.

---

## 4. System Architecture

- **PDF Extraction:** `pypdf`
- **Embedding Model:** `sentence-transformers (all-MiniLM-L6-v2)`
- **Vector Database:** `FAISS (IndexFlatL2)`
- **Language Model:** Groq API using **Llama 3.1 8B Instant**
- **Grounding Mechanism:** The model is instructed to return the exact token `NOT_FOUND_IN_DOCUMENTS` whenever the retrieved context does not contain the requested information. The application then converts this into a user-friendly message ("I don't know based on the available documents") without displaying misleading citations.
- **User Interface:** Streamlit with a chat-style interface.

---

## 5. Bonus Features Implemented

### Live PDF Upload

Users can upload an additional PDF during a session. The uploaded document is chunked, embedded, and merged with the existing FAISS index for that session only. The original stored index remains unchanged.

### Multi-turn Conversational Memory

Follow-up questions such as *"What about FF?"* are automatically rewritten into complete, standalone questions using recent conversation history before retrieval. The final prompt also includes recent chat context, allowing the assistant to answer naturally in multi-turn conversations.

---

## 6. Known Limitations and Future Improvements

Although the system performs well for factual academic queries, there are several areas for improvement.

- **Fixed-size chunking** may split tables or numbered lists, reducing retrieval quality. Structure-aware chunking based on document sections could improve context preservation.

- **No re-ranking stage** is currently used. The system retrieves the top four chunks directly from FAISS. Adding a cross-encoder re-ranker could improve retrieval accuracy.

- **Duplicate retrievals** occasionally occur because the older and newer UG rulebooks contain similar content. Deduplicating highly similar chunks would increase retrieval diversity.

- **Citation highlighting** currently displays the entire retrieved chunk rather than highlighting the exact sentence used to generate the answer.

- **No caching** is implemented. Every query performs embedding, retrieval, and LLM inference even if the same question has already been asked.

---

## 7. Testing Performed

The assistant was evaluated using multiple categories of queries.

- **Single-document factual questions**
  - Example: *"What grade is awarded if a student is caught with a mobile phone during an examination?"*
  - The system correctly retrieved the disciplinary rules and answered **FR grade**.

- **Multi-document reasoning**
  - Example: Comparing the meanings and implications of **FR** and **DX** grades using information from multiple documents.

- **Out-of-scope questions**
  - Example: *"How are you ?"*
  - The system correctly returned an "I don't know based on the available documents" response instead of hallucinating an answer.

- **Live document upload**
  - A hostel rules PDF was uploaded during runtime to verify that newly added documents could be retrieved correctly while maintaining access to the original academic knowledge base.
