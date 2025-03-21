import sqlite3
import os
import re
import magic
import textract
import spacy
from pdfminer.high_level import extract_text as extract_pdf_text

DATABASE = "db.db"
nlp = spacy.load("en_core_web_sm")

def extract_terms(text):
    """Extracts meaningful words from text using spaCy, removing unnecessary tokens."""
    doc = nlp(text.lower())
    return [token.lemma_ for token in doc if not token.is_stop and not token.is_punct and not token.is_digit and token.is_alpha]

def extract_text(file_path):
    """Extracts pure plain text from any document, handling different formats."""
    try:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".pdf":
            text = extract_pdf_text(file_path)
        else:
            text = textract.process(file_path).decode(errors="replace")
        return text.strip()
    except Exception as e:
        print(f"Text extraction failed for {file_path}: {e}")
        return ""

def index(file_path):
    """Indexes the content of a document in the database."""
    try:
        content = extract_text(file_path)
        
        if not content.strip():
            print(f"No valid content found in {file_path}")
            return

        terms = extract_terms(content)
        if not terms:
            print(f"No valid terms found in {file_path}")
            return

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        # Insert document into the database
        cur.execute("INSERT INTO document (path) VALUES (?)", (file_path,))
        doc_id = cur.lastrowid

        term_counts = {}
        for term in terms:
            term_counts[term] = term_counts.get(term, 0) + 1

        # Insert terms into the database and count occurrences
        for term, count in term_counts.items():
            cur.execute("INSERT OR IGNORE INTO terms (term) VALUES (?)", (term,))
            cur.execute("SELECT id FROM terms WHERE term = ?", (term,))
            term_id = cur.fetchone()[0]

            # Insert term count for document
            cur.execute("INSERT INTO counts (term, document, count) VALUES (?, ?, ?)",
                        (term_id, doc_id, count))

        conn.commit()
        conn.close()
        print(f"Successfully indexed {file_path}")

    except Exception as e:
        print(f"Indexing error: {e}")
