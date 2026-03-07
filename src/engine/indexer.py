import json
from typing import List, Dict, Any

class SectionNode:
    def __init__(self, section_id, title, parent=None):
        self.section_id = section_id
        self.title = title
        self.parent = parent
        self.children = []
        self.summary = None
        self.ldus = []  # Logical Document Units (chunks)

    def add_child(self, child):
        self.children.append(child)

    def to_dict(self):
        return {
            'section_id': self.section_id,
            'title': self.title,
            'summary': self.summary,
            'ldus': self.ldus,
            'children': [c.to_dict() for c in self.children]
        }

class PageIndexBuilder:
    def __init__(self, summarizer):
        self.summarizer = summarizer

    def build_index(self, doc_structure: Dict[str, Any]) -> SectionNode:
        # Traverse doc_structure to build tree
        root = SectionNode('root', 'Document Root')
        for i, section in enumerate(doc_structure.get('sections', [])):
            node = SectionNode(f'section_{i}', section['title'], parent=root)
            node.ldus = section.get('ldus', [])
            node.summary = self.summarizer(section['content'])
            root.add_child(node)
        return root

    @staticmethod
    def serialize_index(root: SectionNode, path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(root.to_dict(), f, indent=2)
