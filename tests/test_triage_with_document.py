from src.agents.triage import TriageAgent, DocumentProfile
import pdfplumber
import os

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
            # Placeholder: count images and font metadata
            if hasattr(page, 'images'):
                image_count += len(page.images)
            # Placeholder: font metadata and whitespace gaps
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
            domain_hint=domain_hint
        )
        return profile

if __name__ == "__main__":
    pdf_path = os.path.join("resource", "sample.pdf")
    profile = profile_document(pdf_path)
    print(profile.json(indent=2))
