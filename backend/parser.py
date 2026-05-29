"""
Document parsing utilities for the AI Document Assistant.

This module provides functions to extract text from PDF and DOCX files.
"""

import os
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document


def parse_pdf(filepath: str) -> str:
    """
    Extract all text from a PDF file.

    Args:
        filepath: Path to the PDF file to parse.

    Returns:
        Full document text as a single string with pages concatenated.

    Raises:
        ValueError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise ValueError(f"File not found: {filepath}")

    # Open the PDF
    doc = fitz.open(filepath)

    # Extract text from all pages
    text_parts = []
    for page in doc:
        text = page.get_text()
        if text:  # Only add non-empty pages
            text_parts.append(text)

    doc.close()

    # Handle empty documents gracefully
    if not text_parts:
        return ""

    # Concatenate all pages with newline separator
    return "\n".join(text_parts)


def parse_docx(filepath: str) -> str:
    """
    Extract all text from a DOCX file.

    Args:
        filepath: Path to the DOCX file to parse.

    Returns:
        Full document text as a single string with paragraphs joined by newlines.

    Raises:
        ValueError: If the file does not exist.
    """
    if not os.path.exists(filepath):
        raise ValueError(f"File not found: {filepath}")

    # Open the DOCX document
    doc = Document(filepath)

    # Extract all paragraphs
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]

    # Handle empty documents gracefully
    if not paragraphs:
        return ""

    # Join paragraphs with newline separator
    return "\n".join(paragraphs)
