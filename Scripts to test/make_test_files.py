from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def create_pdf(filename, content_list):
    c = canvas.Canvas(filename, pagesize=LETTER)
    y = 750
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, f"Resume: {filename}")
    
    c.setFont("Helvetica", 12)
    for line in content_list:
        c.drawString(50, y, line)
        y -= 20
    c.save()
    print(f"✅ Created {filename}")

# --- 1. THE PERFECT CANDIDATE ---
# Has mostly everything the Job Description wants
perfect_resume = [
    "Name: Alice Coder",
    "Summary: Senior Python Developer",
    "Skills: Python, Django, SQL, React, AWS, Docker, Git.",
    "Experience: Built scalable apps using Flask and PostgreSQL."
]

# --- 2. THE JUNIOR / PARTIAL MATCH ---
# Good, but missing "Advanced" tools (Docker, AWS, React)
partial_resume = [
    "Name: Bob Junior",
    "Summary: Fresh Graduate",
    "Skills: Python, C++, HTML, CSS, SQL, Git.",
    "Experience: College project using Tkinter and SQLite."
]

# --- 3. THE IRRELEVANT CANDIDATE ---
# Has valid skills, but wrong domain (Chef/Management)
bad_resume = [
    "Name: Charlie Chef",
    "Summary: Hotel Management",
    "Skills: Cooking, Teamwork, Time Management, Leadership.",
    "Experience: Head Chef at 5-star hotel."
]

if __name__ == "__main__":
    create_pdf("resume_perfect.pdf", perfect_resume)
    create_pdf("resume_partial.pdf", partial_resume)
    create_pdf("resume_irrelevant.pdf", bad_resume)