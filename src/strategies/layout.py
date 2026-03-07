from src.strategies.base import BaseExtractor, ExtractionResult
from src.strategies.docling_adapter import DoclingDocumentAdapter

class LayoutExtractor(BaseExtractor):
    def process_page(self, page) -> ExtractionResult:
        # Assume DoclingDocumentAdapter returns a dict with keys: text, tables, headers, paragraphs
        docling_result = DoclingDocumentAdapter.normalize(page)
        return ExtractionResult(**docling_result, is_escalated=True)
