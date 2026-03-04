import pytest
from src.agents.triage import TriageAgent, DocumentProfile
from src.agents.extractor import ExtractionRouter

class DummyExtractor:
    def extract(self, path: str):
        return f"Extracted from {path}"

def make_profile(origin, layout, confidence=1.0):
    return DocumentProfile(
        origin_type=origin,
        character_density=0.5,
        image_ratio=0.1,
        layout_complexity=layout,
        domain_hint=None,
        extraction_confidence=confidence
    )

def test_digital_single_column():
    profile = make_profile('native_digital', 'single_column', 0.9)
    router = ExtractionRouter()
    result = router.route(profile, 'digital.pdf')
    assert result is not None

def test_scanned_image():
    profile = make_profile('scanned_image', 'single_column', 0.9)
    router = ExtractionRouter()
    result = router.route(profile, 'scanned.pdf')
    assert result is not None

def test_complex_table():
    profile = make_profile('native_digital', 'table_heavy', 0.8)
    router = ExtractionRouter()
    result = router.route(profile, 'complex_table.pdf')
    assert result is not None

def test_low_confidence_escalation():
    profile = make_profile('native_digital', 'single_column', 0.7)
    router = ExtractionRouter()
    result = router.route(profile, 'low_confidence.pdf')
    assert result is not None
