import yaml
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import os
from src.agents.triage import DocumentProfile

class TriageThresholds(BaseModel):
    min_character_density: float
    scanned_image_trigger: float

class ConfidenceGates(BaseModel):
    gate_low: float
    gate_critical: float

class ChunkingConfig(BaseModel):
    target_chunk_size_tokens: int
    context_overlap: int
    break_points: List[str]

class BudgetaryGuardrails(BaseModel):
    max_cost_per_doc_usd: float
    model_pricing: Dict[str, float]

class ExtractionRules(BaseModel):
    triage_thresholds: TriageThresholds
    confidence_gates: ConfidenceGates
    chunking: ChunkingConfig
    budgetary_guardrails: BudgetaryGuardrails

class RefinerySettings:
    _instance = None
    _config_path = os.path.join('rubric', 'extraction_rules.yaml')

    def __init__(self):
        with open(self._config_path, 'r') as f:
            data = yaml.safe_load(f)
        self.rules = ExtractionRules(**data)

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_strategy_for_profile(self, profile: DocumentProfile) -> str:
        t = self.rules.triage_thresholds
        g = self.rules.confidence_gates
        # Digital if character_density >= min_character_density
        if profile.character_density >= t.min_character_density and profile.image_ratio < t.scanned_image_trigger:
            if profile.extraction_confidence is not None:
                if profile.extraction_confidence < g.gate_critical:
                    return 'VisionExtractor'
                elif profile.extraction_confidence < g.gate_low:
                    return 'LayoutExtractor'
                else:
                    return 'FastTextExtractor'
            return 'FastTextExtractor'
        elif profile.image_ratio >= t.scanned_image_trigger:
            return 'VisionExtractor'
        else:
            return 'LayoutExtractor'
