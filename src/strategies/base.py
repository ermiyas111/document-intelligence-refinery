from abc import ABC, abstractmethod
from typing import Any


from pydantic import BaseModel
from typing import Optional

class ExtractedDocument(BaseModel):
    doc_id: Optional[str] = None
    text: Optional[str] = None
    tables: Optional[list] = None
    headers: Optional[list] = None
    paragraphs: Optional[list] = None
    confidence: Optional[float] = None
    cost_estimate: Optional[float] = None
    processing_time_ms: Optional[int] = None
    escalation_triggered: Optional[bool] = None

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, path: str) -> ExtractedDocument:
        """Extract structured data from the document at the given path."""
        pass
