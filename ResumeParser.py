import os
import spacy
import json
import webbrowser
from collections import defaultdict
from PyPDF2 import PdfReader


class ResumeParser:
    def __init__(self, skill_set):
        self.text = ""
        self.skill_set = set(skill_set)  

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF and clean it."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File not found: {pdf_path}")
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            self.text = " ".join([page.extract_text() or "" for page in reader.pages])
        self.text = self.text.replace('\n', ' ')
        return self.text.strip()

    def extract_entities(self):
        """Extracts PERSON and SKILLS from the resume."""
        nlp = self.load_spacy_model()
        doc = nlp(self.text)

        entities = defaultdict(list)

        # Extract PERSON (name) entities
        for ent in doc.ents:
            if ent.label_ == "PERSON" :
                entities[ent.label_].append(ent.text)

        # Extract SKILLS based on the provided skill set
        found_skills = set()
        lower_text = self.text.lower()
        for skill in self.skill_set:
            if skill.lower() in lower_text:
                found_skills.add(skill)

        entities["SKILLS"] = list(found_skills)
        return dict(entities)

    def load_spacy_model(self):
        """Load SpaCy model for NER."""
        try:
            return spacy.load("en_core_web_lg")
        except OSError:
            from spacy.cli import download
            download("en_core_web_lg")
            return spacy.load("en_core_web_lg")


def process_resumes(resume_paths, skill_set):
    """Process each resume and calculate skill matching scores."""
    results = []

    parser = ResumeParser(skill_set)

    for resume_path in resume_paths:
        print(f"Processing {resume_path}...")

        # Extract text from PDF
        resume_text = parser.extract_text_from_pdf(resume_path)
        extracted_data = parser.extract_entities()

        # Extracted person name and skills
        person_names = extracted_data.get("PERSON", [])
        skills = extracted_data.get("SKILLS", [])

        # Calculate matching score
        skill_match_score = len(skills)
        
        # Store result for each resume
        results.append({
            "Resume": resume_path,
            "Names": person_names,
            "Matched Skills": skills,
            "Skill Match Score": skill_match_score
        })

    return results


if __name__ == "__main__":
    # Input: Multiple resume files (you can replace with actual paths)
    resume_paths = [
        "C:/Users/lenovo/Desktop/PPP/Eya-Khlifi-Resume.pdf", 
        "C:/Users/lenovo/Desktop/PPP/Eya-Khlifi-CV.pdf"
    ]

    # Input: Dynamic skill set (can be adjusted)
    skill_set = ["python", "java", "html", "css", "javascript", "machine learning", "tensorflow", "docker"]

    # Process the resumes
    results = process_resumes(resume_paths, skill_set)

    # Output: Display results and save to JSON
    output_json = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resume_match_results.json")
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)

    print(f"Resume processing complete. Results saved to: {output_json}")
    webbrowser.open(f"file://{os.path.abspath(output_json)}")
