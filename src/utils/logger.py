import json
import os
from datetime import datetime

LEDGER_PATH = os.path.join('.refinery', 'extraction_ledger.jsonl')

def log_extraction_attempt(doc_id, filename, strategy_used, confidence_score, escalation_count, actual_cost, latency_ms, error=None):
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'doc_id': doc_id,
        'filename': filename,
        'strategy_used': strategy_used,
        'confidence_score': confidence_score,
        'escalation_count': escalation_count,
        'actual_cost': actual_cost,
        'latency_ms': latency_ms,
        'error': error
    }
    with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
