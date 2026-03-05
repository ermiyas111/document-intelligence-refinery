import pytest
from unittest.mock import patch, MagicMock
from src.agents.triage import TriageAgent, DocumentProfile
from src.strategies.extractors import FastTextExtractor
from src.utils.config import RefinerySettings
from src.utils.budget import BudgetGuard
from src.strategies.exceptions import BudgetExceededError, LowConfidenceError

# 1. Mock Document Factory
class MockPDF:
    def __init__(self, kind):
        if kind == 'digital':
            self.text_length = 5000
            self.page_area = 1000 * 1000
            self.image_count = 0
            self.font_metadata = ['Arial', 'Arial', 'Arial']
            self.whitespace_gaps = [10, 12, 8]
            self.text = 'A' * 5000
            self.image_area = 0
        elif kind == 'scanned':
            self.text_length = 0
            self.page_area = 1000 * 1000
            self.image_count = 5
            self.font_metadata = [None]
            self.whitespace_gaps = [5, 5, 5]
            self.text = ''
            self.image_area = 800 * 1000
        elif kind == 'complex_table':
            self.text_length = 2000
            self.page_area = 1000 * 1000
            self.image_count = 0
            self.font_metadata = ['Arial', 'Times', 'Courier']
            self.whitespace_gaps = [120, 130, 110]
            self.text = 'Table' * 400
            self.image_area = 0
        else:
            raise ValueError('Unknown kind')

# 2. Triage Classification Tests
@pytest.mark.parametrize('kind,expected_origin', [
    ('digital', 'native_digital'),
    ('scanned', 'scanned_image'),
    ('complex_table', 'native_digital'),
])
def test_origin_detection(kind, expected_origin):
    mock = MockPDF(kind)
    origin = TriageAgent.detect_origin(mock.text_length, mock.image_count)
    assert origin == expected_origin

@pytest.mark.parametrize('kind,expected_layout', [
    ('digital', 'single_column'),
    ('scanned', 'single_column'),
    ('complex_table', 'multi_column'),
])
def test_layout_complexity(kind, expected_layout):
    mock = MockPDF(kind)
    layout = TriageAgent.complexity_scorer(mock.font_metadata, mock.whitespace_gaps)
    if kind == 'complex_table':
        assert layout in ['multi_column', 'table_heavy']
    else:
        assert layout == expected_layout

def test_domain_hinting():
    text = "This is a Tax Expenditure and Amortization report."
    hint = TriageAgent.keyword_classifier(text)
    assert hint == 'financial'

# 3. Confidence Scoring Tests
@pytest.mark.parametrize('kind,expected_min_conf', [
    ('digital', 0.90),
    ('scanned', 0.0),
])
def test_fasttext_confidence(kind, expected_min_conf):
    mock = MockPDF(kind)
    extractor = FastTextExtractor()
    char_density = TriageAgent.calculate_character_density(mock.text_length, mock.page_area)
    confidence = extractor.calculate_confidence(char_density, set(mock.font_metadata), mock.image_area, mock.page_area)
    if kind == 'digital':
        assert confidence > expected_min_conf
    else:
        assert confidence < RefinerySettings.get().rules.confidence_gates.gate_low

def test_escalation_trigger():
    mock = MockPDF('scanned')
    extractor = FastTextExtractor()
    char_density = TriageAgent.calculate_character_density(mock.text_length, mock.page_area)
    confidence = extractor.calculate_confidence(char_density, set(mock.font_metadata), mock.image_area, mock.page_area)
    assert confidence < RefinerySettings.get().rules.confidence_gates.gate_low

@patch('src.strategies.extractors.FastTextExtractor.extract')
@patch('src.strategies.extractors.LayoutExtractor.extract')
@pytest.mark.asyncio
def test_router_escalation(mock_layout_extract, mock_fasttext_extract):
    from src.agents.extractor import ExtractionRouter
    profile = DocumentProfile(
        origin_type='native_digital',
        character_density=0.5,
        image_ratio=0.1,
        layout_complexity='single_column',
        extraction_confidence=0.2
    )
    mock_fasttext_extract.side_effect = LowConfidenceError()
    mock_layout_extract.return_value = MagicMock(confidence=0.8)
    router = ExtractionRouter()
    result = pytest.run(asyncio.run(router.route(profile, 'dummy.pdf')))
    assert mock_layout_extract.called

# 4. Budget Guard Tests

def test_budget_blocker():
    guard = BudgetGuard(model_name='gpt-4o')
    with pytest.raises(BudgetExceededError):
        guard.check_budget(page_count=1000)
