from abc import ABC, abstractmethod
from typing import Any


from pydantic import BaseModel
from typing import Optional


class ExtractionResult(BaseModel):
    text: str = ""
    tables: list = []
    headers: list = []
    paragraphs: list = []
    confidence: float = 0.0
    cost_estimate: float = 0.0
    processing_time_ms: int = 0
    is_escalated: bool = False

class BaseExtractor(ABC):
    @abstractmethod
    def process_page(self, page: Any) -> ExtractionResult:
        pass
