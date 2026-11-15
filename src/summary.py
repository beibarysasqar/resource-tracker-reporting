import os

import pandas as pd

XLSX_PATH = "data/resource_tracker.xlsx"
REPORT_PATH = "reports/summary.csv"

# the tracker has monthly hours only, so a week is taken as 1/4 of a month
WEEKS_IN_MONTH = 4
WEEKLY_LIMIT = 40

COLUMNS = ["section", "id", "name", "month", "planned_hours", "actual_hours", "weekly_hours"]


def load_data():
    employees = pd.read_excel(XLSX_PATH, sheet_name="employees")
    projects = pd.read_excel(XLSX_PATH, sheet_name="projects")
    assignments = pd.read_excel(XLSX_PATH, sheet_name="assignments")
    return employees, projects, assignments


def hours_by_project(assignments, projects):
    hours = assignments.groupby("project_id")[["planned_hours", "actual_hours"]].sum()
    hours = hours.reset_index()
    return hours.merge(projects[["project_id", "project_name"]], on="project_id")


def load_by_employee(assignments, employees):
    # one person can be on several projects in the same month
    load = assignments.groupby(["employee_id", "month"])[["planned_hours", "actual_hours"]].sum()
    load = load.reset_index()
    load = load.merge(employees[["employee_id", "full_name"]], on="employee_id")
    load["weekly_hours"] = load["actual_hours"] / WEEKS_IN_MONTH
    return load


def find_overloaded(load):
    return load[load["weekly_hours"] > WEEKLY_LIMIT]


def build_summary(by_project, load, overloaded):
    proj = by_project.rename(columns={"project_id": "id", "project_name": "name"})
    proj["section"] = "project"

    emp = load.rename(columns={"employee_id": "id", "full_name": "name"})
    emp["section"] = "employee"

    over = overloaded.rename(columns={"employee_id": "id", "full_name": "name"})
    over["section"] = "overloaded"

    summary = pd.concat([proj, emp, over], ignore_index=True)
    return summary[COLUMNS]


def main():
    employees, projects, assignments = load_data()
    by_project = hours_by_project(assignments, projects)
    load = load_by_employee(assignments, employees)
    overloaded = find_overloaded(load)

    summary = build_summary(by_project, load, overloaded)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    summary.to_csv(REPORT_PATH, index=False)

    print("projects:", len(by_project))
    print("employee months:", len(load))
    print("overloaded months:", len(overloaded))
    print("overloaded people:", overloaded["employee_id"].nunique())


if __name__ == "__main__":
    main()
