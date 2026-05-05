# Phase 1: Data Consolidation Prompt

## Objective
Convert raw career transcript into structured, professional JSON data.

## Input
- Candidate's raw word-vomit transcript
- Existing resume (if any)
- LinkedIn profile (if any)
- Job preferences, location, salary range

## Task Steps

### 1. Extract Responsibilities
Read through the transcript and extract ALL responsibilities, duties, and accomplishments.

### 2. Categorize
Place each responsibility into one of these categories:
- **Operations**: Day-to-day workflow management
- **Data & Reporting**: Metrics, analysis, tracking
- **Pipeline Management**: Sales pipeline, customer pipeline
- **Training & Documentation**: SOPs, manuals, onboarding
- **Customer Service**: Client interactions, support
- **Auditing & Quality Control**: Compliance, accuracy checks
- **Remote Work & Communication**: Virtual meetings, remote collaboration
- **Leadership & Collaboration**: Team support, mentoring

### 3. Remove Emotional Language
Strip out negative framing:
- ❌ "tired of the industry"
- ❌ "overworked"
- ❌ "14 to 18 hour days"
- ❌ "no room to grow"

Replace with professional positioning:
- ✅ "seeking growth in a new industry"
- ✅ "ready to apply transferable skills"
- ✅ "looking for broader advancement opportunities"

### 4. Professional Reframe
Translate each item to professional language using the formula:
> Action verb + responsibility + business impact

## Missing Data to Gather
If not in transcript, create questions for:
- Number of agents/customers handled daily/weekly
- CRM/systems used (Salesforce, etc.)
- Number of templates/manuals created
- Supervised or mentored anyone
- Exact title and company name
- Employment dates

## Output: structured-experience.json
```json
{
  "operations": [],
  "data_reporting": [],
  "pipeline": [],
  "training_docs": [],
  "customer_service": [],
  "auditing": [],
  "remote_work": [],
  "leadership": [],
  "tools": [],
  "soft_skills": [],
  "missing_data": []
}
```

## Acceptance Criteria
- [ ] All raw experience categorized
- [ ] No negative employer language remains
- [ ] Professional positioning statements included
- [ ] Missing data list created