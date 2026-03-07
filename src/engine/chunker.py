import hashlib
from typing import List, Dict, Any
from src.utils.config import RefinerySettings
from src.utils.logging_manager import log_event

class ChunkValidator:
    def __init__(self, constitution: Dict[str, Any]):
        self.constitution = constitution

    def validate(self, chunk: Dict[str, Any]) -> bool:
        # Example rules: min_chunk_size, preserve_table_integrity, break_on_headings
        if len(chunk['content']) < self.constitution['min_chunk_size']:
            log_event(chunk.get('doc_id', 'unknown'), 'Chunking', 0.0, 0.0, 0, True)
            return False
        # Add more rules as needed
        return True

class SpatialHasher:
    @staticmethod
    def hash_chunk(chunk: Dict[str, Any]) -> str:
        # Deterministic hash based on content and position
        h = hashlib.sha256()
        h.update(chunk['content'].encode('utf-8'))
        h.update(str(chunk.get('position', 0)).encode('utf-8'))
        return h.hexdigest()

class SemanticChunkingEngine:
    def __init__(self):
        self.rules = RefinerySettings.get().rules.chunking
        self.validator = ChunkValidator({
            'min_chunk_size': self.rules.target_chunk_size_tokens // 4,
            # Add more constitution rules as needed
        })

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Placeholder: simple chunking by length
        content = doc['text']
        size = self.rules.target_chunk_size_tokens
        overlap = self.rules.context_overlap
        chunks = []
        for i in range(0, len(content), size - overlap):
            chunk = {
                'content': content[i:i+size],
                'position': i,
                'doc_id': doc.get('doc_id', 'unknown')
            }
            if self.validator.validate(chunk):
                chunk['spatial_hash'] = SpatialHasher.hash_chunk(chunk)
                chunks.append(chunk)
        return chunks
