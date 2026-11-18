from datetime import datetime
from unittest.mock import MagicMock

import pytest

import util.cli_git_context as gc


def _entries(*dates):
    return [{"date": d} for d in dates]


@pytest.mark.parametrize("start, end, expected", [
    ((9, 0), (11, 15), gc.RangeTime("2h 15m", 135, 135, False)),
    ((9, 0), (10, 0), gc.RangeTime("1h", 60, 60, False)),
    ((9, 0), (9, 0), gc.RangeTime("1m", 1, 1, False)),
    ((8, 0), (16, 0), gc.RangeTime("8h", 480, 480, True)),
    ((8, 0), (17, 30), gc.RangeTime("8h", 480, 570, True)),
])
def test_combined_range_time(start, end, expected):
    day = datetime(2025, 3, 10)
    assert gc.combined_range_time(day.replace(hour=start[0], minute=start[1]),
                                  day.replace(hour=end[0], minute=end[1])) == expected


@pytest.mark.parametrize("dates, expected", [
    (("01/01/2025", "02/01/2025"), (2, 1)),                   # no today -> oldest
    (("T", "T"), (2, 1)),                                     # today is oldest -> oldest
    (("Y", "Y", "T", "T"), (3, 1)),                           # entry just before today
    (("Y", "T"), (2, 1)),
])
def test_default_range_numbers(dates, expected):
    assert gc.default_range_numbers(_entries(*dates), "T") == expected


def test_load_git_defaults_cleans_comment():
    git = MagicMock()
    git.get_git_detail.return_value = {
        "date": "10/03/2025", "time_spend": "45m", "time_spend_minutes": 45,
        "description": "commit: fix bug",
    }
    assert gc.load_git_defaults(git, "01/01/2025") == gc.GitDefaults("10/03/2025", "45m", "fix bug", 45)


def test_load_git_defaults_raises_through():
    git = MagicMock()
    git.get_git_detail.side_effect = Exception("boom")
    with pytest.raises(Exception, match="boom"):
        gc.load_git_defaults(git, "01/01/2025")


def test_fallback_issue_key():
    git = MagicMock()
    git.get_issueName.return_value = "PROJ-1"
    assert gc.fallback_issue_key(git) == "PROJ-1"
    git.get_issueName.side_effect = Exception("no repo")
    assert gc.fallback_issue_key(git) is None
