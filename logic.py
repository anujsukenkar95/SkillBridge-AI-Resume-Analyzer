import spacy
import re
from pdfminer.high_level import extract_text
from sentence_transformers import SentenceTransformer, util

# Load NLP Models (This runs once when the app starts)
nlp = spacy.load("en_core_web_sm")
print("Loading Semantic Brain...")
semantic_model = SentenceTransformer('all-MiniLM-L6-v2')

# ... (Keep your existing SKILL_DB and BLACKLIST here) ...


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

def rescue_missing_skills(missing_skills, resume_text):
    """Uses Deep Learning to check if a missing skill is described contextually."""
    rescued_skills = set()
    
    # 1. Split resume into actual sentences using SpaCy
    doc = nlp(resume_text)
    resume_sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
    
    if not resume_sentences or not missing_skills:
        return rescued_skills
        
    # 2. Convert all resume sentences to math vectors at once (fast!)
    sentence_vectors = semantic_model.encode(resume_sentences)
    
    # 3. Check each missing skill
    for skill in missing_skills:
        skill_vector = semantic_model.encode(skill)
        
        # Calculate cosine similarity between the skill and ALL sentences
        scores = util.cos_sim(skill_vector, sentence_vectors)[0]
        
        # If the highest score is > 0.35, the candidate actually has the skill!
        best_score = max(scores).item()
        if best_score > 0.35:
            rescued_skills.add(skill)
            
    return rescued_skills

def calculate_match(resume_text, jd_text, nlp_model):
    clean_res = clean_text(resume_text)
    clean_jd = clean_text(jd_text)
    
    resume_skills = extract_keywords(clean_res, nlp_model)
    jd_skills = extract_keywords(clean_jd, nlp_model)
    
    # --- DEBUGGING (LOOK AT YOUR TERMINAL) ---
    print("\n" + "="*40)
    print(f"DEBUG: Found {len(jd_skills)} Requirements in JD:")
    print(jd_skills) 
    print("="*40 + "\n")
    # ----------------------------------------
    
    if not jd_skills:
        return 0.0, set()

    # 1. Find initial missing skills (Keyword Matcher)
    missing = jd_skills - resume_skills
    
    # --- 2. THE AI RESCUE MISSION (Semantic Search) ---
    print(f"DEBUG: Sending {len(missing)} missing skills to AI for context check...")
    # Note: We pass the raw 'resume_text' so the AI can read full sentences with punctuation
    rescued_skills = rescue_missing_skills(missing, resume_text) 
    
    if rescued_skills:
        print(f"DEBUG: AI Successfully Rescued: {rescued_skills}")
        # Add rescued skills to candidate's profile
        resume_skills.update(rescued_skills)
        # Remove them from the missing list
        missing = missing - rescued_skills
    # --------------------------------------------------
    
    # 3. Calculate Final Score (With Rescued Points!)
    intersection = resume_skills.intersection(jd_skills)
    score = (len(intersection) / len(jd_skills)) * 100
    
    return round(score, 2), missing

def extract_personal_info(text, nlp_model):
    """Extracts Name, Email, and Phone Number from the resume text."""
    info = {"Name": "Not Found", "Email": "Not Found", "Phone": "Not Found"}
    
    # 1. Extract Email
    email_match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    if email_match:
        info["Email"] = email_match.group(0)
        
    # 2. Extract Phone 
    phone_match = re.search(r'\b(?:\+?\d{1,3}[-\s]?)?\d{10}\b', text)
    if phone_match:
        info["Phone"] = phone_match.group(0)
        
    # 3. Extract Name (Using SpaCy)
    doc = nlp_model(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON" and len(ent.text.split()) >= 2: 
            info["Name"] = ent.text.title() 
            break 
                
    return info