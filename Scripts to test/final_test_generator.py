from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def create_pdf(filename, name, role, skills, summary):
    c = canvas.Canvas(filename, pagesize=LETTER)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, f"Name: {name}")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 730, f"Target Role: {role}")
    
    # Content
    c.setFont("Helvetica", 12)
    y = 700
    
    c.drawString(50, y, "Professional Summary:")
    c.drawString(50, y-20, summary)
    
    y -= 60
    c.drawString(50, y, "Technical Skills:")
    # We list skills clearly to test the extractor
    c.drawString(50, y-20, skills)
    
    c.save()
    print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    # 1. THE PERFECT MATCH (For Full Stack Developer)
    create_pdf(
        "test_1_perfect.pdf",
        "Alice Coder",
        "Full Stack Developer",
        "Python, Django, React, SQL, AWS, Docker, Git, Linux.",
        "Experienced developer proficient in Python backend and React frontend."
    )

    # 2. THE 50% GAP CANDIDATE (For Data Scientist)
    # Has Python/SQL but misses the advanced AI tools
    create_pdf(
        "test_2_average.pdf",
        "Bob Analyst",
        "Junior Data Analyst",
        "Python, SQL, Excel, PowerPoint.",
        "Fresh graduate with strong statistics knowledge."
    )

    # 3. THE "UNKNOWN" SKILL CANDIDATE (For Digital Marketing)
    # Tests if your AI finds skills NOT in your Python Database
    create_pdf(
        "test_3_marketing.pdf",
        "Charlie Marketer",
        "Digital Marketing Manager",
        "SEO, Google Analytics, Mailchimp, Content Writing, HubSpot.",
        "Expert in driving organic traffic and managing campaigns."
    )
    