# run this file once: python create_test_pdf.py
# from the rag-assistant/ root folder

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

os.makedirs("backend/data/uploads", exist_ok=True)
path = "backend/data/uploads/hr_policy.pdf"

c = canvas.Canvas(path, pagesize=letter)

# ── PAGE 1 ──────────────────────────────────────────
c.setFont("Helvetica-Bold", 18)
c.drawString(50, 750, "ACME Corp — HR Policy Manual")
c.setFont("Helvetica", 10)
c.drawString(50, 730, "Version 2.1 | Effective January 2024")

c.setFont("Helvetica-Bold", 13)
c.drawString(50, 700, "1. Annual Leave")
c.setFont("Helvetica", 11)
items = [
    "Full-time employees receive 20 days paid annual leave per year.",
    "Part-time employees receive leave on a pro-rata basis.",
    "Leave requests must be submitted 2 weeks in advance via HR portal.",
    "Up to 10 unused leave days can be carried over to the next year.",
    "Leave encashment is permitted for up to 5 days at basic salary rate.",
]
y = 675
for item in items:
    c.drawString(60, y, f"• {item}")
    y -= 22

c.setFont("Helvetica-Bold", 13)
c.drawString(50, y - 10, "2. Sick Leave")
c.setFont("Helvetica", 11)
items2 = [
    "Employees receive 10 days paid sick leave annually.",
    "A medical certificate is required for absences over 2 consecutive days.",
    "Sick leave cannot be carried over to the following year.",
    "Probationary employees receive 5 days sick leave only.",
]
y -= 35
for item in items2:
    c.drawString(60, y, f"• {item}")
    y -= 22

c.showPage()

# ── PAGE 2 ──────────────────────────────────────────
c.setFont("Helvetica-Bold", 13)
c.drawString(50, 750, "3. Work From Home Policy")
c.setFont("Helvetica", 11)
items3 = [
    "Employees may work from home up to 2 days per week.",
    "WFH is not allowed during the first 3 months (probation period).",
    "Employees must be reachable on Slack and email during core hours.",
    "Core hours are 10:00 AM to 4:00 PM in your local timezone.",
    "Home office equipment can be requested from the IT department.",
]
y = 725
for item in items3:
    c.drawString(60, y, f"• {item}")
    y -= 22

c.setFont("Helvetica-Bold", 13)
c.drawString(50, y - 10, "4. Salary and Compensation")
c.setFont("Helvetica", 11)
items4 = [
    "Salaries are paid on the last working day of each month.",
    "Annual appraisals happen every March.",
    "Exceeds Expectations rating: minimum 10% salary increment.",
    "Meets Expectations rating: 5 to 7% increment.",
    "Annual bonus of 1 to 3 months basic salary paid in April.",
]
y -= 35
for item in items4:
    c.drawString(60, y, f"• {item}")
    y -= 22

c.showPage()

# ── PAGE 3 ──────────────────────────────────────────
c.setFont("Helvetica-Bold", 13)
c.drawString(50, 750, "5. Code of Conduct")
c.setFont("Helvetica", 11)
items5 = [
    "Treat all colleagues with respect and professionalism.",
    "Harassment of any kind is strictly prohibited and grounds for termination.",
    "Company information must remain confidential at all times.",
    "Conflicts of interest must be declared to your manager in writing.",
    "Violations may result in warnings, suspension, or immediate termination.",
]
y = 725
for item in items5:
    c.drawString(60, y, f"• {item}")
    y -= 22

c.setFont("Helvetica-Bold", 13)
c.drawString(50, y - 10, "6. Grievance Policy")
c.setFont("Helvetica", 11)
items6 = [
    "Employees can raise grievances by emailing hr@acmecorp.com.",
    "All grievances are acknowledged within 2 business days.",
    "Investigations are completed within 15 business days.",
    "Employees may bring a colleague as a support person to grievance meetings.",
    "Retaliation against employees who raise grievances is strictly prohibited.",
]
y -= 35
for item in items6:
    c.drawString(60, y, f"• {item}")
    y -= 22

c.save()
print(f"✅ PDF created: {path}")
print("   Pages: 3")
print("   Topics: Leave, Sick Leave, WFH, Salary, Conduct, Grievance")