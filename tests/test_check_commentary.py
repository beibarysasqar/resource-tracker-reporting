import pandas as pd

from src.check_commentary import (allowed_numbers, check_numbers, find_numbers,
                                  rows_for_sentence)

ROWS = pd.DataFrame([
    {"section": "employee", "name": "Test Person", "month": "2026-05",
     "planned_hours": 160, "actual_hours": 180, "weekly_hours": 45.0},
    {"section": "employee", "name": "Other Person", "month": "2026-05",
     "planned_hours": 150, "actual_hours": 200, "weekly_hours": 50.0},
    {"section": "employee", "name": "Test Person", "month": "2026-06",
     "planned_hours": 170, "actual_hours": 220, "weekly_hours": 55.0},
])


def test_check_numbers():
    allowed = {420.0, 56.0, 57.5}

    result = check_numbers(["420", "999", "56", "57.5"], allowed)

    assert result == [("420", True), ("999", False), ("56", True), ("57.5", True)]


def test_find_numbers_skips_dates():
    text = (
        "## Slide 1\n\n"
        "In 2026-07 the peak was 57.5 hours, and in September 2026 "
        "the team logged 4,255 hours.\n"
    )

    assert find_numbers(text) == ["57.5", "4255"]


def test_number_of_another_person_does_not_match():
    sentence = "Test Person reached 50.0 hours in 2026-05."

    allowed = allowed_numbers(rows_for_sentence(sentence, ROWS))

    assert check_numbers(find_numbers(sentence), allowed) == [("50.0", False)]


def test_number_of_another_month_does_not_match():
    sentence = "Test Person reached 55.0 hours in May 2026."

    allowed = allowed_numbers(rows_for_sentence(sentence, ROWS))

    assert check_numbers(find_numbers(sentence), allowed) == [("55.0", False)]


def test_right_person_and_month_match():
    sentence = "Test Person reached 45.0 hours in May 2026."

    allowed = allowed_numbers(rows_for_sentence(sentence, ROWS))

    assert check_numbers(find_numbers(sentence), allowed) == [("45.0", True)]


def test_month_name_without_year():
    sentence = "In June Test Person reached 55.0 hours, not 45.0."

    allowed = allowed_numbers(rows_for_sentence(sentence, ROWS))

    assert check_numbers(find_numbers(sentence), allowed) == [("55.0", True), ("45.0", False)]
