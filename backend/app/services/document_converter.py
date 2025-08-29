"""Document conversion service for DOCX <-> HTML conversion"""

import io
import tempfile
import os
from typing import Optional, Tuple
from pathlib import Path

try:
    import mammoth
    from docx import Document
    from html2docx import html2docx
    CONVERSION_AVAILABLE = True
except ImportError:
    CONVERSION_AVAILABLE = False
    print("Warning: Document conversion packages not available. Install: pip install python-docx mammoth html2docx")


class DocumentConverter:
    """Service for converting between DOCX and HTML formats"""

    def __init__(self):
        if not CONVERSION_AVAILABLE:
            raise ImportError("Document conversion packages not available")

    def docx_to_html(self, docx_content: bytes) -> Tuple[str, str]:
        """
        Convert DOCX content to HTML

        Args:
            docx_content: Raw DOCX file content as bytes

        Returns:
            Tuple of (html_content, plain_text)
        """
        try:
            # Create a temporary file for mammoth
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(docx_content)
                temp_file_path = temp_file.name

            try:
                # Convert DOCX to HTML using mammoth
                with open(temp_file_path, 'rb') as docx_file:
                    result = mammoth.convert_to_html(docx_file)
                    html_content = result.value

                    # Also get plain text for Quill
                    text_result = mammoth.extract_raw_text(docx_file)
                    plain_text = text_result.value

                    return html_content, plain_text

            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)

        except Exception as e:
            raise Exception(f"Failed to convert DOCX to HTML: {str(e)}")

    def html_to_docx(self, html_content: str, filename: str = "document.docx") -> bytes:
        """
        Convert HTML content to DOCX

        Args:
            html_content: HTML content as string
            filename: Output filename for the DOCX

        Returns:
            DOCX content as bytes
        """
        try:
            # Convert HTML to DOCX using html2docx
            docx_content = html2docx(html_content, title=filename)

            # Convert to bytes
            docx_bytes = docx_content.read()
            docx_content.seek(0)  # Reset file pointer

            return docx_bytes

        except Exception as e:
            raise Exception(f"Failed to convert HTML to DOCX: {str(e)}")

    def is_docx_file(self, filename: str) -> bool:
        """Check if a file is a DOCX file based on extension"""
        return filename.lower().endswith('.docx')

    def is_html_file(self, filename: str) -> bool:
        """Check if a file is an HTML file based on extension"""
        return filename.lower().endswith(('.html', '.htm'))

    def get_quill_content(self, html_content: str) -> str:
        """
        Convert HTML content to Quill-compatible format
        Quill expects HTML but may need some cleanup
        """
        # Basic HTML cleanup for Quill
        # Remove any script tags for security
        import re
        cleaned_html = re.sub(
            r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)

        # Remove any style tags that might interfere
        cleaned_html = re.sub(
            r'<style[^>]*>.*?</style>', '', cleaned_html, flags=re.IGNORECASE | re.DOTALL)

        return cleaned_html.strip()

    def html_to_quill_delta(self, html_content: str) -> dict:
        """
        Convert HTML to Quill Delta format (if needed)
        For now, we'll return HTML as Quill can handle HTML directly
        """
        # Quill can handle HTML directly, so we return the HTML content
        # wrapped in a Quill-compatible structure
        return {
            "ops": [
                {"insert": html_content}
            ]
        }


# Global instance
document_converter = DocumentConverter() if CONVERSION_AVAILABLE else None
