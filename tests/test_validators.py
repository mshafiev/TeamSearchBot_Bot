import pytest
from app.validators import is_valid_user_id, validate_message_text, parse_age, parse_date_dmy


def test_is_valid_user_id():
    assert is_valid_user_id("123")
    assert not is_valid_user_id("")
    assert not is_valid_user_id(None)
    assert not is_valid_user_id("abc")


def test_validate_message_text():
    ok, val = validate_message_text(" hello ")
    assert ok and val == "hello"

    ok, val = validate_message_text(" ")
    assert not ok and val is None

    ok, val = validate_message_text(None)
    assert not ok and val is None

    long = "x" * 1200
    ok, val = validate_message_text(long)
    assert not ok and len(val) == 1000


def test_parse_age():
    assert parse_age("14") == 14
    assert parse_age("100") == 100
    assert parse_age("13") is None
    assert parse_age("101") is None
    assert parse_age("abc") is None


def test_parse_date_dmy():
    assert parse_date_dmy("01-12-2000") == (1, 12, 2000)
    assert parse_date_dmy("32-12-2000") is None
    assert parse_date_dmy("01-13-2000") is None
    assert parse_date_dmy("01-12-1800") is None
    assert parse_date_dmy("bad") is None