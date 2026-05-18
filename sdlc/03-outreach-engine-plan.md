# Outreach Engine - SDLC Plan

## Issue: #19 [sdlc:plan] Outreach Engine
## Parent: #3 Outreach Engine

### Requirements (from parent issue)
- Personalized messaging automation
- Locate recruiters/hiring managers
- Template-based messages
- Follow-up automation
- Track responses in SQLite
- Priority: High

### Acceptance Criteria
- [ ] Find recruiter/hiring manager contact info from LinkedIn/company sites
- [ ] Generate personalized outreach messages using templates
- [ ] Send initial outreach and scheduled follow-ups
- [ ] Track outreach status in SQLite database
- [ ] CLI to send messages and view status
- [ ] Configurable templates with personalization tokens

### Entry Points
- Input: config file with template strings and target contacts
- Output: SQLite DB for tracking, sent messages logged

### Test Plan
- Unit test template rendering with tokens
- Unit test contact finding logic
- Integration test: send message → verify DB entry
- Verify follow-up scheduling logic

---

## Detailed Implementation Specification

### File Structure
```
outreach-engine/
├── __init__.py
├── outreach_engine.py    # Core logic
├── templates.py          # Message template engine
├── contact_finder.py     # Recruiter/hiring manager discovery
├── database.py           # SQLite tracking
├── config.json           # Configuration
└── test_outreach.py      # Unit tests
```

### Database Schema (SQLite)
```sql
CREATE TABLE contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    company TEXT NOT NULL,
    title TEXT,
    email TEXT,
    linkedin_url TEXT,
    source TEXT,  -- 'linkedin', 'company_site', 'manual'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE outreach_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER REFERENCES contacts(id),
    message_type TEXT,  -- 'initial', 'followup_1', 'followup_2'
    subject TEXT,
    body TEXT,
    sent_at TIMESTAMP,
    status TEXT DEFAULT 'pending',  -- 'pending', 'sent', 'replied', 'bounced'
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);

CREATE TABLE followup_schedule (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER REFERENCES contacts(id),
    followup_number INTEGER,  -- 1, 2, 3
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    status TEXT DEFAULT 'pending',
    FOREIGN KEY (contact_id) REFERENCES contacts(id)
);
```

### Configuration Schema (config.json)
```json
{
  "templates": {
    "initial": {
      "subject": "Re: {job_title} opportunity at {company}",
      "body": "Hi {first_name},\n\nI came across the {job_title} role at {company} and am very interested. As a {my_title} with experience in {my_skills}, I believe I'd be a strong fit.\n\nWould love to connect and discuss further.\n\nBest,\n{my_name}"
    },
    "followup_1": {
      "subject": "Re: {job_title} opportunity at {company} - Following up",
      "body": "Hi {first_name},\n\nJust wanted to follow up on my earlier message about the {job_title} position. I'd love to discuss how my background in {my_skills} could contribute to {company}.\n\nBest,\n{my_name}"
    },
    "followup_2": {
      "subject": "Re: {job_title} at {company}",
      "body": "Hi {first_name},\n\nLast check-in on this — still very interested in the {job_title} role. Happy to share my resume or schedule a call at your convenience.\n\nBest,\n{my_name}"
    }
  },
  "followup_days": [3, 7, 14],  -- days after previous message to send each followup
  "my_name": "Brandy",
  "my_title": "Software Engineer",
  "my_skills": "Python, JavaScript, React, Node.js",
  "database": "outreach.db"
}
```

### Personalization Tokens
Templates support these tokens:
- `{first_name}` — Contact's first name
- `{full_name}` — Contact's full name
- `{company}` — Company name
- `{job_title}` — Target job title
- `{my_name}`, `{my_title}`, `{my_skills}` — My info from config

### Classes

#### `OutreachConfig`
- Loads config.json
- Provides template access
- Stores my personal info for personalization

#### `ContactFinder`
- `find_from_linkedin(job_title, company)` — Search LinkedIn for recruiters
- `find_from_company_site(company)` — Scrape company careers/team pages
- `add_contact(name, company, title, email, linkedin_url, source)` — Manual add

#### `TemplateEngine`
- `render(template_name, context)` — Fill in tokens
- `validate_template(template)` — Ensure required tokens present

#### `OutreachDB`
- SQLite wrapper
- `add_contact()`, `get_contact()`, `list_contacts()`
- `add_message()`, `get_messages_for_contact()`
- `schedule_followup()`, `get_pending_followups()`, `mark_sent()`

#### `OutreachSender`
- `send_initial(contact, job_title)` — Send first message
- `send_followup(contact, followup_number)` — Send scheduled follow-up
- `check_and_send_followups()` — Cron job function

### CLI Interface
```bash
# Add a contact manually
python outreach_engine.py add-contact --name "Jane Recruiter" --company "TechCorp" --title "Tech Recruiter" --email jane@techcorp.com

# Send initial outreach
python outreach_engine.py send --contact-id 1 --job-title "Software Engineer"

# Check and send pending followups
python outreach_engine.py send-followups

# List contacts
python outreach_engine.py list-contacts

# View message history
python outreach_engine.py history --contact-id 1
```

### Error Handling
- SMTP errors: log to DB with status='error', retry next run
- Invalid email: mark contact with warning flag
- Template missing token: raise ValueError with token name

### Dependencies
- `requests` — HTTP for LinkedIn/company site scraping
- `beautifulsoup4` — HTML parsing
- `lxml` — Fast XML/HTML parser
- `apscheduler` — Schedule follow-ups (or use cron)
