# Career Transition

Open source job transition agent system — resume generation, job pipeline, outreach, interview prep.

## Overview

This system helps candidates transition from one industry to another by:
- Converting raw career experience into structured professional data
- Generating polished, styled resumes (PDF)
- Optimizing LinkedIn profiles
- Building a repeatable job search pipeline
- Automating outreach and applications
- Preparing for interviews
- Weekly optimization based on metrics

## Components

```
career-transition/
├── resume-generator/       # Core: Markdown → styled PDF
├── templates/              # Resume templates (copy Adam Pena style)
├── prompts/                # Agent prompts per phase
├── kanban/                 # Hermes Kanban setup
├── scripts/                # Automation scripts
└── docs/                   # Documentation
```

## Quick Start

```bash
# Clone the repo
git clone https://github.com/ODNT-SOL/career-transition.git
cd career-transition

# Setup Hermes Kanban board
hermes kanban boards create career-transition
hermes kanban boards switch career-transition

# Start gateway
hermes gateway start
```

## Phases

| Phase | Component | Description |
|-------|-----------|-------------|
| 1 | Data Consolidation | Raw transcript → structured JSON |
| 2 | Role Positioning | Experience → target roles |
| 3 | Resume Generation | Markdown → styled PDF |
| 4 | LinkedIn Optimization | Profile rewrite |
| 5 | Job Pipeline | Daily job search |
| 6 | Outreach | Personalized messaging |
| 7 | Applications | Track + apply |
| 8 | Interview Prep | STAR stories |
| 9 | Weekly Optimization | Metrics → recommendations |

## Tech Stack

- Hermes Agent (OCR, prompts, orchestration)
- Hermes Kanban (workflow)
- Hermes Cron (scheduling)
- SQLite (local data)
- ReportLab / pandoc (PDF generation)

## License

MIT