"""
Resume Generator - Markdown to Styled PDF
Uses ReportLab to generate professional PDFs matching the Adam Pena template style.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import markdown
import json
import os
from datetime import datetime


# Adam Pena resume styling constants
FONT_HEADER = "Helvetica-Bold"
FONT_BODY = "Helvetica"
FONT_ACCENT = "Helvetica-Oblique"

COLOR_HEADER = colors.HexColor("#1a1a1a")
COLOR_BODY = colors.HexColor("#333333")
COLOR_ACCENT = colors.HexColor("#666666")
COLOR_LINK = colors.HexColor("#0066cc")


def create_resume_styles():
    """Create custom styles matching Adam Pena resume."""
    styles = getSampleStyleSheet()
    
    # Header name style
    styles.add(ParagraphStyle(
        name="HeaderName",
        parent=styles["Heading1"],
        fontName=FONT_HEADER,
        fontSize=18,
        textColor=COLOR_HEADER,
        spaceAfter=2,
        alignment=TA_LEFT,
    ))
    
    # Role subtitle
    styles.add(ParagraphStyle(
        name="RoleSubtitle",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=11,
        textColor=COLOR_BODY,
        spaceAfter=8,
    ))
    
    # Contact info
    styles.add(ParagraphStyle(
        name="ContactInfo",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=9,
        textColor=COLOR_ACCENT,
        spaceAfter=12,
    ))
    
    # Section header
    styles.add(ParagraphStyle(
        name="SectionHeader",
        parent=styles["Heading2"],
        fontName=FONT_HEADER,
        fontSize=12,
        textColor=COLOR_HEADER,
        spaceBefore=12,
        spaceAfter=6,
        borderPadding=0,
        keepWithNext=True,
    ))
    
    # Job title
    styles.add(ParagraphStyle(
        name="JobTitle",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=10,
        textColor=COLOR_HEADER,
        fontBold=True,
        spaceAfter=2,
    ))
    
    # Company + dates
    styles.add(ParagraphStyle(
        name="CompanyInfo",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=9,
        textColor=COLOR_ACCENT,
        spaceAfter=6,
    ))
    
    # Bullet point
    styles.add(ParagraphStyle(
        name="BulletPoint",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=10,
        textColor=COLOR_BODY,
        spaceAfter=4,
        leftIndent=20,
        firstLineIndent=-20,
    ))
    
    # Skills category
    styles.add(ParagraphStyle(
        name="SkillsCategory",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=10,
        textColor=COLOR_HEADER,
        fontBold=True,
        spaceAfter=2,
    ))
    
    # Skills list
    styles.add(ParagraphStyle(
        name="SkillsList",
        parent=styles["Normal"],
        fontName=FONT_BODY,
        fontSize=10,
        textColor=COLOR_BODY,
        spaceAfter=8,
    ))
    
    return styles


def parse_resume_json(json_path: str) -> dict:
    """Load resume data from JSON."""
    with open(json_path, 'r') as f:
        return json.load(f)


def generate_header(data: dict, styles) -> list:
    """Generate header section."""
    elements = []
    
    # Name
    elements.append(Paragraph(data.get("name", "Candidate Name"), styles["HeaderName"]))
    
    # Role subtitle
    roles = data.get("roles", [])
    if roles:
        roles_str = " | ".join(roles[:3])
        elements.append(Paragraph(roles_str, styles["RoleSubtitle"]))
    
    # Contact info
    contact_parts = []
    if data.get("email"): contact_parts.append(data["email"])
    if data.get("phone"): contact_parts.append(data["phone"])
    if data.get("linkedin"): contact_parts.append(data["linkedin"])
    if data.get("location"): contact_parts.append(data["location"])
    
    if contact_parts:
        elements.append(Paragraph(" | ".join(contact_parts), styles["ContactInfo"]))
    
    elements.append(Spacer(1, 6))
    return elements


def generate_summary(data: dict, styles) -> list:
    """Generate professional summary."""
    elements = []
    if data.get("summary"):
        elements.append(Paragraph(data["summary"], styles["Normal"]))
        elements.append(Spacer(1, 12))
    return elements


def generate_experience(data: dict, styles) -> list:
    """Generate work experience section."""
    elements = []
    experiences = data.get("experience", [])
    
    for exp in experiences:
        # Job title
        if exp.get("title"):
            elements.append(Paragraph(exp["title"], styles["JobTitle"]))
        
        # Company + location + dates
        company_parts = []
        if exp.get("company"): company_parts.append(exp["company"])
        if exp.get("location"): company_parts.append(exp["location"])
        if exp.get("dates"): company_parts.append(exp["dates"])
        
        if company_parts:
            elements.append(Paragraph(" | ".join(company_parts), styles["CompanyInfo"]))
        
        # Bullet points
        for bullet in exp.get("bullets", []):
            # Add bullet character
            elements.append(Paragraph(f"• {bullet}", styles["BulletPoint"]))
        
        elements.append(Spacer(1, 8))
    
    return elements


def generate_skills(data: dict, styles) -> list:
    """Generate skills section."""
    elements = []
    skills = data.get("skills", {})
    
    for category, skill_list in skills.items():
        elements.append(Paragraph(f"{category}:", styles["SkillsCategory"]))
        if isinstance(skill_list, list):
            skills_str = ", ".join(skill_list)
        else:
            skills_str = str(skill_list)
        elements.append(Paragraph(skills_str, styles["SkillsList"]))
    
    return elements


def generate_resume_pdf(json_path: str, output_path: str, template_style: str = "adam_pena"):
    """
    Generate a styled PDF resume from JSON data.
    
    Args:
        json_path: Path to resume JSON data
        output_path: Output PDF path
        template_style: Template to use (default: adam_pena)
    """
    # Load data
    data = parse_resume_json(json_path)
    
    # Create PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=LETTER,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    # Build story
    styles = create_resume_styles()
    story = []
    
    # Header
    story.extend(generate_header(data, styles))
    
    # Professional Summary
    story.extend(generate_summary(data, styles))
    
    # Section: Work Experience
    story.append(Paragraph("WORK EXPERIENCE", styles["SectionHeader"]))
    story.extend(generate_experience(data, styles))
    
    # Section: Skills
    story.append(Paragraph("SKILLS", styles["SectionHeader"]))
    story.extend(generate_skills(data, styles))
    
    # Build PDF
    doc.build(story)
    return output_path


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python resume_generator.py <input.json> <output.pdf>")
        sys.exit(1)
    
    generate_resume_pdf(sys.argv[1], sys.argv[2])
    print(f"Generated: {sys.argv[2]}")