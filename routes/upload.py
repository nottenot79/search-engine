import os
import threading
import sqlite3
import magic  # Requires `pip install python-magic`
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.index import index  # Import the indexing function

upload_bp = Blueprint("upload", __name__)

ALLOWED_EXTENSIONS = {"txt", "pdf", "doc", "docx", "odt", "rtf", "xml", "html", "htm", "xlsx", "xls", "ppt", "pptx"}
UPLOAD_FOLDER = "static/docs"

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_valid_document(file_path):
    """Check if a file is a valid document based on MIME type."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return (
        file_type.startswith("text") or
        file_type in [
            "application/pdf", "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.oasis.opendocument.text", "application/rtf", "application/xml",
            "text/html", "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        ]
    )

def async_index(file_path):
    """Runs the indexing function in a separate thread."""
    try:
        index(file_path)
    except Exception as e:
        print(f"Indexing failed: {e}")  # Log the error

@upload_bp.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    try:
        file.save(file_path)

        # Validate the file as a document
        if not is_valid_document(file_path):
            os.remove(file_path)  # Delete the file if invalid
            return jsonify({"error": "Uploaded file is not a valid document"}), 400

        threading.Thread(target=async_index, args=(file_path,), daemon=True).start()  # Run indexing in the background
        return jsonify({"message": "File uploaded successfully", "path": file_path}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500
