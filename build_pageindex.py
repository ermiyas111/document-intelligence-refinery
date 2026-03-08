import json
from src.engine.indexer import PageIndexBuilder

# Dummy summarizer function (replace with real model call if available)
def summarizer(content):
    return content[:80] + '...' if content else ''

# Load chunked LDUs
ldus_path = '.refinery/ldus.json'
try:
    with open(ldus_path, 'r', encoding='utf-8') as f:
        ldus = json.load(f)
except FileNotFoundError:
    ldus = []

# Group LDUs by document for sectioning (simple example)
doc_structure = {'sections': []}
if ldus:
    doc_map = {}
    for ldu in ldus:
        doc_id = ldu.get('entity', 'Unknown')
        if doc_id not in doc_map:
            doc_map[doc_id] = {'title': doc_id, 'content': '', 'ldus': []}
        doc_map[doc_id]['content'] += ldu.get('content', '')
        doc_map[doc_id]['ldus'].append(ldu)
    doc_structure['sections'] = list(doc_map.values())

builder = PageIndexBuilder(summarizer)
index_root = builder.build_index(doc_structure)

# Serialize to JSON
output_path = '.refinery/pageindex.json'
builder.serialize_index(index_root, output_path)
print(f"PageIndex serialized to {output_path}")
