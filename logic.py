import spacy
import re
from pdfminer.high_level import extract_text

# --- 1. CATEGORIZED DATABASE ---
SKILL_DB = {
    "Languages": {
        "python", "java", "c++", "c#", "javascript", "typescript", "html", "css", "sql", "go", "ruby"
    },
    "Frameworks & Libs": {
        "flask", "django", "fastapi", "react", "angular", "node", "vue", "spring", "bootstrap", "tailwind", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch"
    },
    "Tools & Cloud": {
        "git", "docker", "kubernetes", "aws", "azure", "gcp", "jenkins", "jira", "excel", "power bi", "tableau", "linux"
    },
    "Soft Skills": {
        "communication", "teamwork", "leadership", "problem solving", "time management", "agile", "scrum"
    }
}

ALL_DB_SKILLS = set().union(*SKILL_DB.values())

# --- 2. EXPANDED BLACKLIST (The Fix for 72%) ---
BLACKLIST = {
    "job", "title", "role", "description", "requirements", "experience", "education",
    "summary", "profile", "candidate", "work", "history", "university", "college",
    "school", "project", "details", "contact", "email", "phone", "address",
    "year", "years", "month", "months", "date", "day", "application", "resume",
    "cv", "manager", "team", "client", "company", "services", "solutions",
    # NEW GHOST WORDS ADDED:
    'familiarity','knowledge',
    "full", "stack", "developer", "software", "engineer", "technologies", "technical",
    "professional", "intern", "internship", "grade", "bca", "mca", "btech"
}

def load_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

def extract_text_from_pdf(pdf_file):
    try:
        return extract_text(pdf_file)
    except Exception as e:
        return ""

def clean_text(text):
    if not text: return ""
    text = re.sub(r'[^a-zA-Z0-9\s\+\#]', ' ', text)
    return text

def extract_keywords(text, nlp_model):
    found_skills = set()
    
    # --- PHASE 1: DB Lookup ---
    text_lower = text.lower()
    for skill in ALL_DB_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found_skills.add(skill)

    # --- PHASE 2: AI Extraction ---
    doc = nlp_model(text)
    
    for token in doc:
        if token.pos_ == "PROPN" and len(token.text) > 2:
            clean_token = token.text.lower()
            if (clean_token not in found_skills 
                and clean_token not in BLACKLIST
                and not token.is_stop):
                found_skills.add(clean_token)

    return found_skills

def calculate_match(resume_text, jd_text, nlp_model):
    clean_res = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    resume_skills = extract_keywords(clean_res, nlp_model)
    jd_skills = extract_keywords(clean_jd, nlp_model)
    
    # --- DEBUGGING (LOOK AT YOUR TERMINAL) ---
    print("\n" + "="*40)
    print(f"DEBUG: Found {len(jd_skills)} Requirements in JD:")
    print(jd_skills) # <--- THIS WILL SHOW YOU THE GHOSTS
    print("="*40 + "\n")
    # ----------------------------------------
    
    if not jd_skills:
        return 0.0, set()

    intersection = resume_skills.intersection(jd_skills)
    score = (len(intersection) / len(jd_skills)) * 100
    missing = jd_skills - resume_skills
    
    return round(score, 2), missing