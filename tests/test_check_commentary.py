from src.check_commentary import check_numbers, find_numbers


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
