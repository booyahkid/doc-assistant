"""
FastAPI application for AI Document Assistant.

This module provides REST API endpoints for document upload and processing.
"""

import os
import uuid
from pathlib import Path
from typing import Dict

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from parser import parse_pdf, parse_docx


# Initialize FastAPI app
app = FastAPI(
    title="AI Document Assistant",
    description="Upload and process PDF/DOCX documents with AI-powered Q&A",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for document metadata
# Format: {document_id: {"filename": str, "filepath": str, "char_count": int}}
documents: Dict[str, Dict[str, any]] = {}

# Configuration
UPLOAD_DIR = Path(__file__).parent / "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
PREVIEW_LENGTH = 300


@app.on_event("startup")
async def startup_event():
    """
    Create uploads directory on application startup if it doesn't exist.
    """
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    print(f" Uploads directory ready: {UPLOAD_DIR}")


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the server is running.

    Returns:
        dict: Status message indicating server is healthy.
    """
    return {"status": "ok"}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and parse a PDF or DOCX document.

    Args:
        file: The uploaded file (PDF or DOCX only).

    Returns:
        dict: Document metadata including:
            - filename: Original filename
            - document_id: Unique identifier (UUID4)
            - char_count: Number of characters in extracted text
            - preview: First 300 characters of extracted text

    Raises:
        HTTPException: 400 if file type is not allowed
        HTTPException: 500 if parsing fails
    """
    # Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{file_ext}' not allowed. Only {', '.join(ALLOWED_EXTENSIONS)} are supported."
        )

    # Generate unique document ID
    document_id = str(uuid.uuid4())

    # Create unique filename to avoid collisions
    safe_filename = f"{document_id}_{file.filename}"
    filepath = UPLOAD_DIR / safe_filename

    try:
        # Save uploaded file
        content = await file.read()
        with open(filepath, "wb") as f:
            f.write(content)

        # Parse document based on extension
        if file_ext == ".pdf":
            extracted_text = parse_pdf(str(filepath))
        elif file_ext == ".docx":
            extracted_text = parse_docx(str(filepath))
        else:
            # Should never reach here due to validation above
            raise HTTPException(status_code=400, detail="Unsupported file type")

        # Calculate character count
        char_count = len(extracted_text)

        # Generate preview (first 300 characters)
        preview = extracted_text[:PREVIEW_LENGTH] if extracted_text else ""

        # Store metadata in memory
        documents[document_id] = {
            "filename": file.filename,
            "filepath": str(filepath),
            "char_count": char_count,
            "extracted_text": extracted_text  # Store full text for later use
        }

        # Return response
        return {
            "filename": file.filename,
            "document_id": document_id,
            "char_count": char_count,
            "preview": preview
        }

    except ValueError as e:
        # Parser raised ValueError (e.g., file not found)
        raise HTTPException(status_code=500, detail=f"Parsing error: {str(e)}")
    except Exception as e:
        # Catch any other errors during parsing
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
