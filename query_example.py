import json
from src.agents.query_agent import QueryAgent
from src.engine.indexer import SectionNode
from src.db.fact_store import FactStore

# Load PageIndex from JSON
def load_section_node(d):
    node = SectionNode(d['section_id'], d['title'])
    node.summary = d.get('summary')
    node.ldus = d.get('ldus', [])
    node.children = [load_section_node(child) for child in d.get('children', [])]
    return node

with open('.refinery/pageindex.json', 'r', encoding='utf-8') as f:
    index_dict = json.load(f)
page_index = load_section_node(index_dict)

vector_db = None  # Replace with your vector DB if available
fact_table = FactStore()  # Uses default fact_store.db

agent = QueryAgent(page_index, vector_db, fact_table)
response = agent.run("What was the revenue growth?")
print(response)