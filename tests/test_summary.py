import pandas as pd

from src.summary import load_by_employee


def test_load_one_employee():
    employees = pd.DataFrame([
        {"employee_id": "E001", "full_name": "Test Person"},
    ])
    assignments = pd.DataFrame([
        {"employee_id": "E001", "project_id": "P01", "month": "2026-05",
         "planned_hours": 90, "actual_hours": 100},
        {"employee_id": "E001", "project_id": "P02", "month": "2026-05",
         "planned_hours": 70, "actual_hours": 80},
    ])

    load = load_by_employee(assignments, employees)

    assert len(load) == 1
    assert load.loc[0, "planned_hours"] == 160
    assert load.loc[0, "actual_hours"] == 180
    assert load.loc[0, "weekly_hours"] == 45
