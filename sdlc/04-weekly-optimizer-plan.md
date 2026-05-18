# Weekly Optimization Engine - SDLC Plan

## Issue: #31 [sdlc:plan] Weekly Optimization Engine
## Parent: #5 Weekly Optimization Engine

### Requirements (from parent issue)
- Metrics tracking and optimization recommendations
- Track apps, responses, interviews
- Output weekly PDF report
- Diagnosis rules for strategy adjustment
- Priority: Medium

### Acceptance Criteria
- [ ] Track job applications (submitted, response rate, interviews)
- [ ] Track outreach responses (replies, acceptance, rejection)
- [ ] Generate weekly summary report
- [ ] Output report as PDF
- [ ] Provide optimization recommendations based on diagnosis rules
- [ ] CLI to log activities and generate reports

### Entry Points
- Input: activity logs (applications, outreach, interviews)
- Output: weekly PDF report with metrics and recommendations

### Test Plan
- Unit test metric calculations
- Unit test diagnosis rules
- Integration test: log activities → generate PDF
- Verify PDF output is valid and non-empty

---

## Detailed Implementation Specification

### File Structure
```
weekly-optimizer/
├── __init__.py
├── optimizer.py          # Core logic
├── metrics.py            # Metric calculations
├── diagnosis.py          # Diagnosis rules engine
├── report_generator.py   # PDF report generation
├── activities.py         # Activity logging
├── config.json           # Configuration
└── test_optimizer.py    # Unit tests
```

### Configuration Schema (config.json)
```json
{
  "report_title": "Weekly Job Search Report",
  "author": "Brandy",
  "report_output": "weekly-report.pdf",
  "thresholds": {
    "low_response_rate": 0.1,
    "good_response_rate": 0.25,
    "low_interview_rate": 0.05,
    "good_interview_rate": 0.15
  },
  "diagnosis_rules": [
    {
      "condition": "response_rate < 0.1",
      "recommendation": "Your response rate is low. Consider: (1) Customizing cover letters more, (2) Targeting roles closer to your experience, (3) Expanding to adjacent job titles."
    },
    {
      "condition": "interview_rate < 0.05",
      "recommendation": "Interview rate is very low. Consider: (1) Resume optimization, (2) Applying to more roles, (3) Reviewing job descriptions for keyword alignment."
    },
    {
      "condition": "response_rate >= 0.25 AND outreach_reply_rate >= 0.3",
      "recommendation": "Great response rates! Maintain current strategy and focus on interview preparation."
    }
  ]
}
```

### Activities Log Schema (activities.jsonl)
Each line is a JSON object:
```
{"date": "2025-05-12", "type": "application", "company": "TechCorp", "role": "Software Engineer", "status": "submitted"}
{"date": "2025-05-13", "type": "outreach", "contact_id": 1, "status": "replied"}
{"date": "2025-05-14", "type": "interview", "company": "StartupXYZ", "role": "Backend Dev", "status": "scheduled"}
{"date": "2025-05-15", "type": "interview", "company": "StartupXYZ", "role": "Backend Dev", "status": "completed"}
{"date": "2025-05-16", "type": "offer", "company": "StartupXYZ", "role": "Backend Dev", "status": "received"}
```

### Activity Types
- `application` — Job application submitted
- `outreach` — Outreach message sent (linked to contact_id)
- `interview` — Interview event (scheduled/completed/cancelled)
- `offer` — Job offer (received/declined/accepted)

### Metrics Calculated

| Metric | Formula |
|--------|---------|
| Applications submitted (week) | Count of `application` with status=submitted |
| Applications total | Cumulative count |
| Response rate | (applications with response / total applications) |
| Outreach sent (week) | Count of outreach |
| Outreach reply rate | (replies / outreach sent) |
| Interviews (week) | Count of interviews |
| Interview rate | (interviews / applications) |
| Offers | Count of offers |

### Diagnosis Rules Engine
Each rule has:
- `condition`: Python-like expression evaluated against metrics dict
- `recommendation`: Human-readable advice

Example rule evaluation:
```python
metrics = calculate_metrics(activities)
for rule in config["diagnosis_rules"]:
    if eval(rule["condition"], {}, metrics):
        recommendations.append(rule["recommendation"])
```

### Classes

#### `ActivityLogger`
- `log_activity(type, date, **kwargs)` — Append to activities.jsonl
- `load_activities()` — Load all activities from file
- `get_activities_since(date)` — Get activities from a date range

#### `MetricsCalculator`
- `calculate(metrics)` — Returns dict of all metrics
- `weekly_summary(activities)` — Metrics for current week
- `cumulative_summary(activities)` — All-time metrics

#### `DiagnosisEngine`
- `evaluate(metrics)` — Returns list of recommendations

#### `ReportGenerator`
- `generate_pdf(output_path)` — Create PDF report
- Uses ReportLab or fpdf for PDF generation

### PDF Report Structure
1. **Header**: Report title, date range, author
2. **Executive Summary**: 3-5 bullet points of key stats
3. **Metrics Table**: This week vs. last week comparison
4. **Diagnosis & Recommendations**: Bulleted advice
5. **Activity Log**: Table of recent activities

### CLI Interface
```bash
# Log an activity
python optimizer.py log --type application --company TechCorp --role "Software Engineer"
python optimizer.py log --type outreach --contact-id 1
python optimizer.py log --type interview --company TechCorp --role "SWE" --status scheduled
python optimizer.py log --type offer --company Startup --role "Dev" --status accepted

# Generate weekly report
python optimizer.py report --output weekly-report.pdf

# View current metrics
python optimizer.py metrics
```

### Dependencies
- `reportlab` or `fpdf2` — PDF generation
- Standard library: `json`, `datetime`, `statistics`

### Cron Setup (sdlc:ops stage)
```bash
# Every Monday at 10 AM
0 10 * * 1 cd /home/chronos/career-transition && .venv/bin/python weekly-optimizer/optimizer.py report --output weekly-reports/$(date +\%Y-\%m-\%d).pdf
```
