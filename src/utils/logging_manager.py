import json
import os
from datetime import datetime

LEDGER_PATH = os.path.join('.refinery', 'extraction_ledger.jsonl')

def log_event(doc_id, strategy_used, confidence_score, cost_estimate, processing_time_ms, is_escalated):
    entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'doc_id': doc_id,
        'strategy_used': strategy_used,
        'confidence_score': confidence_score,
        'cost_estimate': cost_estimate,
        'processing_time_ms': processing_time_ms,
        'is_escalated': is_escalated
    }
    with open(LEDGER_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')
