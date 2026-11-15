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


def add_totals(summary):
    # monthly team totals are not in the csv, commentary.py sums them the same way
    employees = summary[summary["section"] == "employee"]
    totals = employees.groupby("month")[["planned_hours", "actual_hours"]].sum()
    totals = totals.reset_index()
    totals["section"] = "total"
    return pd.concat([summary, totals], ignore_index=True)


def split_sentences(text):
    lines = [line for line in text.splitlines() if not line.startswith("#")]
    # split only on a dot followed by a space, so 57.5 stays in one piece
    return re.split(r"(?<=[.!?])\s+", " ".join(lines))


def find_months(sentence, known_months):
    months = re.findall(r"\d{4}-\d{2}", sentence)
    for number, name in enumerate(MONTH_NAMES.split("|"), start=1):
        if name in sentence:
            # the model often drops the year ("July saw..."), so only the month number is compared
            months += [m for m in known_months if m.endswith(f"-{number:02d}")]
    return months


def rows_for_sentence(sentence, rows):
    names = [name for name in rows["name"].dropna().unique() if name in sentence]
    months = find_months(sentence, rows["month"].dropna().unique())
    if names:
        rows = rows[rows["name"].isin(names)]
    if months:
        keep = rows["month"].isin(months)
        if names:
            # project rows have no month, they are picked by name only
            keep = keep | rows["month"].isna()
        rows = rows[keep]
    return rows


def allowed_numbers(rows):
    allowed = set()
    for col in ["planned_hours", "actual_hours", "weekly_hours"]:
        for value in rows[col].dropna():
            allowed.add(float(value))
    return allowed


def check_numbers(numbers, allowed):
    result = []
    for number in numbers:
        result.append((number, float(number) in allowed))
    return result


def main():
    rows = add_totals(pd.read_csv(SUMMARY_PATH))
    with open(COMMENTARY_PATH, encoding="utf-8") as f:
        text = f.read()

    result = []
    for sentence in split_sentences(text):
        # a number must come from the rows of the project, person or month in its sentence
        allowed = allowed_numbers(rows_for_sentence(sentence, rows))
        result += check_numbers(find_numbers(sentence), allowed)

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
