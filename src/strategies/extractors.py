from .base import BaseExtractor, ExtractedDocument


import pdfplumber
import time
import asyncio
from src.strategies.exceptions import LowConfidenceError, BudgetExceededError
from src.strategies.docling_adapter import DoclingDocumentAdapter

class FastTextExtractor(BaseExtractor):
    def extract(self, path: str) -> ExtractedDocument:
        start = time.time()
        with pdfplumber.open(path) as pdf:
            total_chars = 0
            total_area = 0
            font_metadata = set()
            image_area = 0
            for page in pdf.pages:
                text = page.extract_text() or ""
                total_chars += len(text)
                width, height = page.width, page.height
                total_area += width * height
                # font_metadata and image_area are placeholders
                # Actual extraction would require more logic
            char_density = total_chars / total_area if total_area else 0
            confidence = self.calculate_confidence(char_density, font_metadata, image_area, total_area)
            if confidence < 0.6:
                raise LowConfidenceError(f"Low confidence: {confidence}")
            doc = ExtractedDocument(confidence=confidence, processing_time_ms=int((time.time() - start) * 1000))
            return doc

    def calculate_confidence(self, char_density: float, font_metadata: set, image_area: float, total_area: float) -> float:
        score = char_density
        if font_metadata:
            score += 0.2
        if total_area and (image_area / total_area) > 0.5:
            score -= 0.4
        return max(0.0, min(1.0, score))

class LayoutExtractor(BaseExtractor):
    def extract(self, path: str) -> ExtractedDocument:
        # Placeholder for Docling/MinerU integration
        docling_output = {}  # Replace with actual call
        return DoclingDocumentAdapter.normalize(docling_output)


class BudgetGuard:
    def __init__(self, budget_cap_usd: float, model_price_per_token: float):
        self.budget_cap_usd = budget_cap_usd
        self.model_price_per_token = model_price_per_token

    def check_budget(self, input_tokens: int, output_tokens: int):
        cost = (input_tokens + output_tokens) * self.model_price_per_token
        if cost > self.budget_cap_usd:
            raise BudgetExceededError(f"Cost {cost} exceeds cap {self.budget_cap_usd}")
        return cost

class VisionExtractor(BaseExtractor):
    def __init__(self, budget_guard: BudgetGuard):
        self.budget_guard = budget_guard

    async def extract(self, path: str, input_tokens: int = 0, output_tokens: int = 0) -> ExtractedDocument:
        # Placeholder for async OpenRouter API call
        self.budget_guard.check_budget(input_tokens, output_tokens)
        await asyncio.sleep(0.1)  # Simulate async call
        doc = ExtractedDocument(confidence=1.0)
        return doc
