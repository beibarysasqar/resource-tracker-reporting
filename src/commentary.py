import os

import pandas as pd
import requests
from dotenv import load_dotenv

SUMMARY_PATH = "reports/summary.csv"
OUT_PATH = "reports/commentary.md"

MODEL = "gemini-3.5-flash-lite"
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def project_table(summary):
    rows = summary[summary["section"] == "project"]
    return rows[["name", "planned_hours", "actual_hours"]].to_csv(index=False)


def monthly_table(summary):
    # 192 employee rows are too much for one slide, so the prompt gets team totals per month
    rows = summary[summary["section"] == "employee"]
    totals = rows.groupby("month")[["planned_hours", "actual_hours"]].sum()
    return totals.reset_index().to_csv(index=False)


def overloaded_table(summary):
    rows = summary[summary["section"] == "overloaded"]
    return rows[["name", "month", "weekly_hours"]].to_csv(index=False)


def build_prompt(title, table):
    return (
        f"Write a commentary for a PowerPoint slide titled '{title}'.\n"
        "Write 2-3 sentences in plain business English.\n"
        "Use only the numbers from the table below, do not round them "
        "and do not calculate new ones.\n"
        "No bullet points, no headings.\n\n"
        f"{table}"
    )


def ask_gemini(prompt, api_key):
    # key goes in the header, in the URL it would show up in error messages
    headers = {"x-goog-api-key": api_key}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    response = requests.post(API_URL, headers=headers, json=body, timeout=60)
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()


def main():
    load_dotenv()
    api_key = os.environ["GEMINI_API_KEY"]
    summary = pd.read_csv(SUMMARY_PATH)

    slides = [
        ("Project hours: plan vs actual", project_table(summary)),
        ("Team load by month", monthly_table(summary)),
        ("Overloaded employees", overloaded_table(summary)),
    ]

    text = ""
    for title, table in slides:
        comment = ask_gemini(build_prompt(title, table), api_key)
        text += f"## {title}\n\n{comment}\n\n"

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print("slides:", len(slides))


if __name__ == "__main__":
    main()
