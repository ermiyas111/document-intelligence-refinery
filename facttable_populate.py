import json
from src.db.fact_store import FactStore

# Placeholder: load extracted LDUs from somewhere
ldus_path = '.refinery/ldus.json'
try:
    with open(ldus_path, 'r', encoding='utf-8') as f:
        ldus = json.load(f)
except FileNotFoundError:
    ldus = []

fact_store = FactStore()

for ldu in ldus:
    # Example: parse entity, metric, value, etc. from LDU content
    # This should be replaced with real extraction logic
    fact = {
        'entity': ldu.get('entity', 'Unknown'),
        'metric': ldu.get('metric', 'Unknown'),
        'value': ldu.get('value', 0.0),
        'unit': ldu.get('unit', ''),
        'quarter': ldu.get('quarter', ''),
        'year': ldu.get('year', 0),
        'source_hash': ldu.get('spatial_hash', ''),
        'provenance': json.dumps(ldu.get('provenance', {})),
    }
    fact_store.insert_fact(fact)

print(f"Inserted {len(ldus)} facts into the FactTable.")
