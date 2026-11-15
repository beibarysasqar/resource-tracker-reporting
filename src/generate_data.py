import os
import random
from datetime import date

import pandas as pd
from faker import Faker

# fixed seed so the numbers in the report stay the same after every run
SEED = 42
N_EMPLOYEES = 40
DATA_DIR = "data"

MONTHS = ["2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"]

ROLES = {
    "Engineering": ["Developer", "QA Engineer", "DevOps Engineer"],
    "Analytics": ["Data Analyst", "BI Analyst"],
    "Design": ["UX Designer", "UI Designer"],
    "Operations": ["Project Coordinator", "Business Analyst"],
}

PROJECT_NAMES = [
    "Atlas Migration", "Billing Revamp", "Customer Portal", "Data Lake Setup",
    "Mobile App Refresh", "Warehouse Dashboard", "HR Self-Service", "Payment Gateway",
    "Reporting Automation", "Inventory Sync", "Onboarding Portal", "Search Upgrade",
]

random.seed(SEED)
Faker.seed(SEED)
fake = Faker("en_US")


def make_employees():
    rows = []
    for i in range(1, N_EMPLOYEES + 1):
        department = random.choice(list(ROLES.keys()))
        # a few part-time people, otherwise everyone has the same capacity
        capacity = 80 if random.random() < 0.15 else 160
        rows.append({
            "employee_id": f"E{i:03d}",
            "full_name": fake.first_name() + " " + fake.last_name(),
            "department": department,
            "role": random.choice(ROLES[department]),
            "grade": random.choices(["Junior", "Middle", "Senior"], weights=[3, 4, 2])[0],
            "capacity_hours": capacity,
            "start_date": fake.date_between(date(2019, 1, 1), date(2026, 4, 30)),
        })
    return pd.DataFrame(rows)


def make_projects():
    rows = []
    for i, name in enumerate(PROJECT_NAMES, start=1):
        start = random.randint(0, 2)
        end = random.randint(start + 2, len(MONTHS) - 1)
        if end < len(MONTHS) - 1:
            status = "Completed"
        else:
            status = random.choices(["Active", "On hold"], weights=[5, 1])[0]
        rows.append({
            "project_id": f"P{i:02d}",
            "project_name": name,
            "department": random.choice(list(ROLES.keys())),
            "start_month": MONTHS[start],
            "end_month": MONTHS[end],
            "status": status,
        })
    return pd.DataFrame(rows)


def make_assignments(employees, projects):
    rows = []
    for _, emp in employees.iterrows():
        n_projects = random.randint(1, 3)
        picked = projects.sample(n_projects, random_state=random.randint(0, 10000))
        for _, proj in picked.iterrows():
            for month in MONTHS:
                # string compare works because months are in YYYY-MM format
                if month < proj["start_month"] or month > proj["end_month"]:
                    continue
                share = emp["capacity_hours"] / n_projects
                planned = round(share * random.uniform(0.7, 1.3) / 5) * 5
                actual = round(planned * random.uniform(0.8, 1.2))
                rows.append({
                    "assignment_id": f"A{len(rows) + 1:04d}",
                    "employee_id": emp["employee_id"],
                    "project_id": proj["project_id"],
                    "month": month,
                    "planned_hours": planned,
                    "actual_hours": actual,
                })
    return pd.DataFrame(rows)


def add_budget(projects, assignments):
    planned = assignments.groupby("project_id")["planned_hours"].sum()
    budgets = []
    for project_id in projects["project_id"]:
        total = planned.get(project_id, 0)
        # budget is based on planned hours, otherwise budget vs actual makes no sense
        budgets.append(round(total * random.uniform(0.95, 1.15) / 10) * 10)
    projects["budget_hours"] = budgets
    return projects


def save(employees, projects, assignments):
    os.makedirs(DATA_DIR, exist_ok=True)
    xlsx_path = os.path.join(DATA_DIR, "resource_tracker.xlsx")
    with pd.ExcelWriter(xlsx_path) as writer:
        employees.to_excel(writer, sheet_name="employees", index=False)
        projects.to_excel(writer, sheet_name="projects", index=False)
        assignments.to_excel(writer, sheet_name="assignments", index=False)
    employees.to_csv(os.path.join(DATA_DIR, "employees.csv"), index=False)
    projects.to_csv(os.path.join(DATA_DIR, "projects.csv"), index=False)
    assignments.to_csv(os.path.join(DATA_DIR, "assignments.csv"), index=False)


def main():
    employees = make_employees()
    projects = make_projects()
    assignments = make_assignments(employees, projects)
    projects = add_budget(projects, assignments)
    save(employees, projects, assignments)
    print("employees:", len(employees))
    print("projects:", len(projects))
    print("assignments:", len(assignments))


if __name__ == "__main__":
    main()
