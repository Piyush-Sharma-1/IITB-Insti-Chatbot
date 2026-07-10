import os
from pypdf import PdfReader

DOCS_FOLDER = "docs"

def extract_all_pdfs():
    all_documents = []

    for filename in os.listdir(DOCS_FOLDER):
        if filename.endswith(".pdf"):
            filepath = os.path.join(DOCS_FOLDER, filename)
            reader = PdfReader(filepath)

            full_text = ""
            for page in reader.pages:
                full_text += page.extract_text() + "\n"

            all_documents.append({
                "source": filename,
                "text": full_text
            })
            print(f"Extracted {filename}: {len(full_text)} characters")

    return all_documents

if __name__ == "__main__":
    documents = extract_all_pdfs()
    print(f"\nTotal documents extracted: {len(documents)}")