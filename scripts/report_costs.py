import json
import os

LEDGER_PATH = os.path.join('.refinery', 'extraction_ledger.jsonl')

def main():
    total_cost = 0.0
    doc_count = 0
    if not os.path.exists(LEDGER_PATH):
        print("No extraction ledger found.")
        return
    with open(LEDGER_PATH, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            if 'actual_cost' in entry and entry['actual_cost']:
                total_cost += entry['actual_cost']
                doc_count += 1
    print(f"Total cost for {doc_count} documents: ${total_cost:.4f}")

if __name__ == "__main__":
    main()
