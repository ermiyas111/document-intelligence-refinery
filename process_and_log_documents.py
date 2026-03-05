import os
import json
import pdfplumber
from src.agents.triage import TriageAgent, DocumentProfile
from src.utils.logger import log_extraction_attempt

def profile_document(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        total_text = ""
        total_area = 0
        image_count = 0
        font_metadata = []
        whitespace_gaps = []
        for page in pdf.pages:
            text = page.extract_text() or ""
            total_text += text
            width, height = page.width, page.height
            total_area += width * height
            if hasattr(page, 'images'):
                image_count += len(page.images)
            font_metadata.append('default')
            whitespace_gaps.append(0)
        char_density = TriageAgent.calculate_character_density(len(total_text), total_area)
        image_ratio = TriageAgent.calculate_image_ratio(0, total_area)
        origin_type = TriageAgent.detect_origin(len(total_text), image_count)
        layout_complexity = TriageAgent.complexity_scorer(font_metadata, whitespace_gaps)
        domain_hint = TriageAgent.keyword_classifier(total_text)
        profile = DocumentProfile(
            origin_type=origin_type,
            character_density=char_density,
            image_ratio=image_ratio,
            layout_complexity=layout_complexity,
            domain_hint=domain_hint,
            page_count=len(pdf.pages)
        )
        return profile

def select_strategy_and_log(profile, file_name):
    # Example logic: select strategy and confidence
    if profile.origin_type == 'native_digital' and profile.layout_complexity == 'single_column':
        strategy = 'FastTextExtractor'
        confidence = 0.95
        cost = 0.01
    elif profile.origin_type == 'scanned_image' or profile.layout_complexity == 'table_heavy':
        strategy = 'VisionExtractor'
        confidence = 0.85
        cost = 0.25
    else:
        strategy = 'LayoutExtractor'
        confidence = 0.75
        cost = 0.05
    escalation_count = 0 if strategy == 'FastTextExtractor' else 1
    latency_ms = int(100 + 100 * escalation_count)
    log_extraction_attempt(file_name, file_name, strategy, confidence, escalation_count, cost, latency_ms)

def main():
    resource_dir = 'resource'
    output_dir = os.path.join('.refinery', 'Profiles')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'DocumentProfile.json')
    profiles = []
    for fname in os.listdir(resource_dir):
        if fname.lower().endswith('.pdf'):
            pdf_path = os.path.join(resource_dir, fname)
            profile = profile_document(pdf_path)
            profile_dict = profile.model_dump()
            profile_dict['file_name'] = fname
            profiles.append(profile_dict)
            select_strategy_and_log(profile, fname)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)
    print(f"Processed and logged {len(profiles)} documents.")

if __name__ == "__main__":
    main()
