# Resume Generator - SDLC Plan

## Issue: #6 [sdlc:plan] Resume Generator
## Parent: #1 MVP: Resume Generator with PDF Output

### Requirements (from parent issue):
- Convert resume JSON data to styled PDF
- Match Adam Pena resume template style
- Support multiple sections: header, summary, experience, skills

### Acceptance Criteria:
- [ ] Generate PDF from JSON input
- [ ] Matches styling of Adam Pena resume
- [ ] Supports all resume sections
- [ ] CLI usage works

### Entry Points:
- Input: resume-generator/sample_resume.json
- Output: PDF file

### Test Plan:
- Generate sample_resume.json → PDF
- Verify formatting matches reference

### Implementation Notes:
- Use reportlab (already in venv)
- Code at: resume-generator/resume_generator.py
