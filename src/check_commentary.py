import re

import pandas as pd

SUMMARY_PATH = "reports/summary.csv"
COMMENTARY_PATH = "reports/commentary.md"

MONTH_NAMES = ("January|February|March|April|May|June|July|August|"
               "September|October|November|December")


def find_numbers(text):
    lines = [line for line in text.splitlines() if not line.startswith("#")]
    text = "\n".join(lines)
    # dates like 2026-07 or "September 2026" are not report figures
    text = re.sub(r"\d{4}-\d{2}", " ", text)
    text = re.sub(rf"({MONTH_NAMES}) \d{{4}}", " ", text)
    # the model sometimes writes 4,255 instead of 4255
    text = re.sub(r"(?<=\d),(?=\d{3})", "", text)
    return re.findall(r"\d+(?:\.\d+)?", text)


def allowed_numbers(summary):
    allowed = set()
    for col in ["planned_hours", "actual_hours", "weekly_hours"]:
        for value in summary[col].dropna():
            allowed.add(float(value))

    # monthly team totals are not in the csv, commentary.py sums them the same way
    employees = summary[summary["section"] == "employee"]
    totals = employees.groupby("month")[["planned_hours", "actual_hours"]].sum()
    for col in ["planned_hours", "actual_hours"]:
        for value in totals[col]:
            allowed.add(float(value))
    return allowed


def check_numbers(numbers, allowed):
    result = []
    for number in numbers:
        result.append((number, float(number) in allowed))
    return result


def main():
    summary = pd.read_csv(SUMMARY_PATH)
    with open(COMMENTARY_PATH, encoding="utf-8") as f:
        text = f.read()

    result = check_numbers(find_numbers(text), allowed_numbers(summary))
    matched = 0
    for number, ok in result:
        if ok:
            matched += 1
            print(number, " match")
        else:
            print(number, " no match")

    print("matched:", matched)
    print("not matched:", len(result) - matched)


if __name__ == "__main__":
    main()
