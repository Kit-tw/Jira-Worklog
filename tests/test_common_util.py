import re
import pytest
from util.common_util import date_str_to_iso, get_currentdate_forentry, now_greater_than_date


def test_date_str_to_iso():
    result = date_str_to_iso("01/06/2025")
    assert result == "2025-06-01T00:00:00.000+0000"


def test_date_str_to_iso_end_of_year():
    result = date_str_to_iso("31/12/2024")
    assert result == "2024-12-31T00:00:00.000+0000"


def test_now_greater_than_past_date():
    assert now_greater_than_date("01/01/2000", "%d/%m/%Y") is True


def test_now_not_greater_than_future_date():
    assert now_greater_than_date("01/01/2099", "%d/%m/%Y") is False


def test_get_currentdate_format():
    result = get_currentdate_forentry()
    assert re.match(r'^\d{2}/\d{2}/\d{4}$', result)
