# Phase 2: Role Positioning Prompt

## Objective
Align candidate experience to realistic target roles outside insurance.

## Target Roles

### Primary (highest priority)
- Operations Coordinator
- Operations Analyst
- Business Analyst (Entry/Mid-Level)
- Customer Success Specialist
- Project Coordinator
- Training Coordinator
- Enablement Specialist

### Secondary
- Administrative Operations Manager
- Client Success Coordinator
- Implementation Coordinator
- Process Improvement Associate
- Support Operations Specialist

## Task Steps

### 1. Compare to Job Descriptions
Search for real job descriptions in target roles. Note:
- Required skills
- Preferred experience
- Keywords that appear frequently

### 2. Determine Role Fit
Score each target role:
- 70%+ match = strong fit
- 50-69% = possible with adjustments
- <50% = unlikely, skip

### 3. Create Positioning Statements

**Primary Positioning:**
> Operations and process improvement professional with experience building workflows, analyzing performance data, supporting customer-facing teams, creating training documentation, and improving day-to-day business operations.

**Secondary Positionings:**
- **Business Analyst**: Data-minded operations professional skilled in reporting, workflow analysis, pipeline tracking, and translating business needs into organized processes.
- **Customer Success**: Customer-focused operations professional with strong communication skills, experience handling high-volume client interactions, and a track record of improving internal support processes.
- **Training Coordinator**: Training and documentation professional experienced in building manuals, templates, and onboarding resources that help teams operate more consistently.

### 4. Build Keyword Bank
Extract keywords per role:
- Operations: workflow, optimization, process improvement, efficiency
- Data: reporting, analysis, metrics, Excel, dashboard
- Customer: support, success, engagement, satisfaction
- Project: coordination, timeline, stakeholders, planning

## Output: role-positioning.json
```json
{
  "primary_role": "",
  "secondary_roles": [],
  "positioning_statements": {
    "primary": "",
    "business_analyst": "",
    "customer_success": "",
    "training": ""
  },
  "keyword_bank": {
    "operations": [],
    "data": [],
    "customer": [],
    "project": []
  }
}
```

## Acceptance Criteria
- [ ] At least one role with 70%+ match
- [ ] Clear primary positioning
- [ ] Keyword bank for each target role