from .base import BaseExtractor, ExtractedDocument

class FastTextExtractor(BaseExtractor):
    def extract(self, path: str) -> ExtractedDocument:
        """Use pdfplumber or pypdf for rapid, native text extraction."""
        # Implementation placeholder
        return ExtractedDocument()

class LayoutExtractor(BaseExtractor):
    def extract(self, path: str) -> ExtractedDocument:
        """Use Docling or MinerU to preserve structural integrity."""
        # Implementation placeholder
        return ExtractedDocument()

class VisionExtractor(BaseExtractor):
    def extract(self, path: str) -> ExtractedDocument:
        """Use a VLM for visual OCR on scanned/handwritten documents."""
        # Implementation placeholder
        return ExtractedDocument()
