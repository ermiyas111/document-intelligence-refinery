import sqlite3
from typing import List, Dict, Any

FACT_TABLE_SCHEMA = """
CREATE TABLE IF NOT EXISTS fact_table (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT,
    metric TEXT,
    value REAL,
    unit TEXT,
    quarter TEXT,
    year INTEGER,
    source_hash TEXT,
    provenance TEXT
);
"""

class FactStore:
    def __init__(self, db_path='fact_store.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(FACT_TABLE_SCHEMA)
        self.conn.commit()

    def insert_fact(self, fact: Dict[str, Any]):
        self.conn.execute(
            "INSERT INTO fact_table (entity, metric, value, unit, quarter, year, source_hash, provenance) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                fact['entity'], fact['metric'], fact['value'], fact['unit'],
                fact['quarter'], fact['year'], fact['source_hash'], fact['provenance']
            )
        )
        self.conn.commit()

    def query(self, query_str: str) -> List[Dict[str, Any]]:
        # Placeholder: naive implementation
        cursor = self.conn.execute("SELECT * FROM fact_table WHERE metric LIKE ?", (f"%{query_str}%",))
        return [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]

    def get_value_by_provenance(self, prov) -> Any:
        cursor = self.conn.execute("SELECT value FROM fact_table WHERE source_hash=?", (prov.content_hash,))
        row = cursor.fetchone()
        return row[0] if row else None
