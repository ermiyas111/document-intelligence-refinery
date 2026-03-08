import json
from src.engine.chunker import SemanticChunkingEngine

# Load extracted document profiles
profiles_path = '.refinery/Profiles/DocumentProfile.json'
ldus_path = '.refinery/ldus.json'

try:
    with open(profiles_path, 'r', encoding='utf-8') as f:
        profiles = json.load(f)
except FileNotFoundError:
    profiles = []

chunker = SemanticChunkingEngine()
ldus = []

for profile in profiles:
    # Simulate document extraction (replace with real extraction logic)
    doc = {
        'doc_id': profile.get('file_name', 'unknown'),
        'text': profile.get('text', 'Sample extracted text for LDU generation.')
    }
    chunks = chunker.chunk_document(doc)
    for chunk in chunks:
        # Add dummy fields for FactTable
        ldu = {
            'entity': profile.get('domain_hint', 'Unknown'),
            'metric': 'SampleMetric',
            'value': 123.45,
            'unit': 'USD',
            'quarter': 'Q1',
            'year': 2023,
            'spatial_hash': chunk['spatial_hash'],
            'provenance': {
                'doc_id': doc['doc_id'],
                'position': chunk['position']
            },
            'content': chunk['content']
        }
        ldus.append(ldu)

with open(ldus_path, 'w', encoding='utf-8') as f:
    json.dump(ldus, f, indent=2)

print(f"Generated {len(ldus)} LDUs and saved to {ldus_path}.")
