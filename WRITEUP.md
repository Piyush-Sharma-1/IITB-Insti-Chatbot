# IITB Insti-Chatbot — Project Write-up

**Live demo:** https://iitb-insti-chatbot-gq5etbjf5lh6tqegthr4px.streamlit.app/

## 1. Chosen scope and why

I picked the **Academic Assistant** scope — course registration, grading policy, exam rules, and academic calendar. I actually started out planning to build the Hostel & Campus Life assistant, but after looking at what data was available for each, I switched. The academic rulebooks turned out to have much more precise, lookup-style content (specific grade codes like DD/FF/FR/DX, exact attendance percentages, and specific disciplinary actions for academic malpractice) compared to hostel documents, which were more scattered across individual hostel pages and less consistent in format. Precise, factual content like this is a better fit for RAG because the retrieved answers can be verified directly against the official documents.

## 2. Data sources used

I used six official IIT Bombay documents, all obtained directly from the `acad.iitb.ac.in` and `iitb.ac.in` domains :

1. **ugrulebook.pdf** — Undergraduate Rule Book covering course registration, attendance requirements, grading rules, examinations, and academic regulations.
2. **Academic_Calendar_2026-27_FINAL.pdf** — Academic calendar containing semester timelines, registration periods, holidays, and examination schedules.
3. **grading.pdf** — Official grading system explaining grades such as `DD`, `FF`, `FR`, `DX`, `II`, and `AU`.
4. **M.Tech_. MPP. M.Des_. MBA Rules_0.pdf** — Postgraduate academic regulations including NPTEL/SWAYAM policies, course withdrawal, and programme-specific rules.
5. **procedures201521July.pdf** — Procedures followed by D-ADAC and ADAC for investigating academic malpractice cases.
6. **punishments201521July.pdf** — Official disciplinary actions and penalties for various examination malpractices.

I deliberately limited the knowledge base to these six documents because several other IIT Bombay rulebooks available online were largely duplicated versions of the same regulations. Including them would have increased retrieval redundancy without improving coverage.

## 3. Chunking strategy and why

I used a fixed-size character chunking strategy with **1000 characters per chunk** and an **overlap of 200 characters** between consecutive chunks.

I chose this approach because the extracted PDF text did not preserve a consistent structure. During PDF extraction, section headings, bullet points, and numbered lists were often flattened into plain text, making structure-aware chunking unreliable without significant preprocessing.

The 200-character overlap ensures that information near chunk boundaries is not lost. If an important sentence is split across two chunks, the overlap ensures it remains complete in at least one retrieved chunk.

The six documents contain approximately **257,000 characters**, resulting in a total of **324 chunks**.

## 4. System architecture

- **Extraction:** `pypdf` for extracting raw text from PDF documents.
- **Embedding:** `sentence-transformers` using the `all-MiniLM-L6-v2` model to generate local embeddings.
- **Vector Database:** FAISS (`IndexFlatL2`) storing all 324 embeddings and performing exact nearest-neighbor search.
- **LLM:** Groq API running **Llama 3.1 8B Instant**, chosen because of its fast inference speed and generous free tier.
- **Grounding:** The prompt instructs the model to return the exact token `NOT_FOUND_IN_DOCUMENTS` whenever the retrieved context does not contain the requested information. The application converts this into a clear *"I don't know based on the available documents"* response without displaying misleading citations.
- **User Interface:** Streamlit with a chat-based interface deployed on Streamlit Community Cloud.

## 5. Extra features implemented

### Live PDF Upload

Users can upload an additional PDF during a session. The uploaded document is chunked, embedded, and merged with the existing FAISS index only for that session. The original stored index remains unchanged.

### Multi-turn Conversational Memory

Follow-up questions such as *"What about FF?"* are automatically rewritten into standalone questions using recent conversation history before retrieval. Recent chat history is also supplied to the language model during answer generation to maintain conversational context.

## 6. Known limitations and future improvements

- **Fixed-size chunking** occasionally splits tables and numbered lists, reducing retrieval quality. Structure-aware chunking based on document sections would likely improve results.

- **No re-ranking stage** is currently used. Retrieval relies solely on the top four FAISS results. Adding a cross-encoder re-ranker could improve retrieval accuracy.

- **Near-duplicate chunks** from overlapping rulebooks sometimes occupy multiple retrieval slots. Deduplicating highly similar chunks would improve result diversity.

- **Citation highlighting** currently displays the complete retrieved chunk instead of highlighting only the specific sentence used to generate the answer.

- **No caching** is implemented. Every query performs embedding, retrieval, and LLM inference even if the same question has already been asked during the session.

## 7. Testing performed

The system was evaluated using several categories of test cases:

- **Single-document factual queries**, such as *"What grade do I get if caught with a mobile phone during an exam?"*, which correctly returned the **FR** grade using `punishments201521July.pdf`.

- **Multi-document questions**, such as comparing the meanings and implications of `FR` and `DX` grades.

- **Out-of-scope questions**, such as *"How are you ?"*, to verify that the assistant refuses to hallucinate answers and instead reports that the information is unavailable in the provided documents.

- **Live PDF upload testing**, where a hostel rules PDF was uploaded during runtime to verify retrieval from newly added documents without affecting the original knowledge base.

- **Multi-turn conversations**, such as asking *"What is a DX grade?"* followed by *"What about FF?"*, to verify conversational memory and question rewriting.

- **End-to-end testing** on the deployed Streamlit application using both academic and out-of-scope queries.
