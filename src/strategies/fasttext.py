import pdfplumber
import time
from src.strategies.base import BaseExtractor, ExtractionResult
from src.strategies.exceptions import LowConfidenceError
from src.utils.config import RefinerySettings

class FastTextExtractor(BaseExtractor):
    def process_page(self, page) -> ExtractionResult:
        start = time.time()
        text = page.extract_text() or ""
        char_density = len(text) / (page.width * page.height) if page.width and page.height else 0
        font_presence = 1.0 if hasattr(page, 'fonts') and page.fonts else 0.0
        image_ratio = sum(img['width'] * img['height'] for img in getattr(page, 'images', [])) / (page.width * page.height) if hasattr(page, 'images') and page.images else 0.0
        # Confidence formula
        alpha, beta, gamma = 0.7, 0.2, 0.5
        confidence = alpha * char_density + beta * font_presence - gamma * image_ratio
        gate_low = RefinerySettings.get().rules.confidence_gates.gate_low
        if confidence < gate_low:
            raise LowConfidenceError(f"Confidence {confidence:.2f} below gate_low {gate_low}")
        return ExtractionResult(
            text=text,
            confidence=confidence,
            processing_time_ms=int((time.time() - start) * 1000),
            is_escalated=False
        )
