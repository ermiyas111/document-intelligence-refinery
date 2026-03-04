from typing import Type
from pydantic import BaseModel
from src.agents.triage import DocumentProfile
from src.strategies.extractors import FastTextExtractor, LayoutExtractor, VisionExtractor, BaseExtractor

class ExtractionRouter:
    """
    Routes document extraction to the appropriate strategy based on the DocumentProfile.
    Escalates to more advanced extractors if confidence is low.
    """
    def __init__(self):
        self.fast_text = FastTextExtractor()
        self.layout = LayoutExtractor()
        self.vision = VisionExtractor()

    def route(self, profile: DocumentProfile, path: str):
        if profile.origin_type == 'native_digital' and profile.layout_complexity == 'single_column':
            result = self.fast_text.extract(path)
            if profile.extraction_confidence is not None and profile.extraction_confidence < 0.85:
                return self.layout.extract(path)
            return result
        elif profile.origin_type == 'scanned_image' or profile.layout_complexity == 'table_heavy':
            return self.vision.extract(path)
        else:
            return self.layout.extract(path)
