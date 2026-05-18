# Interview Prep Generator - SDLC Plan

## Issue: #26 [sdlc:plan] Interview Prep Generator
## Parent: #4 Interview Prep Generator

### Requirements (from parent issue)
- STAR story generation for interviews
- Create 10+ STAR stories
- Transition narrative
- 30-sec and 2-min pitches
- 30-60-90 day plan
- Priority: Medium

### Acceptance Criteria
- [ ] Generate STAR-formatted stories from resume data
- [ ] Create 10+ unique STAR stories covering different skills/scenarios
- [ ] Generate transition narrative explaining career change motivation
- [ ] Produce 30-second elevator pitch
- [ ] Produce 2-minute pitch
- [ ] Generate 30-60-90 day onboarding plan
- [ ] CLI to generate all outputs as a PDF or text file
- [ ] All outputs personalized to candidate's background

### Entry Points
- Input: Candidate resume JSON, job target description
- Output: interview-prep.pdf with all materials

### Test Plan
- Unit test STAR story template rendering
- Unit test pitch length calculation
- Unit test transition narrative generation
- Integration test: generate full PDF

---

## Detailed Implementation Specification

### File Structure
```
interview-prep/
├── __init__.py
├── interview_prep.py     # Core logic
├── star_stories.py      # STAR story generation
├── pitches.py           # Elevator pitches
├── transition.py        # Transition narrative
├── onboarding.py        # 30-60-90 day plan
├── report.py            # PDF generation
├── config.json          # Configuration
└── test_prep.py         # Unit tests
```

### Configuration Schema (config.json)
```json
{
  "candidate_name": "Brandy",
  "current_role": "Software Engineer",
  "target_role": "Senior Software Engineer",
  "key_skills": ["Python", "JavaScript", "React", "Node.js", "AWS"],
  "years_experience": 3,
  "output_file": "interview-prep.pdf"
}
```

### Classes

#### `STARStoryGenerator`
- `generate_stories(resume_data, count=10)` — Create N STAR stories
- Each story: Situation, Task, Action, Result with metrics
- Stories drawn from resume experience entries

#### `TransitionNarrative`
- `generate(candidate_data, target_role)` — Career transition story
- Explains motivation, transferable skills, fit

#### `PitchGenerator`
- `generate_30sec(candidate_data)` — Tight elevator pitch
- `generate_2min(candidate_data)` — Extended pitch with depth

#### `OnboardingPlan`
- `generate_30_60_90(candidate_data, target_company)` — 30/60/90 day plan

#### `InterviewPrepReport`
- `generate_pdf(output_path)` — Compile all sections into PDF

### CLI Interface
```bash
# Generate all interview prep materials
python interview_prep.py generate --resume ../resume-generator/brandy_resume.json --target "Senior SWE" --output interview-prep.pdf

# Generate just STAR stories
python interview_prep.py star-stories --resume ../resume-generator/brandy_resume.json

# Generate pitches
python interview_prep.py pitches --resume ../resume-generator/brandy_resume.json
```
