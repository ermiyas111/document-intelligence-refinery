from abc import ABC, abstractmethod
from typing import Any

class ExtractedDocument:
    # Placeholder for extracted document structure
    pass

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, path: str) -> ExtractedDocument:
        """Extract structured data from the document at the given path."""
        pass
