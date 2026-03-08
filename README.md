# Document Intelligence Refinery

## Overview
The Document Intelligence Refinery is a modular, agentic pipeline for extracting structured, queryable data from unstructured enterprise documents (PDFs, scans, reports). It features dynamic triage, multi-strategy extraction, confidence-based escalation, and cost-aware processing for robust, auditable document intelligence at scale.

## Architecture
- **Triage Agent:** Profiles each document (origin type, character density, image ratio, layout, domain hints) and selects the extraction strategy.
- **Extraction Engine:** Implements FastTextExtractor, LayoutExtractor, and VisionExtractor, escalating based on confidence gates and document features.
- **Semantic Chunking Engine:** Segments extracted text into logical document units (LDUs) with spatial hashing and validation.
- **PageIndex Builder:** Constructs a hierarchical, searchable tree of document sections, with summaries and vector search integration.
- **FactTable:** Stores structured facts (entity, metric, value, etc.) with provenance for audit and structured queries.
- **Query Agent:** Combines pageindex navigation, semantic search, and structured queries, returning answers with full provenance chains.
- **Provenance & Audit Layer:** Every answer is anchored in verifiable source data, with audit mode for claim verification.
- **Config Loader:** Loads all thresholds, gates, and budget rules from `rubric/extraction_rules.yaml` for live, code-free tuning.
- **BudgetGuard:** Enforces per-document cost caps and model pricing for LLM/VLM calls.
- **Extraction Ledger:** Logs every extraction attempt (strategy, confidence, cost, escalation) to `.refinery/extraction_ledger.jsonl` for full auditability.

## Key Features
- Dynamic strategy routing based on document profile and confidence scores
- YAML-driven configuration for triage, escalation, chunking, and budget
- Modular extractors with robust error handling and escalation
- Semantic chunking and spatial hashing for provenance
- Hierarchical PageIndex for explainable, top-down retrieval
- FactTable for structured, auditable answers
- Query Agent with provenance chain and audit mode
- Ledger and reporting for cost and pipeline transparency


## Getting Started
1. **Install dependencies:**
	- Use `uv pip install -r uv.lock` or `poetry install` (see `pyproject.toml` and `uv.lock`).
2. **Configure rules:**
	- Edit `rubric/extraction_rules.yaml` to tune thresholds, gates, and budget.
3. **Add documents:**
	- Place PDFs in the `resource/` directory.
4. **Run the pipeline:**
	- `python process_and_log_documents.py` to profile and log all documents.
	- `python scripts/generate_ldus.py` to chunk documents into LDUs.
	- `python scripts/facttable_populate.py` to populate the FactTable from LDUs.
	- `python scripts/build_pageindex.py` to build and serialize the PageIndex.
5. **Query and audit:**
	- `python scripts/query_example.py` to run a query and get answers with provenance.
	- `python scripts/benchmark_retrieval.py` to benchmark retrieval methods.
6. **Review outputs:**
	- Document profiles: `.refinery/Profiles/DocumentProfile.json`
	- LDUs: `.refinery/ldus.json`
	- FactTable: `fact_store.db` (SQLite)
	- PageIndex: `.refinery/pageindex.json`
	- Extraction ledger: `.refinery/extraction_ledger.jsonl`
	- Cost report: `python scripts/report_costs.py`

## Testing
- Run `pytest tests/` for full triage, extraction, chunking, escalation, and budget guard coverage.
- All tests use mocks and config-driven thresholds for reproducibility.

## Configuration Example
See `rubric/extraction_rules.yaml` for triage, confidence, chunking, and budget settings. All pipeline logic is dynamically driven by this file.

## Extensibility
- Add new extractors, chunking rules, or domain hints by extending the triage agent, chunker, and config.
- Tune all thresholds and gates in YAML—no code changes required.
- Integrate with real vector DBs or LLM APIs for advanced retrieval and summarization.

## License
MIT License
