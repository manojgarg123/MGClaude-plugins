---
name: shortlisting
description: >
  Resume shortlisting and scoring skill — use this whenever the user wants to screen, score, rank,
  or evaluate resumes/CVs against a job description. Triggers include: "shortlist resumes",
  "screen candidates", "rank applicants", "score CVs", "match resumes to JD", "evaluate candidates",
  "which resumes are best for this role", or any time the user provides a job description and wants
  to assess one or more resumes against it. Also trigger for "add this resume to the tracker",
  "process this CV", or "update my candidate list". Extracts candidate details, scores on skills,
  experience, education and fit, updates a ranked Excel tracker, and generates an HTML dashboard.
  Skips already-processed resumes and uses parallel agents for high-volume batches.
---

# Resume Shortlisting Skill

Screen and rank candidates by scoring resumes against a job description. A consistent **evaluation rubric** is built once and reused across every subsequent run, so all candidates are always judged on the same criteria regardless of when they apply.

The skill is designed to be **run multiple times on the same folder** — it checks the tracker for already-scored resumes and skips them.

## Standard Folder Structure

```
<Role>/
├── JD/  (or "Job Description/")
│   ├── <jd_file>.pdf
│   ├── evaluation_rubric.json   ← built on first run, sole source of truth thereafter
│   └── jd_summary.json          ← cached JD extract (only used during first-run rubric build)
├── Resumes/
├── Tracker/
│   ├── Candidate_Tracker.xlsx
│   └── token_usage.json         ← running token log (updated each run)
└── Dashboard/
    └── <PositionTitle>_Dashboard.html
```

---

## Step 0 — Pre-flight: count and deduplicate

**0a. List all resume files** (pdf, docx, doc, txt):
```bash
ls "<resumes-folder>"
```

**0b. Check the tracker** for already-processed resumes:
```bash
python scripts/check_processed.py --tracker "<role-folder>/Tracker/Candidate_Tracker.xlsx"
```
Prints one filename per line (empty if no tracker yet).

**0c. Compute new resumes** = all resumes − already-processed ones.

**0d. Report to the user:**
```
Found N resumes total.
  - Already processed (skipping): X  →  [filenames]
  - New resumes to process: Y  →  [filenames]
```
If Y = 0, tell the user everything is already scored and stop. Offer to regenerate the dashboard.

**0e. Record the run start timestamp** — you'll need it for token logging at the end:
```python
from datetime import datetime
RUN_ID = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
```

---

## Step 1 — Load or build the evaluation rubric

The rubric is the single source of truth for all scoring — it fully encodes everything relevant from the JD (required skills, experience bands, education criteria, hard rejection rules). Check for it first, and only read the JD if it doesn't exist yet.

```bash
ls "<JD folder>/evaluation_rubric.json" 2>/dev/null && echo "EXISTS" || echo "NOT_FOUND"
```

### If EXISTS (subsequent runs)
Read `evaluation_rubric.json`, load into context, and tell the user:
> "Using existing evaluation rubric from `evaluation_rubric.json`."

**Proceed directly to Step 2. Do not load `jd_summary.json` or the JD file** — the rubric already contains everything needed for scoring and hard rejection.

### If NOT_FOUND (first run only)
The rubric doesn't exist yet, so the JD must be read to build it.

**1a. Extract the JD** — check for a cached summary first to avoid re-parsing the raw PDF:
```bash
ls "<JD folder>/jd_summary.json" 2>/dev/null && echo "CACHED" || echo "EXTRACT"
```
- **If CACHED**: read `jd_summary.json` and load into context.
- **If EXTRACT**: run:
  ```bash
  python scripts/extract_text.py "<path-to-jd-file>"
  ```
  Then save a compact structured summary to `<JD folder>/jd_summary.json`:
  ```json
  {
    "role_title": "...",
    "required_experience_years": "...",
    "required_education": "...",
    "critical_skills": ["..."],
    "preferred_skills": ["..."],
    "key_responsibilities": ["..."],
    "nice_to_have": ["..."]
  }
  ```
  Caching this means any future first-run re-attempts load ~200 tokens of structured data rather than ~1,500 tokens of raw PDF text.

**1b. Build the rubric**: Read `references/rubric_guide.md` for full instructions on building the rubric from the JD summary, presenting it to the user, and saving `evaluation_rubric.json`. **Wait for user confirmation before proceeding.**

> Once the rubric is confirmed and saved, `jd_summary.json` is no longer consulted on future runs. The rubric is self-contained from this point forward.

---

## Step 2 — Hard rejection screening (fast pass)

Before doing any detailed scoring, apply the rubric's `hard_rejection_rules` to each new resume. Extract just the text, then check:
- Does experience fall within `min_years`–`max_years`?
- Is the candidate's industry in `accepted_industries`?

Run the extraction for all new resumes in parallel where possible:
```bash
python scripts/extract_text.py "<resume-path>"
```

Candidates failing any hard rule → mark as `AUTO-REJECTED` immediately (total_score = 0). No further scoring needed. Note the rejection reason clearly.

This early-exit saves scoring work on clearly disqualified candidates.

---

## Step 3 — Score passing candidates

For each candidate that passed hard rejection, produce scores across all four dimensions in a **single compact pass**. Output a JSON block like this (reason for each score in one tight sentence, not an essay):

```json
{
  "name": "Candidate Name",
  "skills_score": 28,
  "skills_rationale": "Strong litigation + contract drafting; no healthcare compliance or IPR.",
  "experience_score": 22,
  "experience_rationale": "14 yrs, DGM level; team of 5; industry mostly FMCG.",
  "education_score": 15,
  "education_rationale": "LLB from regional university; no LLM.",
  "fit_score": 7,
  "fit_rationale": "Manupatra + SCC Online; public speaker at FICCI.",
  "total_score": 72,
  "key_strengths": "comma, separated, phrases",
  "key_gaps": "comma, separated, phrases",
  "summary": "One-sentence verdict + recommendation."
}
```

Keep rationale brief — one sentence per dimension is enough and reduces output tokens significantly.

**Status thresholds:**
- ≥ 75 → Shortlisted
- 50–74 → On Hold
- < 50 → Not Suitable
- 0 (rejected) → Auto-Rejected

---

## Step 4 — Update the tracker

For each candidate (passing or rejected), call:
```bash
python scripts/update_excel.py \
  --tracker "<role-folder>/Tracker/Candidate_Tracker.xlsx" \
  --position-title "<role>" \
  --name "<name>" \
  --email "<email or N/A>" \
  --phone "<phone or N/A>" \
  --current-org "<org or N/A>" \
  --qualification "<highest degree>" \
  --years-experience "<number>" \
  --resume "<filename>" \
  --skills-score <int> \
  --experience-score <int> \
  --education-score <int> \
  --fit-score <int> \
  --total-score <int> \
  --strengths "<comma-separated phrases>" \
  --gaps "<comma-separated phrases>" \
  --summary "<one-sentence summary>"
```

> **Important:** `update_excel.py` works only with the Python `exec()` pattern or direct Python3 call (not `python` which may be Python 2). If argparse doesn't parse when called via shell, use:
> ```python
> python3 -c "
> import sys, types
> # load the script's functions via exec()
> exec(open('scripts/update_excel.py').read(), namespace)
> args = types.SimpleNamespace(...)
> "
> ```

The script auto-sorts all rows by total_score and re-assigns ranks after every write.

If the tracker file already exists and cannot be overwritten (permission/lock issue), write to `Candidate_Tracker_v<N>.xlsx` in the same folder and note this to the user. Always use the most recent `_v<N>` file as the source for subsequent reads.

---

## Step 5 — Generate the dashboard

```bash
python scripts/generate_dashboard.py \
  --tracker "<role-folder>/Tracker/Candidate_Tracker.xlsx" \
  --output  "<role-folder>/Dashboard/<PositionTitle>_Dashboard.html"
```

Do **not** read `generate_dashboard.py` into context — just call it as a subprocess.

---

## Step 6 — Log token usage

After all candidates are processed, collect the input files used this run and call:

```bash
python scripts/log_tokens.py \
  --log-file    "<role-folder>/Tracker/token_usage.json" \
  --run-id      "<RUN_ID from Step 0e>" \
  --position    "<role title>" \
  --new-resumes <Y> \
  --input-files "<rubric.json>,<resume1.pdf>,<resume2.pdf>,..." \
  --output-text "<paste all generated strengths+gaps+summaries concatenated>"
```

The script appends a record with input