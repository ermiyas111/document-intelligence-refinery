from typing import Type
from pydantic import BaseModel
from src.agents.triage import DocumentProfile


import os
import json
import asyncio
import time
from src.strategies.extractors import FastTextExtractor, LayoutExtractor, VisionExtractor, BaseExtractor
from src.strategies.exceptions import LowConfidenceError, BudgetExceededError
from src.utils.budget import BudgetGuard
from src.utils.logger import log_extraction_attempt

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
        # Use BudgetGuard from utils (model_name can be parameterized)
        self.budget_guard = BudgetGuard(model_name='gpt-4o')
        self.vision = VisionExtractor(self.budget_guard)
        self.confidence_thresholds = config.get('confidence_thresholds', {'fast_text': 0.6, 'layout': 0.7, 'vision': 0.8})

    # Remove log_attempt; use log_extraction_attempt from utils.logger

    async def route(self, profile: DocumentProfile, path: str, input_tokens: int = 0, output_tokens: int = 0):
        doc_id = getattr(profile, 'doc_id', os.path.basename(path))
        filename = os.path.basename(path)
        escalation_count = 0
        error = None
        # Try FastTextExtractor
        try:
            start = time.time()
            doc = self.fast_text.extract(path)
            confidence = doc.confidence or 0.0
            cost = 0.0
            if confidence < self.confidence_thresholds['fast_text']:
                raise LowConfidenceError()
            doc.doc_id = doc_id
            doc.cost_estimate = cost
            doc.processing_time_ms = int((time.time() - start) * 1000)
            log_extraction_attempt(doc_id, filename, 'FastTextExtractor', confidence, escalation_count, cost, doc.processing_time_ms, error)
            return doc
        except LowConfidenceError as e:
            escalation_count += 1
            error = str(e)
            log_extraction_attempt(doc_id, filename, 'FastTextExtractor', 0.0, escalation_count, 0.0, 0, error)
        # Try LayoutExtractor
        try:
            start = time.time()
            doc = self.layout.extract(path)
            confidence = doc.confidence or 0.0
            cost = 0.0
            if confidence < self.confidence_thresholds['layout']:
                raise LowConfidenceError()
            doc.doc_id = doc_id
            doc.cost_estimate = cost
            doc.processing_time_ms = int((time.time() - start) * 1000)
            log_extraction_attempt(doc_id, filename, 'LayoutExtractor', confidence, escalation_count, cost, doc.processing_time_ms, error)
            return doc
        except LowConfidenceError as e:
            escalation_count += 1
            error = str(e)
            log_extraction_attempt(doc_id, filename, 'LayoutExtractor', 0.0, escalation_count, 0.0, 0, error)
        # Try VisionExtractor (async)
        try:
            start = time.time()
            # Estimate cost using BudgetGuard before extraction
            page_count = getattr(profile, 'page_count', 1)
            try:
                cost = self.budget_guard.check_budget(page_count)
            except BudgetExceededError as e:
                error = str(e)
                log_extraction_attempt(doc_id, filename, 'VisionExtractor', 0.0, escalation_count + 1, 0.0, 0, error)
                raise
            doc = await self.vision.extract(path, input_tokens, output_tokens)
            confidence = doc.confidence or 0.0
            doc.doc_id = doc_id
            doc.cost_estimate = cost
            doc.processing_time_ms = int((time.time() - start) * 1000)
            log_extraction_attempt(doc_id, filename, 'VisionExtractor', confidence, escalation_count, cost, doc.processing_time_ms, error)
            return doc
        except BudgetExceededError as e:
            error = str(e)
            log_extraction_attempt(doc_id, filename, 'VisionExtractor', 0.0, escalation_count + 1, 0.0, 0, error)
            raise
