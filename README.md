# Resource Tracker Reporting

A small practice project around a resource tracker: who works on which project, how many hours were planned and how many were actually logged. Python scripts generate the data, build a summary, draft slide commentary through the Gemini API and then check that every number in the commentary really comes from the summary.

All data is synthetic. Names are generated with Faker, there are no real people or companies.

## What is inside

- `src/generate_data.py` - creates 40 employees, 12 projects and their monthly assignments for May-October 2026. Saves `data/resource_tracker.xlsx` and three csv files. The seed is fixed, so the numbers are the same after every run.
- `src/summary.py` - reads the xlsx and writes `reports/summary.csv`: hours per project, load per employee per month, and the months where someone worked more than 40 hours a week.
- `src/commentary.py` - sends three small tables to Gemini and saves a 2-3 sentence commentary for each slide to `reports/commentary.md`.
- `src/check_commentary.py` - finds all numbers in the commentary and checks them against the summary.
- `tests/` - tests for the load calculation and for the number check.

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

Only `commentary.py` needs the key. The `data/` folder is not in Git, so run `generate_data.py` first.

## Results

- 281 assignment rows, which give 192 employee-month rows in the summary.
- Planned hours over all projects: 24360, actual: 24382.
- The busiest month is 2026-07 with 5905 planned and 5794 actual hours. The quietest is 2026-05 with 2400 planned and 2328 actual.
- 26 of 40 employees have at least one month above 40 hours a week, 55 such months in total. The highest value is 57.5 hours a week.
- The check found 19 numbers in the commentary, all 19 match the summary.
- 3 tests pass.