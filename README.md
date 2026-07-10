# IITB Insti-Assist — Academic Assistant

A RAG chatbot to answer questions about IIT Bombay’s academic rules, grading system, examination policies and academic calendar using official institute documents.

## Live Demo

**https://iitb-insti-chatbot-gq5etbjf5lh6tqegthr4px.streamlit.app/**

## Features

- Answers academic queries with six official IIT Bombay documents.
- It uses Retrieval Augmented Generation (RAG) to provide grounded factually correct answers.
- Does not answer when the requested information is not in the available documents.
- Indicates the document(s) from the source that support each answer.
- Allows uploading other PDF documents during an active session for temporary retrieval.
- 

## Project Structure

```text
.
├── .streamlit/
│   └── config.toml
├── docs/
├── .gitignore
├── README.md
├── WRITEUP.md
├── app.py
├── build_index.py
├── chunk_documents.py
├── chunks.json
├── chunks_metadata.pkl
├── extract_text.py
├── query_rag.py
├── requirements.txt
└── vector_index.faiss
```

## Setup

### 1. Clone the repository

### 2. Create a virtual environment

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/macOS**

```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install the required  dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is unavailable:

```bash
pip install pypdf sentence-transformers faiss-cpu openai streamlit
```

### 4. Configure the Groq API key

**Windows (PowerShell)**

```powershell
[System.Environment]::SetEnvironmentVariable("GROQ_API_KEY","your-api-key","User")
```

Restart the  terminal after setting the environment variable.

### 5. Add the source documents

Place all the  official IIT Bombay PDF documents inside the `docs/` directory.

### 6. Build the knowledge base

```bash
python extract_text.py
python chunk_documents.py
python build_index.py
```

### 7. Run the application

```bash
streamlit run app.py
```

The application will open in your browser at:

```
http://localhost:8501
```

## Technology Stack

- **Programming Language:** Python
- **PDF Extraction:** `pypdf`
- **Embedding Model:** `sentence-transformers` (`all-MiniLM-L6-v2`)
- **Vector Database:** FAISS (`IndexFlatL2`)
- **LLM:** Groq API using **Llama 3.1 8B Instant**
- **Frontend:** Streamlit

## Data Sources

The knowledge base consists of six official IIT Bombay academic documents:

- `ugrulebook.pdf`
- `Academic_Calendar_2026-27_FINAL.pdf`
- `grading.pdf`
- `M.Tech_. MPP. M.Des_. MBA Rules_0.pdf`
- `procedures201521July.pdf`
- `punishments201521July.pdf`

## How It Works

1. PDF files are converted into plain text.
2. The extracted text is divided into overlapping chunks.
3. Each chunk is embedded by `all-MiniLM-L6-v2` model.
4. FAISS retrieves the most relevant chunks for a user query.
5. The retrieved context is sent to Llama 3.1 8B Instant through the Groq API.
6. The assistant then generates a response using the retrieved documents, citing the sources that back up the answer.
