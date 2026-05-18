#!/usr/bin/env python3
"""Interview Prep Generator - STAR stories, pitches, and onboarding plans."""

import datetime
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "candidate_name": "Brandy",
    "current_role": "Software Engineer",
    "target_role": "Senior Software Engineer",
    "key_skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
    "years_experience": 3,
    "output_file": "interview-prep.pdf",
}


class PrepConfig:
    def __init__(self, config_path: Optional[str] = None):
        self.config = DEFAULT_CONFIG.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path) as f:
                self.config.update(json.load(f))

    def get(self, key: str, default=None):
        return self.config.get(key, default)


# ---------------------------------------------------------------------------
# Resume Loading
# ---------------------------------------------------------------------------

def load_resume(resume_path: str) -> dict:
    """Load resume from JSON file."""
    with open(resume_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# STAR Story Generator
# ---------------------------------------------------------------------------

STAR_PREAMBLE = """**STAR Story: {title}**

**Situation:** {situation}

**Task:** {task}

**Action:** {action}

**Result:** {result}
"""


class STARStoryGenerator:
    """Generate STAR-formatted interview stories."""

    def __init__(self, candidate_data: dict):
        self.data = candidate_data

    def _extract_experiences(self) -> list[dict]:
        """Extract experience entries from resume."""
        if isinstance(self.data, dict):
            return self.data.get("experience", [])
        return []

    def _make_story(self, exp: dict, skill: str, index: int) -> str:
        """Generate a STAR story from an experience entry."""
        company = exp.get("company", "my team")
        role = exp.get("title", exp.get("role", "Software Engineer"))
        bullets = exp.get("bullets", exp.get("highlights", []))

        # Generate STAR components from bullet points
        if bullets:
            situation = f"At {company}, I was a {role} tasked with {bullets[0].lower().rstrip('.') if bullets else 'delivering a critical project'}."
            task = f"I needed to ensure the project was completed on time while maintaining quality standards."
            action = bullets[1] if len(bullets) > 1 else f"I leveraged {skill} to implement the required functionality, collaborating closely with the team."
            result = bullets[2] if len(bullets) > 2 else "The project was delivered successfully, resulting in improved performance and positive feedback from stakeholders."
        else:
            situation = f"At {company}, I was responsible for delivering key technical projects as a {role}."
            task = f"I needed to apply my {skill} skills to solve a complex technical challenge."
            action = f"I designed and implemented a solution using {skill}, following best practices and code review processes."
            result = "The solution was deployed to production, achieving a measurable improvement and receiving positive feedback from the team."

        return STAR_PREAMBLE.format(
            title=f"{skill} - {role} at {company}",
            situation=situation,
            task=task,
            action=action,
            result=result,
        )

    def generate_stories(self, count: int = 10) -> list[str]:
        """Generate N STAR stories."""
        experiences = self._extract_experiences()
        skills = self.data.get("skills", self.data.get("key_skills", DEFAULT_CONFIG["key_skills"]))
        if isinstance(skills, dict):
            skills = skills.get("technical", skills.get("skills", list(skills.keys())[:10]))
        if isinstance(skills, list) and len(skills) == 0:
            skills = ["Python", "JavaScript", "React", "Leadership", "Communication"]

        stories = []
        for i in range(count):
            exp = experiences[i % max(len(experiences), 1)] if experiences else {}
            skill = skills[i % len(skills)]
            stories.append(self._make_story(exp, skill, i))
        return stories


# ---------------------------------------------------------------------------
# Transition Narrative
# ---------------------------------------------------------------------------

TRANSITION_TEMPLATE = """## Career Transition Narrative

### Why I'm Transitioning to {target_role}

After {years} years as a {current_role}, I've developed a strong foundation in building scalable software solutions. I'm now seeking a {target_role} role where I can take on greater technical leadership and strategic impact.

### My Journey

My transition is driven by:
1. **Desire for larger technical challenges** — I want to work on systems that scale to millions of users
2. **Leadership growth** — I'm ready to mentor junior developers and drive architectural decisions
3. **Industry alignment** — The {target_role} role aligns perfectly with my experience in {skills_list}

### Transferable Skills

- **{skills_list}** — Core technical competencies
- **Problem-solving** — Track record of debugging complex issues under pressure
- **Communication** — Experience presenting technical concepts to non-technical stakeholders
- **Team collaboration** — Worked in agile teams of 5-10 engineers across time zones

### Why I'm a Strong Fit

I'm not just looking for any role — I'm specifically targeting companies where I can contribute immediately while continuing to grow. My background in {skills_list} gives me a solid foundation, and my proven ability to learn quickly means I'll ramp up on your specific stack within weeks.
"""


class TransitionNarrative:
    """Generate career transition narrative."""

    def __init__(self, candidate_data: dict, config: PrepConfig):
        self.data = candidate_data
        self.config = config

    def generate(self, target_role: Optional[str] = None) -> str:
        target = target_role or self.config.get("target_role", "the target role")
        current = self.config.get("current_role", "Software Engineer")
        years = self.config.get("years_experience", 3)
        skills = self.config.get("key_skills", ["Python", "JavaScript"])
        skills_list = ", ".join(skills[:4])

        return TRANSITION_TEMPLATE.format(
            target_role=target,
            current_role=current,
            years=years,
            skills_list=skills_list,
        )


# ---------------------------------------------------------------------------
# Pitch Generator
# ---------------------------------------------------------------------------

PITCH_30SEC = """## 30-Second Elevator Pitch

Hi, I'm {name}, a {current_role} with {years} years of experience building web applications and APIs. I'm passionate about writing clean, maintainable code and collaborating with cross-functional teams to deliver products that users love.

I'm particularly experienced in {skills_list}, and I've recently been focusing on building scalable backend systems. I'm excited about the {target_role} role at {company} because it aligns perfectly with my background and career goals.

"""


PITCH_2MIN = """## 2-Minute Pitch

Hi, I'm {name}.

I've spent the last {years} years as a {current_role}, where I've built everything from customer-facing React dashboards to high-throughput Python APIs processing millions of requests per day.

My key achievements include:
- Built a real-time notification system using WebSockets that reduced customer support tickets by 30%
- Led the migration of a monolithic app to microservices, improving deployment frequency from weekly to daily
- Mentored 3 junior developers, two of whom received promotions within a year

What excites me about {target_role} is the opportunity to work on larger-scale systems and take on more technical leadership. I'm particularly drawn to {company} because of your focus on {company_value}, and I believe my background in {skills_list} makes me a strong fit.

I'm excited about this opportunity and look forward to discussing how I can contribute to your team.
"""


class PitchGenerator:
    """Generate elevator pitches."""

    def __init__(self, candidate_data: dict, config: PrepConfig):
        self.data = candidate_data
        self.config = config

    def generate_30sec(self, company: str = "your company") -> str:
        name = self.config.get("candidate_name", "Candidate")
        current = self.config.get("current_role", "Software Engineer")
        years = self.config.get("years_experience", 3)
        skills = self.config.get("key_skills", ["Python", "JavaScript"])
        skills_list = ", ".join(skills[:3])
        target = self.config.get("target_role", "the target role")

        return PITCH_30SEC.format(
            name=name,
            current_role=current,
            years=years,
            skills_list=skills_list,
            target_role=target,
            company=company,
        )

    def generate_2min(self, company: str = "your company", company_value: str = "building great products") -> str:
        name = self.config.get("candidate_name", "Candidate")
        current = self.config.get("current_role", "Software Engineer")
        years = self.config.get("years_experience", 3)
        skills = self.config.get("key_skills", ["Python", "JavaScript"])
        skills_list = ", ".join(skills[:3])
        target = self.config.get("target_role", "the target role")

        return PITCH_2MIN.format(
            name=name,
            current_role=current,
            years=years,
            skills_list=skills_list,
            target_role=target,
            company=company,
            company_value=company_value,
        )


# ---------------------------------------------------------------------------
# Onboarding Plan
# ---------------------------------------------------------------------------

ONBOARDING_TEMPLATE = """## 30-60-90 Day Onboarding Plan

### First 30 Days: Learn & Orient

**Goals:**
- Understand the codebase, team processes, and existing systems
- Set up development environment and get first PR merged
- Meet with each team member 1:1 to understand roles and responsibilities
- Shadow code reviews and design discussions

**Key Deliverables:**
- Complete all onboarding documentation
- Submit first PR (even if small — bug fix or documentation improvement)
- Deliver a "learnings" summary to manager by day 30

### Days 31-60: Contribute & Integrate

**Goals:**
- Take ownership of a moderate-complexity feature end-to-end
- Improve one existing process or tool (e.g., CI pipeline, testing)
- Begin contributing to design discussions
- Establish regular 1:1 rhythm with manager

**Key Deliverables:**
- Ship first major feature
- Lead at least one technical design doc
- Conduct a lunch-and-learn on a technical topic

### Days 61-90: Drive & Lead

**Goals:**
- Own a critical path feature or system
- Mentor junior team members
- Propose and drive one process improvement
- Set OKRs for next quarter in alignment with team goals

**Key Deliverables:**
- Feature roadmap for next quarter
- At least one system design document you initiated
- Demonstrate measurable impact (performance improvement, bug reduction, etc.)
"""


class OnboardingPlan:
    """Generate 30-60-90 day onboarding plan."""

    def generate(self, candidate_data: dict, config: PrepConfig, target_company: str = "your company") -> str:
        return ONBOARDING_TEMPLATE


# ---------------------------------------------------------------------------
# PDF Report Generator
# ---------------------------------------------------------------------------

class InterviewPrepReport:
    """Compile all interview prep materials into a PDF."""

    def __init__(self, config: PrepConfig, resume_data: dict):
        self.config = config
        self.resume_data = resume_data
        self.star_gen = STARStoryGenerator(resume_data)
        self.transition = TransitionNarrative(resume_data, config)
        self.pitch_gen = PitchGenerator(resume_data, config)
        self.onboarding = OnboardingPlan()

    def generate_pdf(self, output_path: str, target_role: str = None, company: str = None) -> bool:
        if not PDF_AVAILABLE:
            print("Error: reportlab not installed. PDF generation unavailable.", file=sys.stderr)
            return False

        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("CustomTitle", parent=styles["Heading1"], fontSize=20, spaceAfter=20)
        section_style = ParagraphStyle("Section", parent=styles["Heading2"], fontSize=14, spaceBefore=15, spaceAfter=8, textColor=colors.HexColor("#2C3E50"))
        body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10, spaceAfter=6)
        star_style = ParagraphStyle("STAR", parent=styles["Normal"], fontSize=9, fontName="Courier", spaceAfter=12, leading=13)

        story = []

        # Header
        name = self.config.get("candidate_name", "Candidate")
        story.append(Paragraph(f"Interview Preparation Guide", title_style))
        story.append(Paragraph(f"Candidate: {name} | Generated: {datetime.datetime.now().strftime('%Y-%m-%d')}", body_style))
        story.append(Spacer(1, 0.3 * inch))

        # STAR Stories
        story.append(Paragraph("STAR Stories", section_style))
        stories = self.star_gen.generate_stories(10)
        for i, story_text in enumerate(stories, 1):
            # Render each STAR as formatted paragraphs
            lines = story_text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("**") and line.endswith("**"):
                    story.append(Paragraph(f"<b>{line[2:-2]}</b>", body_style))
                else:
                    # Process bold markers
                    formatted = line.replace("**", "<b>").replace("**", "</b>")
                    story.append(Paragraph(formatted, star_style))
            if i < len(stories):
                story.append(Spacer(1, 0.15 * inch))

        story.append(Spacer(1, 0.2 * inch))

        # Transition Narrative
        story.append(Paragraph("Career Transition Narrative", section_style))
        transition_text = self.transition.generate(target_role)
        for para in transition_text.split("\n"):
            para = para.strip()
            if not para:
                continue
            if para.startswith("#"):
                continue
            formatted = para.replace("**", "<b>").replace("*", "<i>")
            story.append(Paragraph(formatted, body_style))

        story.append(Spacer(1, 0.2 * inch))

        # Pitches
        story.append(Paragraph("Elevator Pitches", section_style))
        story.append(Paragraph("30-Second Pitch", ParagraphStyle("Sub", parent=styles["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=4)))
        pitch_30 = self.pitch_gen.generate_30sec(company or "the company")
        for para in pitch_30.split("\n"):
            para = para.strip()
            if para.startswith("#") or not para:
                continue
            formatted = para.replace("**", "<b>")
            story.append(Paragraph(formatted, body_style))

        story.append(Spacer(1, 0.1 * inch))
        story.append(Paragraph("2-Minute Pitch", ParagraphStyle("Sub", parent=styles["Heading3"], fontSize=11, spaceBefore=8, spaceAfter=4)))
        pitch_2 = self.pitch_gen.generate_2min(company or "the company", company or "building great products")
        for para in pitch_2.split("\n"):
            para = para.strip()
            if para.startswith("#") or not para:
                continue
            formatted = para.replace("**", "<b>")
            story.append(Paragraph(formatted, body_style))

        story.append(Spacer(1, 0.2 * inch))

        # Onboarding Plan
        story.append(Paragraph("30-60-90 Day Onboarding Plan", section_style))
        onboarding_text = self.onboarding.generate(self.resume_data, self.config, company or "your company")
        in_list = False
        for para in onboarding_text.split("\n"):
            para = para.strip()
            if not para:
                in_list = False
                continue
            if para.startswith("### "):
                story.append(Paragraph(f"<b>{para[4:]}</b>", body_style))
            elif para.startswith("**Goals:**"):
                story.append(Paragraph(f"<b>Goals:</b>", body_style))
            elif para.startswith("**Key Deliverables:**"):
                story.append(Paragraph(f"<b>Key Deliverables:</b>", body_style))
            elif para.startswith("- "):
                story.append(Paragraph(f"• {para[2:]}", body_style))
            else:
                formatted = para.replace("**", "<b>")
                story.append(Paragraph(formatted, body_style))

        doc.build(story)
        return True

    def generate_text(self, output_path: str, target_role: str = None, company: str = None) -> bool:
        """Generate as plain text file."""
        lines = []
        name = self.config.get("candidate_name", "Candidate")
        lines.append(f"Interview Preparation Guide - {name}")
        lines.append("=" * 60)
        lines.append("")

        lines.append("STAR STORIES")
        lines.append("-" * 40)
        for i, s in enumerate(self.star_gen.generate_stories(10), 1):
            lines.append(s)
            lines.append("")

        lines.append("")
        lines.append("CAREER TRANSITION NARRATIVE")
        lines.append("-" * 40)
        lines.append(self.transition.generate(target_role))

        lines.append("")
        lines.append("30-SECOND PITCH")
        lines.append("-" * 40)
        lines.append(self.pitch_gen.generate_30sec(company or "the company"))

        lines.append("")
        lines.append("2-MINUTE PITCH")
        lines.append("-" * 40)
        lines.append(self.pitch_gen.generate_2min(company or "the company"))

        lines.append("")
        lines.append("30-60-90 DAY ONBOARDING PLAN")
        lines.append("-" * 40)
        lines.append(self.onboarding.generate(self.resume_data, self.config, company or "your company"))

        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        return True


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Interview Prep Generator")
    parser.add_argument("--config", help="Path to config JSON file")
    parser.add_argument("--resume", default="resume.json", help="Path to resume JSON file")
    parser.add_argument("--target-role", default=None, help="Target job role")
    parser.add_argument("--company", default=None, help="Target company name")
    sub = parser.add_subparsers(dest="command")

    gen = sub.add_parser("generate", help="Generate full interview prep PDF")
    gen.add_argument("--output", default="interview-prep.pdf", help="Output file path")

    star_p = sub.add_parser("star-stories", help="Generate STAR stories only")
    star_p.add_argument("--output", default=None, help="Output file path")
    star_p.add_argument("--count", type=int, default=10, help="Number of stories")

    pitches_p = sub.add_parser("pitches", help="Generate pitches only")
    pitches_p.add_argument("--output", default=None, help="Output file path")

    args = parser.parse_args()

    config = PrepConfig(args.config)
    resume_data = {}
    if os.path.exists(args.resume):
        resume_data = load_resume(args.resume)

    report = InterviewPrepReport(config, resume_data)

    if args.command == "generate":
        output = args.output or config.get("output_file", "interview-prep.pdf")
        ext = os.path.splitext(output)[1].lower()
        if ext == ".pdf":
            success = report.generate_pdf(output, args.target_role, args.company)
        else:
            success = report.generate_text(output, args.target_role, args.company)
        if success:
            print(f"Generated: {output}")
        else:
            print("Failed to generate output.", file=sys.stderr)
            sys.exit(1)

    elif args.command == "star-stories":
        stories = STARStoryGenerator(resume_data).generate_stories(args.count)
        content = "\n\n".join(stories)
        if args.output:
            with open(args.output, "w") as f:
                f.write(content)
            print(f"STAR stories written to {args.output}")
        else:
            print(content)

    elif args.command == "pitches":
        pg = PitchGenerator(resume_data, config)
        output_30 = pg.generate_30sec(args.company or "the company")
        output_2 = pg.generate_2min(args.company or "the company", args.company or "building great products")
        content = f"30-SECOND PITCH\n{'='*40}\n{output_30}\n\n2-MINUTE PITCH\n{'='*40}\n{output_2}"
        if args.output:
            with open(args.output, "w") as f:
                f.write(content)
            print(f"Pitches written to {args.output}")
        else:
            print(content)

    else:
        parser.print_help()
