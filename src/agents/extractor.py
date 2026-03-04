from typing import Type
from pydantic import BaseModel
from src.agents.triage import DocumentProfile

import os
import json
import asyncio
import time
from src.strategies.extractors import FastTextExtractor, LayoutExtractor, VisionExtractor, BaseExtractor, BudgetGuard
from src.strategies.exceptions import LowConfidenceError, BudgetExceededError

class ExtractionRouter:
    """
    Routes document extraction to the appropriate strategy based on the DocumentProfile.
    Escalates to more advanced extractors if confidence is low.
    Logs extraction attempts to .refinery/extraction_ledger.jsonl
    """
    def __init__(self, config=None):
        # Load config.yaml if not provided
        import yaml
        if config is None:
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
        self.fast_text = FastTextExtractor()
        self.layout = LayoutExtractor()
        self.budget_guard = BudgetGuard(
            budget_cap_usd=config.get('budget_cap_usd', 2.0),
            model_price_per_token=config.get('model_price_per_token', 0.00002)
        )
        self.vision = VisionExtractor(self.budget_guard)
        self.confidence_thresholds = config.get('confidence_thresholds', {'fast_text': 0.6, 'layout': 0.7, 'vision': 0.8})
        self.ledger_path = os.path.join('.refinery', 'extraction_ledger.jsonl')

    def log_attempt(self, doc_id, strategy, confidence, cost, processing_time, escalation):
        entry = {
            'doc_id': doc_id,
            'strategy_used': strategy,
            'confidence_score': confidence,
            'cost_estimate': cost,
            'processing_time_ms': processing_time,
            'escalation_triggered': escalation
        }
        with open(self.ledger_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    async def route(self, profile: DocumentProfile, path: str, input_tokens: int = 0, output_tokens: int = 0):
        doc_id = getattr(profile, 'doc_id', os.path.basename(path))
        # Try FastTextExtractor
        try:
            start = time.time()
            doc = self.fast_text.extract(path)
            confidence = doc.confidence or 0.0
            cost = 0.0
            escalation = False
            if confidence < self.confidence_thresholds['fast_text']:
                raise LowConfidenceError()
            doc.doc_id = doc_id
            doc.escalation_triggered = escalation
            doc.cost_estimate = cost
            doc.processing_time_ms = int((time.time() - start) * 1000)
            self.log_attempt(doc_id, 'FastTextExtractor', confidence, cost, doc.processing_time_ms, escalation)
            return doc
        except LowConfidenceError:
            escalation = True
            self.log_attempt(doc_id, 'FastTextExtractor', 0.0, 0.0, 0, escalation)
        # Try LayoutExtractor
        try:
            start = time.time()
            doc = self.layout.extract(path)
            confidence = doc.confidence or 0.0
            cost = 0.0
            if confidence < self.confidence_thresholds['layout']:
                raise LowConfidenceError()
            doc.doc_id = doc_id
            doc.escalation_triggered = escalation
            doc.cost_estimate = cost
            doc.processing_time_ms = int((time.time() - start) * 1000)
            self.log_attempt(doc_id, 'LayoutExtractor', confidence, cost, doc.processing_time_ms, escalation)
            return doc
        except LowConfidenceError:
            escalation = True
            self.log_attempt(doc_id, 'LayoutExtractor', 0.0, 0.0, 0, escalation)
        # Try VisionExtractor (async)
        try:
            start = time.time()
            doc = await self.vision.extract(path, input_tokens, output_tokens)
            confidence = doc.confidence or 0.0
            cost = self.budget_guard.model_price_per_token * (input_tokens + output_tokens)
            doc.doc_id = doc_id
            doc.escalation_triggered = escalation
            doc.cost_estimate = cost
            doc.processing_time_ms = int((time.time() - start) * 1000)
            self.log_attempt(doc_id, 'VisionExtractor', confidence, cost, doc.processing_time_ms, escalation)
            return doc
        except BudgetExceededError:
            self.log_attempt(doc_id, 'VisionExtractor', 0.0, 0.0, 0, True)
            raise
