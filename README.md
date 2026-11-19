# Resource Tracker Reporting

Resource trackers: who is working on what project, how many hours were planned and how many were actually recorded. It has an Excel tracker, PowerPoint report, built-in documents and files for the SharePoint library. Python scripts generate the data, create a summary, write comments on the slides via the Gemini API, and then check that all the numbers in the comments are actually from the summary.

## What is inside

### Python part

| Path | What it does |
|------|--------------|
| `src/generate_data.py` | Creates 40 employees, 12 projects and their monthly assignments for May-October 2026. Saves `data/resource_tracker.xlsx` and three csv files. The seed is fixed, so the numbers are the same after every run. |
| `src/summary.py` | Reads the xlsx and writes `reports/summary.csv`: hours per project, load per employee per month, and the months where someone worked more than 40 hours a week. |
| `src/commentary.py` | Sends three small tables to Gemini and saves a 2-3 sentence commentary for each slide to `reports/commentary.md`. |
| `src/check_commentary.py` | Finds all numbers in the commentary and checks each one against the summary rows of the project, person or month named in the same sentence. |
| `tests/` | Tests for the load calculation and for the number check. |

### Excel, PowerPoint and Microsoft 365 part

| Path | What it does |
|------|--------------|
| `data/tracker_with_formulas.xlsx` | The tracker with formulas (the `data/` folder is not in Git). `Projects_summary` uses SUMIFS and INDEX/MATCH for hours and budget per project. `Load` shows weekly hours per employee and month, and conditional formatting marks the cells above the 40 hour limit. `Checks` compares four Excel totals with `reports/summary.csv`, all four are OK. |
| `reports/Resource_Report_May-Oct_2026.pptx` | A 6-slide resource report. Slides 3-5 use the commentary from `reports/commentary.md`. |
| `docs/` | An onboarding checklist with 15 steps and a welcome guide for a new team member. |
| `m365/sharepoint_library/` | 25 documents for a SharePoint library: reports, policies, templates, project briefs and onboarding files, named by one naming convention. |
| `m365/library_metadata.xlsx` | Metadata for each of the 25 documents: document type, project, department, owner, status and review date. |
| `m365/planner_tasks.xlsx` | 25 tasks of this project for a Planner board with the buckets To do, In progress, Review and Done. |

## Requirements

- Python.
- A Gemini API key in `.env` (copy `.env.example` and fill it in).

## How to run

```bash
pip install -r requirements.txt
cp .env.example .env                   # put your Gemini API key into .env
python src/generate_data.py            # data/resource_tracker.xlsx and csv files
python src/summary.py                  # reports/summary.csv
python src/commentary.py               # reports/commentary.md
python src/check_commentary.py         # checks the numbers in the commentary
python -m pytest tests/
```

## Results

- 281 assignment rows, which give 192 employee-month rows in the summary.
- Planned hours over all projects: 24360, actual: 24382.
- The busiest month is 2026-07 with 5905 planned and 5794 actual hours. The quietest is 2026-05 with 2400 planned and 2328 actual.
- 26 of 40 employees have at least one month above 40 hours a week, 55 such months in total. The highest value is 57.5 hours a week.
- The check found 19 numbers in the commentary, all 19 match the summary.
- 7 tests pass.
