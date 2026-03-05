import os
import time
from src.utils.logger import log_extraction_attempt
import json

# Load DocumentProfiles
profile_path = os.path.join('.refinery', 'Profiles', 'DocumentProfile.json')
if not os.path.exists(profile_path):
    print('No DocumentProfile.json found.')
    exit(1)

with open(profile_path, 'r', encoding='utf-8') as f:
    profiles = json.load(f)

# Simulate strategy selection and logging for each profile
def simulate_strategy_and_log(profile):
    doc_id = profile.get('file_name', 'unknown')
    filename = profile.get('file_name', 'unknown')
    # Example logic: select strategy and confidence
    if profile['origin_type'] == 'native_digital' and profile['layout_complexity'] == 'single_column':
        strategy = 'FastTextExtractor'
        confidence = 0.95
        cost = 0.01
    elif profile['origin_type'] == 'scanned_image' or profile['layout_complexity'] == 'table_heavy':
        strategy = 'VisionExtractor'
        confidence = 0.85
        cost = 0.25
    else:
        strategy = 'LayoutExtractor'
        confidence = 0.75
        cost = 0.05
    escalation_count = 0 if strategy == 'FastTextExtractor' else 1
    latency_ms = int(100 + 100 * escalation_count)
    log_extraction_attempt(doc_id, filename, strategy, confidence, escalation_count, cost, latency_ms)

for profile in profiles:
    simulate_strategy_and_log(profile)

print('Ledger entries created for all profiles.')
