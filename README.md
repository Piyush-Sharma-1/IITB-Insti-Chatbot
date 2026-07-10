\# IITB Insti-Assist — Academic Assistant



A RAG-powered assistant that answers questions about IIT Bombay's academic rules, grading system, and exam policies, grounded in official institute documents.



\## Features

\- Answers questions using 6 official IITB academic documents (grading, registration, exam malpractice rules, calendar)

\- Refuses to answer when information isn't in the documents

\- Shows source documents for every answer

\- Supports uploading additional PDFs during a session

\- Multi-turn chat with follow-up question understanding



\## Setup



1\. Clone this repo and navigate into it

2\. Create a virtual environment:

python -m venv venv

venv\\Scripts\\Activate.ps1

3\. Install dependencies:

pip install pypdf sentence-transformers faiss-cpu openai streamlit

4\. Set your Groq API key as an environment variable:

\[System.Environment]::SetEnvironmentVariable("GROQ\_API\_KEY", "your-key-here", "User")

5\. Place source PDFs in the `docs/` folder

6\. Run the ingestion pipeline:

python extract\_text.py

python chunk\_documents.py

python build\_index.py

7\. Launch the app:

streamlit run app.py



\## Tech stack

\- Embeddings: sentence-transformers (all-MiniLM-L6-v2)

\- Vector search: FAISS

\- LLM: Groq API (Llama 3.1 8B Instant)

\- UI: Streamlit



\## Data sources

6 official IIT Bombay academic documents covering grading policy, UG/PG rules, exam malpractice procedures, and the academic calendar.

