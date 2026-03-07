import pytest
from unittest.mock import MagicMock, patch
from src.strategies.fasttext import FastTextExtractor
from src.strategies.layout import LayoutExtractor
from src.strategies.vision import OpenRouterVisionExtractor
from src.strategies.exceptions import LowConfidenceError, BudgetExceededError
from src.utils.budget_guard import BudgetGuard
from src.utils.config import RefinerySettings

class DummyPage:
    def __init__(self, text, width, height, fonts=None, images=None):
        self._text = text
        self.width = width
        self.height = height
        self.fonts = fonts or []
        self.images = images or []
    def extract_text(self):
        return self._text

@pytest.mark.parametrize('text,fonts,images,expected_conf', [
    ("A"*5000, ['Arial'], [], True),  # Digital, high confidence
    ("", [], [{'width': 800, 'height': 1000}], False),  # Scanned, low confidence
])
def test_fasttext_confidence(text, fonts, images, expected_conf):
    page = DummyPage(text, 1000, 1000, fonts, images)
    extractor = FastTextExtractor()
    if expected_conf:
        result = extractor.process_page(page)
        assert result.confidence > RefinerySettings.get().rules.confidence_gates.gate_low
    else:
        with pytest.raises(LowConfidenceError):
            extractor.process_page(page)

def test_budget_guard_block():
    guard = BudgetGuard()
    with pytest.raises(BudgetExceededError):
        guard.check_and_update('gpt-4o', tokens=200000)  # Large token count

@patch('src.strategies.layout.LayoutExtractor.process_page')
def test_escalation_logic(mock_layout):
    # Simulate FastTextExtractor raising LowConfidenceError, LayoutExtractor returns result
    page = DummyPage("", 1000, 1000, [], [{'width': 800, 'height': 1000}])
    fasttext = FastTextExtractor()
    layout = LayoutExtractor()
    mock_layout.return_value = MagicMock(confidence=0.8, is_escalated=True)
    try:
        fasttext.process_page(page)
    except LowConfidenceError:
        result = layout.process_page(page)
        assert result.is_escalated
