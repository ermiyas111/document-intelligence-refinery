from typing import Any
from src.strategies.base import ExtractedDocument

class DoclingDocumentAdapter:
    """
    Adapter to normalize Docling/MinerU output to ExtractedDocument schema.
    """
    @staticmethod
    def normalize(docling_output: Any) -> ExtractedDocument:
        # Map docling_output (tables, headers, paragraphs) to ExtractedDocument
        # Placeholder for actual mapping logic
        return ExtractedDocument()
