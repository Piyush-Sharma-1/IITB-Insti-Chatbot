\# IITB Insti-Assist — Project Write-up



\## 1. Chosen scope and why



I picked the \*\*Academic Assistant\*\* scope — course registration, grading policy, exam rules, and academic calendar. I actually started out planning to build the Hostel \& Campus Life assistant, but after looking at what data was available for each, I switched. The academic rulebooks turned out to have much more precise, lookup-style content (specific grade codes like DD/FF/FR/DX, exact attendance percentages, specific fine amounts for exam malpractice) compared to hostel documents, which were more scattered across individual hostel pages and less consistent in format. Precise, factual content like this is a better fit for RAG, since it's easy to verify whether the retrieved answer is actually correct.



\## 2. Data sources used



I used 6 official IIT Bombay documents, all pulled directly from `acad.iitb.ac.in` and `iitb.ac.in` domains (not third-party aggregator sites):



1\. UG Rule Book (Academic Office) — registration categories, attendance rules, exam weightage

2\. Academic Calendar 2026–27 — semester dates, registration windows

3\. Grading System document — letter grades and their meaning (DD, FF, FR, DX, II, AU)

4\. M.Tech/MPP/M.Des/MBA Rules — postgraduate-specific policies (NPTEL/SWAYAM courses, course withdrawal)

5\. UG Rule Book (older/full version) — broader undergraduate rules and academic malpractice overview

6\. Disciplinary Actions for Academic Malpractice — exact penalties for specific violations (e.g. mobile phone in exam → FR grade)



I deliberately kept this to 6 rather than adding more, since several other IITB rulebooks I found while searching were near-duplicates of documents I already had (IITB republishes similar rulebooks across years). Adding those would have added retrieval noise without adding new information.



\## 3. Chunking strategy and why



I used a fixed-size character chunking approach: \*\*1000 characters per chunk, with 200 characters of overlap\*\* between consecutive chunks.



I chose fixed-size chunking over more complex approaches (like splitting by paragraph or by section headers) mainly for simplicity and reliability — the PDFs I extracted text from didn't have consistent, machine-readable structure (headers, bullet points, and numbered sections often got flattened into plain text during PDF extraction), so structure-aware chunking would have been unreliable without a lot of extra cleanup work.



The 200-character overlap was important: without it, a fact that happens to sit right at a chunk boundary (e.g. "the fine for the second offense is Rs. 1000" split right after "is") would get cut and potentially lost from both chunks. The overlap means most important facts appear fully intact in at least one chunk.



With 6 documents totaling roughly 257,000 characters, this produced 324 chunks total.



\## 4. System architecture



\- \*\*Extraction:\*\* `pypdf` to pull raw text out of each PDF

\- \*\*Embedding:\*\* `sentence-transformers` (`all-MiniLM-L6-v2`) — a free, local embedding model, so no per-query embedding cost

\- \*\*Vector storage/search:\*\* FAISS (`IndexFlatL2`), storing all 324 chunk embeddings and doing brute-force nearest-neighbor search (fine at this scale — no need for approximate search methods)

\- \*\*LLM:\*\* Groq API running Llama 3.1 8B Instant — chosen for its free tier and fast response times, since OpenAI's API requires paid credits

\- \*\*Grounding mechanism:\*\* the prompt instructs the model to respond with an exact marker string (`NOT\_FOUND\_IN\_DOCUMENTS`) when the retrieved context doesn't answer the question, which the app then converts into a clear "I don't know based on the available documents" message with no sources shown. This was more reliable than trying to pattern-match every possible way the model might phrase a refusal.

\- \*\*UI:\*\* Streamlit, with a chat-style interface



\## 5. Bonus features implemented



\- \*\*Live PDF upload:\*\* users can upload an additional PDF during a session, which gets chunked and embedded on the fly and merged with the base 324-chunk index for that session only (the original saved index on disk is never modified)

\- \*\*Multi-turn conversational memory:\*\* follow-up questions like "what about FF?" are first rewritten into a self-contained question using recent chat history before retrieval, and the final answer prompt also includes recent conversation turns for context



\## 6. Known limitations / what I'd improve with more time



\- \*\*Fixed-size chunking is crude.\*\* It occasionally cuts a chunk in the middle of a table or a numbered list, which can lose some structure that would help the model. With more time, I'd try structure-aware chunking (e.g. splitting on section numbers like "5.2", "5.3" which appear throughout these rulebooks).

\- \*\*No re-ranking step.\*\* Retrieval currently just takes the top-4 nearest chunks by embedding similarity. Sometimes a highly relevant chunk ranks 5th or 6th and gets missed. A re-ranking step (using a cross-encoder or asking the LLM to re-score retrieved chunks) would likely improve accuracy.

\- \*\*The overlapping rulebooks (older vs newer UG rule books) sometimes retrieve near-duplicate chunks\*\*, taking up slots in the top-4 that could have gone to a more diverse set of sources. Deduplicating near-identical chunks across documents would help.

\- \*\*Citation highlighting is partial.\*\* The app shows the full retrieved chunk text as supporting evidence, but doesn't highlight the exact sentence(s) the answer was based on within that chunk. A cleaner version would ask the model to also return the specific span of text it used, and highlight only that.

\- \*\*No answer caching.\*\* Every question re-runs embedding + search + an LLM call, even if asked before in the same session. Caching repeated questions would reduce latency and API calls.



\## 7. Testing performed



I tested the system with:

\- Direct factual questions answerable from a single document (e.g. "What grade do I get if caught with a mobile phone during an exam?" → correctly answered "FR grade" with the right source)

\- Questions requiring synthesis across two documents (e.g. comparing FR vs DX grades)

\- Out-of-scope questions (e.g. "What is the capital of France?") to confirm the system correctly refuses rather than hallucinating

\- A live-uploaded hostel rules PDF, to confirm the upload feature retrieves correctly from newly added documents without breaking retrieval from the original 6

