from flask import Blueprint, request, render_template
import sqlite3
import numpy as np
import os

search_bp = Blueprint("search", __name__)

DATABASE = "db.db"
DOCS_FOLDER = "/static/docs/"  # Base folder for documents

def get_terms_vector(query_terms):
    """Retrieve term vectors from the database securely."""
    if not query_terms:
        return {}, []

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Get term IDs safely
    query_placeholders = ",".join(["?"] * len(query_terms))
    cur.execute(f"SELECT id, term FROM terms WHERE term IN ({query_placeholders})", query_terms)
    term_map = {term: tid for tid, term in cur.fetchall()}

    if not term_map:
        conn.close()
        return {}, []

    term_ids = list(term_map.values())

    # Get document vectors
    query_placeholders = ",".join(["?"] * len(term_ids))
    cur.execute(f"SELECT document, term, count FROM counts WHERE term IN ({query_placeholders})", term_ids)
    
    doc_vectors = {}
    for document, term, count in cur.fetchall():
        if document not in doc_vectors:
            doc_vectors[document] = {}
        doc_vectors[document][term] = count

    conn.close()
    return doc_vectors, term_ids

def euclidean_distance(vec1, vec2):
    """Compute Euclidean distance between two vectors."""
    all_keys = set(vec1.keys()).union(set(vec2.keys()))
    return np.sqrt(sum((vec1.get(k, 0) - vec2.get(k, 0)) ** 2 for k in all_keys))

@search_bp.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return render_template("results.html", query="", results=[])

    query_terms = query.lower().split()
    doc_vectors, query_vector_terms = get_terms_vector(query_terms)

    if not doc_vectors:
        return render_template("results.html", query=query, results=[])

    # Create a query vector (1 for each matching term)
    query_vector = {tid: 1 for tid in query_vector_terms}
    
    # Compute Euclidean distances
    distances = {doc_id: euclidean_distance(query_vector, doc_vec) for doc_id, doc_vec in doc_vectors.items()}
    
    # Sort by closest match (smallest distance)
    sorted_docs = sorted(distances.items(), key=lambda x: x[1])[:10]

    # If no documents were found, return empty results
    if not sorted_docs:
        return render_template("results.html", query=query, results=[])

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Retrieve document paths safely
    doc_ids = [doc_id for doc_id, _ in sorted_docs]
    
    if doc_ids:
        query_placeholders = ",".join(["?"] * len(doc_ids))
        cur.execute(f"SELECT id, path FROM document WHERE id IN ({query_placeholders})", doc_ids)
        doc_paths = {doc_id: doc_path for doc_id, doc_path in cur.fetchall()}
    else:
        doc_paths = {}

    conn.close()

    # Prepare search results
    results = []
    for doc_id, score in sorted_docs:
        if doc_id in doc_paths:
            filename = os.path.basename(doc_paths[doc_id])  # Extract filename only
            results.append({
                "title": filename,
                "url": f"{DOCS_FOLDER}{filename}",
                "score": f"{score:.2f}"
            })

    return render_template("results.html", query=query, results=results)
