# Phase 3: Resume Generation Prompt

## Objective
Create impact-driven, professional resumes using the Adam Pena template style.

## Resume Structure
1. Header (Name, Roles, Contact)
2. Professional Summary (2-3 lines)
3. Work Experience (bullets with impact)
4. Additional Experience
5. Skills (grouped)

## Resume Versions Needed

### Version 1: General Operations Focus
Best for: Operations Coordinator, Operations Analyst, Project Coordinator

### Version 2: Business Analyst Focus
Best for: Business Analyst, Process Improvement, Data Analyst

### Version 3: Customer Success Focus
Best for: Customer Success Specialist, Client Success, Support Operations

## Style Guide

### Header Template
```
[Candidate Name]
Operations & Business Analyst | Customer Success | Process Optimization
[Phone] | [Email] | [LinkedIn] | [City, State]
```

### Bullet Formula
> Action verb + responsibility + business impact

**Strong action verbs:**
- Analyzed, Built, Conducted, Created, Developed, Facilitated, Improved, Led, Managed, Organized, Supported

### Example Bullets
- Analyzed and organized operational data to support agent performance tracking, pipeline visibility, and business decision-making.
- Built and maintained agent pipelines, improving workflow organization and visibility across customer and sales activity.
- Conducted internal audits to ensure accuracy, compliance, and consistency across agent performance and business processes.
- Developed templates, SOPs, training guides, and manuals to standardize team workflows and improve onboarding consistency.

### Skills Section Format
```
Operations & Business:
Data Analysis, Pipeline Management, Workflow Optimization, Process Improvement...

Tools & Technology:
Microsoft Excel, Microsoft Outlook, Zoom, Remote Collaboration Tools...

Core Strengths:
Problem-Solving, Communication, Team Collaboration, Time Management...
```

## Output Files
- `Resume_v1_ops.md` - General operations
- `Resume_v2_ba.md` - Business analyst
- `Resume_v3_cs.md` - Customer success
- Or generate JSON for PDF generation

## Acceptance Criteria
- [ ] Every bullet starts with action verb
- [ ] Transferable outside insurance industry
- [ ] Passes 10-second recruiter scan
- [ ] 3 versions covering target roles