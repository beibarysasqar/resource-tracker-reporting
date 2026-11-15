# Resource Tracker Reporting

A project around a resource tracker: who works on which project, how many hours were planned and how many were actually logged. It has an Excel tracker, a PowerPoint report, onboarding documents and files for a SharePoint library. Python scripts generate the data, build a summary, draft slide commentary through the Gemini API and then check that every number in the commentary really comes from the summary.

## What is inside

- `src/generate_data.py` - creates 40 employees, 12 projects and their monthly assignments for May-October 2026. Saves `data/resource_tracker.xlsx` and three csv files. The seed is fixed, so the numbers are the same after every run.
- `src/summary.py` - reads the xlsx and writes `reports/summary.csv`: hours per project, load per employee per month, and the months where someone worked more than 40 hours a week.
- `src/commentary.py` - sends three small tables to Gemini and saves a 2-3 sentence commentary for each slide to `reports/commentary.md`.
- `src/check_commentary.py` - finds all numbers in the commentary and checks each one against the summary rows of the project, person or month named in the same sentence.
- `tests/` - tests for the load calculation and for the number check.

The check has a limit: it compares a number with all projects, people and months named in the same sentence. If a sentence names two people, a number that belongs to one of them also passes for the other.

## Excel, PowerPoint and Microsoft 365 part

- `data/tracker_with_formulas.xlsx` - the tracker with formulas (the `data/` folder is not in Git). `Projects_summary` uses SUMIFS and INDEX/MATCH for hours and budget per project. `Load` shows weekly hours per employee and month, and conditional formatting marks the cells above the 40 hour limit. `Checks` compares four Excel totals with `reports/summary.csv`, all four are OK.
- `reports/Resource_Report_May-Oct_2026.pptx` - a 6-slide resource report. Slides 3-5 use the commentary from `reports/commentary.md`.
- `docs/` - an onboarding checklist with 15 steps and a welcome guide for a new team member.
- `m365/sharepoint_library/` - 25 documents for a SharePoint library: reports, policies, templates, project briefs and onboarding files, named by one naming convention.
- `m365/library_metadata.xlsx` - metadata for each of the 25 documents: document type, project, department, owner, status and review date.
- `m365/planner_tasks.xlsx` - 25 tasks of this project for a Planner board with the buckets To do, In progress, Review and Done.

## How to run

```
pip install -r requirements.txt
cp .env.example .env
```

Put your Gemini API key into `.env`, then:

```
python src/generate_data.py
python src/summary.py
python src/commentary.py
python src/check_commentary.py
python -m pytest tests/
```

## Results

- 281 assignment rows, which give 192 employee-month rows in the summary.
- Planned hours over all projects: 24360, actual: 24382.
- The busiest month is 2026-07 with 5905 planned and 5794 actual hours. The quietest is 2026-05 with 2400 planned and 2328 actual.
- 26 of 40 employees have at least one month above 40 hours a week, 55 such months in total. The highest value is 57.5 hours a week.
- The check found 19 numbers in the commentary, all 19 match the summary.
- 7 tests pass.