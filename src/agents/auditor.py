from typing import List
from pydantic import BaseModel

class ProvenanceChain(BaseModel):
    doc_id: str
    page_number: int
    bbox: str
    content_hash: str

class AuditResult(BaseModel):
    claim: str
    verification_status: str
    reasoning: str

class Auditor:
    def __init__(self, fact_table):
        self.fact_table = fact_table

    def audit(self, claim: str, provenance_chain: List[ProvenanceChain]) -> AuditResult:
        # For each provenance, extract value from fact table
        for prov in provenance_chain:
            value = self.fact_table.get_value_by_provenance(prov)
            if value and str(value) in claim:
                return AuditResult(claim=claim, verification_status="VERIFIED", reasoning="Claim matches extracted value.")
        return AuditResult(claim=claim, verification_status="UNVERIFIABLE", reasoning="No matching value found in provenance.")
