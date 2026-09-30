import logging

import pytest
from bis.logs import HourlyFileHandler


@pytest.fixture(autouse=True, scope="session")
def no_log_files():
    """Keep what the tests log out of the log files the MCP `logs` tool reads."""
    root = logging.getLogger()
    for handler in root.handlers:
        if isinstance(handler, HourlyFileHandler):
            root.removeHandler(handler)
