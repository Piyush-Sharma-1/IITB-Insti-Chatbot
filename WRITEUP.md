# IITB Insti-Chatbot — Project Write-up

**Live demo:** https://iitb-insti-chatbot-gq5etbjf5lh6tqegthr4px.streamlit.app/

## 1. Chosen scope and why ?

I opted for the **Academic Assistant** scope — course registration, grading policy, exam rules, academic calendar. In fact, I was going to build the Hostel & Campus Life assistant first but when I looked at the data available for each, I decided to change my mind. The academic rulebooks were discovered to have a lot more precise, lookup-type content (specific grade codes like DD/FF/FR/DX, exact attendance percentages and specific disciplinary actions for academic malpractice) than hostel documents, which were more spread out across individual hostel pages and less uniform in format. This type of factual content works better with RAG, because we can check the retrieved answers directly against the official documents.

## 2. Data sources used

I have used six official IIT Bombay documents, all of which were directly obtained from the `acad.iitb.ac.in` and `iitb.ac.in` domains :

1. **ugrulebook.pdf** — Undergraduate Rule Book on course registration, attendance requirements, grading rules, examinations and academic regulations.
2. **Academic_Calendar_2026-27_FINAL.pdf** – Academic calendar with semester timelines, registration periods, holidays and examination schedules.
3. **grading.pdf** — Official grading system (DD, FF, FR, DX, II, AU).
4. **M.Tech_. MPP. M.Des_. MBA Rules_0.pdf** — Rules for postgraduate academics including NPTEL/SWAYAM policies, withdrawal of courses and programme-specific rules.
5. **procedures201521July.pdf** — Procedures followed by D-ADAC and ADAC for investigating academic malpractice cases
6. **punishments201521July.pdf** – Official disciplinary actions and sanctions for a variety of examination malpractices.



## 3. Chunking strategy and why ?

I used a fixed-size character chunking strategy with **1000 characters per chunk** and an **overlap of 200 characters** between consecutive chunks.

I chose this method because the extracted PDF text did not keep a consistent structure. During PDF extraction, section headings, bullet points, and numbered lists were often turned into plain text. This made structure-aware chunking unreliable without significant preprocessing.

The 200-character overlap ensures that information near chunk boundaries is not lost. If an important sentence is split across two chunks, the overlap ensures it stays complete in at least one retrieved chunk.

The six documents have about **257,000 characters**, resulting in a total of **324 chunks**.

## 4. System architecture

- **Extraction:** Use `pypdf` to get raw text from PDF documents.  
- **Embedding:** Use `sentence-transformers` with the `all-MiniLM-L6-v2` model to create local embeddings.  
- **Vector Database:** FAISS (`IndexFlatL2`) stores all 324 embeddings and performs exact nearest-neighbor searches.  
- **LLM:** Groq API runs **Llama 3.1 8B Instant**. It was chosen for its fast inference speed and generous free tier.  
- **Grounding:** The prompt tells the model to return the token `NOT_FOUND_IN_DOCUMENTS` whenever the retrieved context lacks the requested information. The application changes this into a clear response: *"I don't know based on the available documents,"* without showing misleading citations.  
- **User Interface:** Streamlit provides a chat-based interface, deployed on Streamlit Community Cloud.  

## 5. Extra features implemented

### Live PDF Upload

Users can upload an extra PDF during a session. The uploaded document gets chunked, embedded, and merged with the existing FAISS index only for that session. The original stored index stays the same.

### Multi-turn Conversational Memory

Follow-up questions such as *"What about FF?"* get automatically rewritten into standalone questions using the recent conversation history before retrieval. Recent chat history is also given to the language model during answer generation to keep the conversation flowing.

## 6. Known limitations and future improvements

- **Fixed-size chunking** sometimes splits tables and numbered lists, which affects retrieval quality. Chunking based on document sections would probably yield better results.

- **No re-ranking stage** is currently in place. Retrieval depends only on the top four FAISS results. Adding a cross-encoder re-ranker could increase retrieval accuracy.

- **Near-duplicate chunks** from overlapping rulebooks can take up multiple retrieval slots. Removing highly similar chunks would enhance result diversity.

- **Citation highlighting** currently shows the entire retrieved chunk rather than just highlighting the specific sentence used to create the answer.

- **No caching** is implemented. Every query performs embedding, retrieval, and LLM inference even if the same question has been asked during the session.

## 7. Testing performed

The system was tested using various types of test cases:

- **Single-document factual queries**, like *"What grade do I get if caught with a mobile phone during an exam?"*, which correctly returned the **FR** grade using `punishments201521July.pdf`.

- **Multi-document questions**, such as comparing the meanings and implications of `FR` and `DX` grades.

- **Out-of-scope questions**, like *"How are you?"*, to check that the assistant does not make up answers and states that the information is not available in the provided documents.

- **Live PDF upload testing**, where a hostel rules PDF was uploaded during runtime to check retrieval from newly added documents without impacting the original knowledge base.

- **Multi-turn conversations**, like asking *"What is a DX grade?"* followed by *"What about FF?"*, to verify conversational memory and question rewriting.

- **End-to-end testing** on the deployed Streamlit application using both academic and out-of-scope queries.
