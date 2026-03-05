from typing import List, Optional
from pydantic import BaseModel

class DocumentProfile(BaseModel):
    origin_type: str  # 'native_digital', 'scanned_image', or 'mixed'
    character_density: float
    image_ratio: float
    layout_complexity: str  # 'single_column', 'multi_column', 'table_heavy'
    domain_hint: Optional[str] = None
    extraction_confidence: Optional[float] = None

class TriageAgent:
    @staticmethod
    def calculate_character_density(text_length: int, page_area: float) -> float:
        """Calculate character density as text length divided by page area."""
        if page_area == 0:
            return 0.0
        return text_length / page_area

    @staticmethod
    def calculate_image_ratio(image_area: float, page_area: float) -> float:
        """Calculate image ratio as image area divided by page area."""
        if page_area == 0:
            return 0.0
        return image_area / page_area

    @staticmethod
    def detect_origin(text_length: int, image_count: int) -> str:
        """Classify document origin type."""
        if text_length < 100 and image_count > 0:
            return 'scanned_image'
        elif text_length >= 100 and image_count == 0:
            return 'native_digital'
        else:
            return 'mixed'

    @staticmethod
    def complexity_scorer(font_metadata: List[str], whitespace_gaps: List[float]) -> str:
        """Score layout complexity based on font variety and whitespace gaps."""
        font_variety = len(set(font_metadata))
        avg_gap = sum(whitespace_gaps) / len(whitespace_gaps) if whitespace_gaps else 0
        if font_variety > 3 or avg_gap > 50:
            return 'multi_column'
        elif avg_gap > 100:
            return 'table_heavy'
        else:
            return 'single_column'

    @staticmethod
    def keyword_classifier(text: str) -> Optional[str]:
        """Detect domain hints based on keywords."""
        financial_terms = ["Consolidated Statement", "Amortization", "Tax Expenditure"]
        legal_terms = ["Affidavit", "Deposition", "Indemnity"]
        for term in financial_terms:
            if term.lower() in text.lower():
                return 'financial'
        for term in legal_terms:
            if term.lower() in text.lower():
                return 'legal'
        return None
