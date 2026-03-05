# Document Intelligence Refinery

## Overview
The Document Intelligence Refinery is a modular, agentic pipeline for extracting structured, queryable data from unstructured enterprise documents (PDFs, scans, reports). It features dynamic triage, multi-strategy extraction, confidence-based escalation, and cost-aware processing for robust, auditable document intelligence at scale.

## Architecture
- **Triage Agent:** Profiles each document (origin type, character density, image ratio, layout, domain hints) and selects the extraction strategy.
- **Extraction Engine:** Implements FastTextExtractor, LayoutExtractor, and VisionExtractor, escalating based on confidence gates and document features.
- **Config Loader:** Loads all thresholds, gates, and budget rules from `rubric/extraction_rules.yaml` for live, code-free tuning.
- **BudgetGuard:** Enforces per-document cost caps and model pricing for LLM/VLM calls.
- **Extraction Ledger:** Logs every extraction attempt (strategy, confidence, cost, escalation) to `.refinery/extraction_ledger.jsonl` for full auditability.

## Key Features
- Dynamic strategy routing based on document profile and confidence scores
- YAML-driven configuration for triage, escalation, chunking, and budget
- Modular extractors with robust error handling and escalation
- Ledger and reporting for cost and pipeline transparency

## Getting Started
1. **Install dependencies:**
	- Use `uv pip install -r uv.lock` or `poetry install` (see `pyproject.toml` and `uv.lock`).
2. **Configure rules:**
	- Edit `rubric/extraction_rules.yaml` to tune thresholds, gates, and budget.
3. **Add documents:**
	- Place PDFs in the `resource/` directory.
4. **Run processing:**
	- `python process_and_log_documents.py` to profile and log all documents.
5. **Review outputs:**
	- Document profiles: `.refinery/Profiles/DocumentProfile.json`
	- Extraction ledger: `.refinery/extraction_ledger.jsonl`
	- Cost report: `python scripts/report_costs.py`

## Testing
- Run `pytest tests/test_triage.py` for full triage, extraction, and budget guard coverage.
- All tests use mocks and config-driven thresholds for reproducibility.

## Configuration Example
See `rubric/extraction_rules.yaml` for triage, confidence, chunking, and budget settings. All pipeline logic is dynamically driven by this file.

## Extensibility
- Add new extractors or domain hints by extending the triage agent and config.
- Tune all thresholds and gates in YAML—no code changes required.

## License
MIT License
