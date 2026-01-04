from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

def create_pdf(filename):
    c = canvas.Canvas(filename, pagesize=LETTER)
    c.setFont("Helvetica", 12)
    
    # Content designed to test Dynamic Matching
    text = [
        "Name: Sarah Marketer",
        "Role: Digital Marketing Specialist",
        "Summary: Expert in driving traffic and engagement.",
        "Skills: I use Google Analytics to track performance.",
        "I am an expert in SEO strategies and Content Writing.",
        "Proficient with Mailchimp for email campaigns.",
        "Experience: Managed ads on Facebook Ads Manager."
    ]
    
    y = 750
    for line in text:
        c.drawString(50, y, line)
        y -= 20
        
    c.save()
    print(f"✅ Created {filename}")

if __name__ == "__main__":
    create_pdf("resume_marketing.pdf")
    