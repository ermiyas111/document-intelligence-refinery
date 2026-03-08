## Confidence Thresholds & Escalation Justification

The confidence thresholds (gate_low, gate_critical) are set based on empirical analysis of the document corpus and the need to minimize false positives in extraction:

- **gate_low (0.85):** Chosen to ensure only high-confidence, text-rich pages are processed by FastTextExtractor. Pages below this threshold are likely to be scanned or structurally complex, requiring escalation.
- **gate_critical (0.40):** Pages with confidence below this are almost always unreadable by local tools and must be escalated to VisionExtractor for robust, multimodal extraction.

These values are dynamically loaded from `rubric/extraction_rules.yaml` and can be tuned as more documents are processed. The escalation logic is validated by unit tests that simulate low-confidence pages and verify correct routing through the strategy chain.
# DOMAIN_NOTES.md

## Strategy Decision Tree (Actual Implementation)

graph TD
    A[Start: Document Ingestion] --> B{Triage Agent}
    
    %% Classification Branch
    B -->|Analyze Metadata/Density| C{Origin Type?}
    
    C -->|Native Digital| D[Assess Layout Complexity]
    C -->|Scanned/Image| E[VisionExtractor Strategy C]
    C -->|Mixed| F[Split Pages]
    
    %% Digital Path
    D -->|Simple/Single Col| G[FastTextExtractor Strategy A]
    D -->|Complex/Tables| H[LayoutExtractor Strategy B]
    
    %% Mixed Path
    F -->|Digital Pages| D
    F -->|Image Pages| E
    
    %% The Escalation Guard (Confidence Gates)
    G --> G_Gate{Confidence?}
    G_Gate -->|>= gate_low| J[Semantic Chunking LDU]
    G_Gate -->|< gate_low| H
    
    H --> H_Gate{Confidence?}
    H_Gate -->|>= gate_critical| J
    H_Gate -->|< gate_critical| K{Budget Guard}
    
    %% Final Escalation
    K -->|Under Cap| E
    K -->|Over Cap| L[Fail & Log to Ledger]
    
    E --> J
    J --> M[PageIndex Builder]

## Observed Failure Modes (From Corpus)
- Most documents are classified as `scanned_image` or `mixed` with very low character density (<< 0.12), triggering VisionExtractor or escalation.
- Financial domain hints are detected in some annual reports (e.g., "Tax Expenditure", "Amortization").
- All documents so far have `single_column` layout; no multi-column or table-heavy detected yet.
- Extraction confidence is often null or low, requiring robust escalation logic.
- Structure collapse and provenance blindness remain risks for scanned and mixed-origin documents.

## Pipeline Diagram (Implemented)
sequenceDiagram
    participant User
    participant Triage as Triage Agent
    participant Router as Extraction Router
    participant Engine as Extraction Engine (A/B/C)
    participant Store as .refinery/ (Ledger & Profiles)
    participant LDU as Semantic Chunking (LDU)
    participant Index as PageIndex & Provenance

    User->>Triage: Submit Document
    Note over Triage: Analyze Density, Fonts, & Images
    Triage->>Store: Save DocumentProfile (JSON)
    Triage->>Router: Hand off Profile + Doc

    rect rgb(240, 240, 240)
        Note right of Router: Escalation Guard Loop
        Router->>Engine: Attempt Strategy A (FastText)
        Engine-->>Router: Low Confidence / Error
        Router->>Store: Log Failure to Ledger
        Router->>Engine: Escalate to Strategy B/C
        Engine-->>Router: High Confidence Success
    end

    Router->>Store: Update Ledger (Final Strategy/Cost)
    Router->>LDU: ExtractedDocument (Normalized)
    
    Note over LDU: Apply "Chunking Constitution" (YAML)
    LDU->>Index: Map LDUs to Spatial Coordinates
    
    Index->>Index: Build Recursive PageIndex Tree

    Index->>QueryAgent: Expose PageIndex Tree
    QueryAgent->>User: Query, Top-Down Navigation, Semantic Search, FactTable Query
    QueryAgent->>Auditor: ProvenanceChain, Audit Mode
    Auditor-->>User: VERIFIED/UNVERIFIABLE with Reasoning
    Index-->>User: Structured Knowledge + Provenance

---

**Escalation Guard Triggers (Current Config):**
- If character density < 0.12, escalate to VisionExtractor.
- If image ratio > 0.35, escalate to VisionExtractor.
- If confidence < 0.85, escalate to LayoutExtractor.
- If confidence < 0.40, escalate to VisionExtractor.

---

## Query Agent & Provenance Layer

- The Query Agent uses a three-tool LangGraph: pageindex_navigate, semantic_search, and structured_query (FactTable).
- Every answer is returned as a Response(answer, citations, verification_status), with citations as a ProvenanceChain (doc_id, page_number, bbox, content_hash).
- The ProvenanceChain enables full auditability: every claim can be traced to its source, and the Auditor can verify or refute user claims with binary output (VERIFIED/UNVERIFIABLE + reasoning).
- FactTable is populated from LDUs and supports structured, temporal queries for financial metrics.
- The PageIndex tree enables top-down, explainable retrieval and query expansion.

*This architecture ensures every model response is anchored in verifiable, auditable source data, supporting both explainable AI and regulatory compliance.*
