# Evaluation Rubric Guide

This file is loaded only on the **first run** of a role, when you need to build the rubric from scratch. On subsequent runs, the saved `evaluation_rubric.json` is used directly — no need to read this file.

---

## Step 1 — Classify JD requirements

Split every requirement into **objective** (measurable/verifiable) vs **qualitative** (judgment-based):

- **Objective**: specific tools, years of experience ("5+ years"), degree ("LLB"), certifications
- **Qualitative**: soft skills ("strong communication"), traits ("entrepreneurial mindset"), behavioural expectations ("works under pressure"), culture fit

---

## Step 2 — Auto-draft rubrics for qualitative items

For each qualitative item, create a 4-band scoring guide with this pattern:

```
Requirement: "Strong communication skills"  (maps to: Overall Fit)

8–10 pts → Clear evidence: led cross-functional presentations, authored reports/blogs,
           managed client communications, or explicitly cited in achievements.
 5–7 pts → Moderate: collaborative projects, team-lead roles, stakeholder interaction mentioned.
 2–4 pts → Implied by role but no specific examples.
 0–1 pts → No evidence.
```

**Mapping rule** (which dimension to assign each qualitative item to):
- Skills-related soft skills (e.g. analytical thinking) → Skills Match
- Experience-related behaviours (e.g. managing teams) → Experience
- Education-related attributes → Education
- Personality / culture / general fit → Overall Fit

---

## Step 3 — Present to user for confirmation

Show all qualitative items and suggested rubrics. Ask:
> "I've drafted scoring rubrics above. Type **OK** to accept, or tell me what to adjust."

**Wait for the user's response before saving.**

---

## Rubric JSON template

Save to `<JD folder>/evaluation_rubric.json`:

```json
{
  "position_title": "<role title>",
  "jd_file": "<jd filename>",
  "created_at": "<YYYY-MM-DD>",
  "hard_rejection_rules": [
    {
      "rule": "experience_range",
      "description": "Candidates outside this experience window are auto-rejected",
      "min_years": 0,
      "max_years": 99
    },
    {
      "rule": "industry_filter",
      "description": "Candidates not from these industries are auto-rejected",
      "accepted_industries": []
    }
  ],
  "scoring_dimensions": {
    "skills_match": {
      "max_points": 40,
      "critical_skills": [],
      "preferred_skills": [],
      "scoring_bands": {
        "35-40": "All critical skills present + most preferred",
        "25-34": "All critical skills + some preferred, or 1 critical missing",
        "15-24": "Most critical skills present but notable gaps",
        "0-14":  "Several critical skills missing"
      }
    },
    "experience": {
      "max_points": 30,
      "required_years": "<from JD>",
      "scoring_bands": {
        "27-30": "Meets/exceeds requirement with highly relevant experience",
        "20-26": "Slightly under requirement or partially relevant",
        "10-19": "Significantly under requirement",
        "0-9":   "Well below requirement or irrelevant experience"
      }
    },
    "education": {
      "max_points": 20,
      "required": "<degree/field from JD>",
      "scoring_bands": {
        "18-20": "Exact match or higher degree in required field",
        "12-17": "Closely related field or equivalent",
        "6-11":  "Different but partially relevant degree",
        "0-5":   "Unrelated degree or no degree where required"
      }
    },
    "overall_fit": {
      "max_points": 10,
      "scoring_bands": {
        "8-10": "Strong evidence of fit: communication, tech savviness, cultural alignment",
        "5-7":  "Moderate evidence; fits the role profile reasonably well",
        "2-4":  "Weak evidence beyond technical qualifications",
        "0-1":  "Poor overall fit"
      }
    }
  }
}
```

---

## Hard rejection rules

If the user specifies hard filters (experience ceiling, industry list, etc.), capture them in `hard_rejection_rules`. Candidates failing any rule get total_score = 0 and their summary begins with `AUTO-REJECTED:` followed by the reason. They are still added to the tracker so the full candidate pool is visible.
