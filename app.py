import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re
import spacy
import dateparser
import logging
import json

logging.basicConfig(level=logging.INFO)
nlp = spacy.load("en_core_web_sm")


def extract_text_from_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = '\n'.join(page.extract_text() or '' for page in pdf.pages)
        if text.strip():
            return text, "text"
        else:
            raise Exception("Empty text, using OCR fallback.")
    except:
        images = convert_from_path(pdf_path)
        text = ""
        for image in images:
            text += pytesseract.image_to_string(image)
        return text, "ocr"


def with_conf(value, conf):
    return {"value": value, "confidence": round(conf, 2)} if value else {"value": None, "confidence": 0.0}


def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return with_conf(match.group() if match else None, 0.95 if match else 0.0)

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[\s-]?)?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{4}', text)
    return with_conf(match.group() if match else None, 0.9 if match else 0.0)

def extract_linkedin(text):
    match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9_-]+', text)
    return with_conf(match.group() if match else None, 0.9 if match else 0.0)

def extract_name(text):
    doc = nlp(text.split('\n')[0])
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return with_conf(ent.text, 0.85)
    return with_conf(None, 0.0)

def extract_skills(text, skill_list=None):
    if not skill_list:
        skill_list = ["Python", "Java", "C++", "SQL", "TensorFlow", "Pandas", "Docker", "AWS", "Flask", 
            "JavaScript", "React", "Node.js", "Kubernetes", "MySQL", "MongoDB", "Django", "Git", 
            "Linux", "Azure", "Machine Learning", "Deep Learning", "Data Science", "PyTorch", "HTML", "CSS"]
    found = set()
    for skill in skill_list:
        if re.search(rf'\b{re.escape(skill)}\b', text, re.IGNORECASE):
            found.add(skill)
    return with_conf(list(found), 0.8 if found else 0.0)

def extract_education(text):
    educations = []
    edu_pattern = re.findall(r'(Bachelor|Master|B\.Tech|M\.Tech|BSc|MSc|PhD)[^,\n]*,?\s*(.*?)(\d{4})', text, re.IGNORECASE)
    for degree, inst, year in edu_pattern:
        educations.append({
            "degree": degree.strip(),
            "institution": inst.strip(),
            "year": year
        })
    return with_conf(educations if educations else None, 0.85 if educations else 0.0)

def extract_experience(text):
    experiences = []
    exp_pattern = re.findall(r'(Company|Organization):?\s*(.*?)\n.*?(Role|Title):?\s*(.*?)\n.*?(Duration):?\s*(.*?)(\n|$)', text, re.IGNORECASE)
    for _, company, _, title, _, duration, _ in exp_pattern:
        duration = normalize_duration(duration)
        experiences.append({
            "company": company.strip(),
            "title": title.strip(),
            "duration": duration,
            "description": ""
        })
    return with_conf(experiences if experiences else None, 0.8 if experiences else 0.0)

def normalize_duration(duration):
    parts = re.findall(r'\w+\s+\d{4}', duration)
    parsed = [dateparser.parse(p).strftime('%b %Y') for p in parts if dateparser.parse(p)]
    return ' - '.join(parsed) if parsed else duration

def extract_certifications(text):
    certs = re.findall(r'certified in (.*?)\n', text, re.IGNORECASE)
    return with_conf(certs if certs else None, 0.75 if certs else 0.0)

def extract_projects(text):
    projects = re.findall(r'(Project|Title):?\s*(.*?)\n', text, re.IGNORECASE)
    return with_conf([p[1] for p in projects] if projects else None, 0.75 if projects else 0.0)


def parse_resume(pdf_path):
    text, source = extract_text_from_pdf(pdf_path)
    logging.info(f"Text extracted using: {source}")

    result = {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "linkedin": extract_linkedin(text),
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "certifications": extract_certifications(text),
        "projects": extract_projects(text)
    }

    for k, v in result.items():
        if v["value"] is None:
            logging.warning(f"Missing field: {k}")

    return result


def calculate_overall_confidence(parsed_result):
    total_conf = 0
    count = 0
    for value in parsed_result.values():
        if isinstance(value, dict) and "confidence" in value:
            total_conf += value["confidence"]
            count += 1
    return round(total_conf / count, 2) if count else 0.0


if __name__ == "__main__":
    pdf_file = 'your resume.pdf'
    output = parse_resume(pdf_file)
    overall_conf = calculate_overall_confidence(output)
    output["overall_confidence_score"] = overall_conf
    print(json.dumps(output, indent=2))
