# Resume Shortlisting Plugin

Screen and rank job candidates by scoring resumes against a job description — consistently, at scale.

## What It Does

This plugin adds a **shortlisting skill** to Claude that automates the most time-consuming parts of hiring:

- Reads your job description and builds a structured **evaluation rubric** (once, reused forever)
- Scores each resume across four dimensions: **Skills**, **Experience**, **Education**, and **Fit**
- Applies **hard rejection rules** to instantly filter obviously unqualified candidates
- Updates a ranked **Excel tracker** (`.xlsx`) with every candidate's scores, strengths, and gaps
- Generates an **HTML dashboard** for at-a-glance hiring decisions
- **Skips already-processed resumes** — safe to re-run as new applications arrive

## How to Use

Once installed, just describe what you want in plain language. Claude will recognize phrases like:

- "Shortlist these resumes against the JD"
- "Screen the candidates in my folder"
- "Score these CVs and update the tracker"
- "Add this new resume to the shortlist"
- "Which applicants are best for this role?"

## Expected Folder Structure

Organize your hiring materials like this:

```
<Role>/
├── JD/
│   └── job_description.pdf
├── Resumes/
│   ├── candidate1.pdf
│   ├── candidate2.docx
│   └── ...
├── Tracker/          ← auto-created
└── Dashboard/        ← auto-created
```

Point Claude at your role folder and it handles the rest.

## Scoring System

| Dimension   | Max Points | What It Measures                        |
|-------------|------------|-----------------------------------------|
| Skills      | 40         | Match to required and preferred skills  |
| Experience  | 25         | Years, seniority, industry relevance    |
| Education   | 15         | Degree, institution, certifications     |
| Fit         | 20         | Tools, culture signals, extras          |
| **Total**   | **100**    |                                         |

**Decision thresholds:**
- ≥ 75 → **Shortlisted**
- 50–74 → **On Hold**
- < 50 → **Not Suitable**
- 0 → **Auto-Rejected** (failed hard rejection rules)

## Requirements

- Python 3 must be available in your environment
- Required Python packages: `openpyxl`, `pdfplumber`, `python-docx`

Install dependencies:
```bash
pip install openpyxl pdfplumber python-docx
```

## Output Files

| File | Description |
|------|-------------|
| `JD/evaluation_rubric.json` | The scoring rubric (built once, reused forever) |
| `Tracker/Candidate_Tracker.xlsx` | Ranked Excel sheet with all candidates |
| `Dashboard/<Role>_Dashboard.html` | Visual HTML dashboard |
| `Tracker/token_usage.json` | Running log of token usage per run |

---

Built with Claude Cowork.
