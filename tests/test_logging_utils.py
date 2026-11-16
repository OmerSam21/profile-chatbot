import json
import logging
from unittest.mock import patch

import pytest

from logging_utils import ConsoleFormatter, JSONFormatter, get_logger


def _record(extra_data: dict | None = None) -> logging.LogRecord:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "Answer generated", None, None)
    if extra_data is not None:
        record.extra_data = extra_data
    return record


def test_console_formatter_appends_extra_data():
    assert ConsoleFormatter("%(message)s").format(_record({"attempt": 1})) == 'Answer generated | {"attempt": 1}'


def test_console_formatter_without_extra_data():
    assert ConsoleFormatter("%(message)s").format(_record()) == "Answer generated"


def test_console_formatter_keeps_hebrew_readable():
    assert "שלום" in ConsoleFormatter("%(message)s").format(_record({"question": "שלום"}))


@pytest.mark.parametrize("key, expected", [
    ("message", "Answer generated"),
    ("level", "INFO"),
    ("extra_data", {"attempt": 2}),
])
def test_json_formatter_fields(key, expected):
    assert json.loads(JSONFormatter().format(_record({"attempt": 2})))[key] == expected


@patch("logging_utils.LOG_FILE", "")
def test_get_logger_does_not_duplicate_handlers():
    get_logger("dup-check")
    assert len(get_logger("dup-check").handlers) == 1
