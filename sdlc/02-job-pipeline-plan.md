# Job Pipeline Automation - SDLC Plan

## Issue: #13 [sdlc:plan] Job Pipeline Automation
## Parent: #2 Job Pipeline Automation

### Requirements (from parent issue)
- Daily job search automation
- Search LinkedIn Jobs/Indeed
- Save to tracker CSV
- Filter by remote/hybrid, entry-level
- Exclude insurance
- Priority: High

### Acceptance Criteria
- [ ] Search LinkedIn Jobs for relevant positions
- [ ] Search Indeed for relevant positions
- [ ] Save results to tracker CSV
- [ ] Filter for remote/hybrid positions only
- [ ] Filter for entry-level positions only
- [ ] Exclude insurance industry positions
- [ ] CLI usage works
- [ ] Run as daily cron job

### Entry Points
- Input: config file for search terms/locations
- Output: tracker CSV file

### Test Plan
- Run with sample search terms → verify CSV output
- Verify filtering works correctly
- Verify insurance positions are excluded
- Verify CLI runs without errors

### Implementation Notes
- Use search SDKs or direct API calls
- Code at: job-pipeline/
- Output CSV: job-pipeline/tracker.csv
- Support config file for customization

---

## Detailed Implementation Specification

### File Structure
```
job-pipeline/
├── __init__.py
├── job_search.py          # Core search logic (ALREADY EXISTS)
├── job_search_test.py     # Unit tests (ALREADY EXISTS)
├── config.json           # Search configuration (ALREADY EXISTS)
├── tracker.csv           # Output (gitignored)
└── run_pipeline.py       # NEW: CLI entry point with cron support
```

### Classes & Modules

#### `Job` (dataclass - EXISTS)
```python
@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    source: str  # "LinkedIn" or "Indeed"
    date_posted: str
    description: str = ""
```

#### `JobSearchConfig` (EXISTS)
- Loads from `config.json`
- Defaults for all fields
- Fields: `search_terms`, `locations`, `exclude_keywords`, `experience_levels`, `output_file`

#### `LinkedInJobSearcher` (NEEDS WORK)
- Currently stubbed with `pass`
- Should use LinkedIn Jobs scraping or unofficial API
- User-Agent rotation for anti-scraping
- Rate limiting: max 1 request/2 seconds

#### `IndeedJobSearcher` (EXISTS - functional)
- Uses `requests + BeautifulSoup`
- Filters in `_should_exclude()`
- Extracts: title, company, location, date, URL

#### `CSVTracker` (EXISTS - functional)
- Append-only to prevent duplicates (checks URL)
- CSV injection protection via `sanitize_csv_field()`
- Fieldnames: date_found, title, company, location, url, source, date_posted, status

### Configuration Schema (config.json)
```json
{
  "search_terms": ["software engineer", "frontend developer", ...],
  "locations": ["remote", "hybrid"],
  "exclude_keywords": ["insurance", "state farm", "allstate", ...],
  "experience_levels": ["entry", "junior", "associate"],
  "output_file": "tracker.csv",
  "linkedin": {
    "enabled": true,
    "max_results_per_term": 25
  },
  "indeed": {
    "enabled": true,
    "max_results_per_term": 25
  }
}
```

### CLI Interface
```bash
# Basic usage
python job_search.py

# Custom config
python job_search.py --config custom-config.json

# Custom output
python job_search.py --config-output my-tracker.csv
```

### Filtering Logic
1. **Remote/Hybrid**: Set via location parameter in search URL
2. **Entry-Level**: Set `explvl=entry_level` in Indeed params
3. **Exclude Insurance**: Case-insensitive substring match on company name

### Error Handling
- Network errors: log to stderr, continue with other sources
- Parse errors: skip individual job cards, log warning
- Empty results: print "No new jobs to save"

### Cron Setup (sdlc:ops stage)
```bash
# Daily at 9 AM
0 9 * * * cd /home/chronos/career-transition && .venv/bin/python job-pipeline/job_search.py >> job-pipeline/cron.log 2>&1
```

### Dependencies
- `requests` - HTTP library
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser for BeautifulSoup
