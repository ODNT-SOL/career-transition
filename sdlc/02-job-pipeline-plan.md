# Job Pipeline Automation - SDLC Plan

## Issue: #13 [sdlc:plan] Job Pipeline Automation
## Parent: #2 Job Pipeline Automation

### Requirements (from parent issue):
- Daily job search automation
- Search LinkedIn Jobs/Indeed
- Save to tracker CSV
- Filter by remote/hybrid, entry-level
- Exclude insurance
- Priority: High

### Acceptance Criteria:
- [ ] Search LinkedIn Jobs for relevant positions
- [ ] Search Indeed for relevant positions
- [ ] Save results to tracker CSV
- [ ] Filter for remote/hybrid positions only
- [ ] Filter for entry-level positions only
- [ ] Exclude insurance industry positions
- [ ] CLI usage works
- [ ] Run as daily cron job

### Entry Points:
- Input: config file for search terms/locations
- Output: tracker CSV file

### Test Plan:
- Run with sample search terms → verify CSV output
- Verify filtering works correctly
- Verify insurance positions are excluded
- Verify CLI runs without errors

### Implementation Notes:
- Use search SDKs or direct API calls
- Code at: job-pipeline/
- Output CSV: job-pipeline/tracker.csv
- Support config file for customization