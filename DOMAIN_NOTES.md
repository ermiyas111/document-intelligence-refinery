# DOMAIN_NOTES.md

## Strategy Decision Tree (Actual Implementation)

```mermaid
graph TD
    A[Start: Document Ingestion] --> B{Origin Type Detection}
    B -->|Digital PDF| C[Assess Layout Complexity]
    B -->|Scanned Image| F[VisionExtractor]
    B -->|Mixed| G[Page-wise Assessment]
    C -->|Single Column| D[FastTextExtractor]
    C -->|Multi-Column/Table-Heavy| E[LayoutExtractor]
    G -->|Digital Page| D
    G -->|Image Page| F
    D --> H{Confidence Gate}
    E --> H
    H -->|< gate_critical| F
    H -->|< gate_low| E
    H -->|>= gate_low| I[Chunking]
    F --> I
```

## Observed Failure Modes (From Corpus)
- Most documents are classified as `scanned_image` or `mixed` with very low character density (<< 0.12), triggering VisionExtractor or escalation.
- Financial domain hints are detected in some annual reports (e.g., "Tax Expenditure", "Amortization").
- All documents so far have `single_column` layout; no multi-column or table-heavy detected yet.
- Extraction confidence is often null or low, requiring robust escalation logic.
- Structure collapse and provenance blindness remain risks for scanned and mixed-origin documents.

## Pipeline Diagram (Implemented)
```mermaid
sequenceDiagram
    participant User
    participant TriageAgent
    participant ExtractionLayer
    participant ChunkingEngine
    participant ProvenanceBuilder
    participant PageIndexBuilder
    User->>TriageAgent: Submit document
    TriageAgent->>ExtractionLayer: Profile & route (origin/layout/confidence)
    ExtractionLayer->>ChunkingEngine: Extract structure/content
    ChunkingEngine->>ProvenanceBuilder: Chunk and attach metadata
    ProvenanceBuilder->>PageIndexBuilder: Build navigation index
    PageIndexBuilder->>User: Provide queryable output
```

---

**Escalation Guard Triggers (Current Config):**
- If character density < 0.12, escalate to VisionExtractor.
- If image ratio > 0.35, escalate to VisionExtractor.
- If confidence < 0.85, escalate to LayoutExtractor.
- If confidence < 0.40, escalate to VisionExtractor.

*Thresholds and gates are dynamically loaded from rubric/extraction_rules.yaml and can be tuned without code changes.*
