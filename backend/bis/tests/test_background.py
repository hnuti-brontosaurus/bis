import logging
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

import django.db.utils
import pytest
from bis import background


@pytest.fixture
def executor():
    executor = ThreadPoolExecutor(max_workers=1)
    with patch.object(background, "_executor", executor):
        yield executor
    executor.shutdown(wait=True)


def run_task(fn, *args, **kwargs):
    background.run_in_background(fn, *args, **kwargs)
    # Single worker: a sentinel queued after the task proves the task finished.
    background._executor.submit(lambda: None).result(timeout=5)


def test_transient_connection_error_is_retried_once(executor):
    calls = []

    def task():
        calls.append(1)
        if len(calls) == 1:
            raise django.db.utils.OperationalError("server closed the connection")

    with patch.object(background, "close_old_connections") as close_mock:
        run_task(task)

    assert len(calls) == 2
    assert close_mock.call_count == 2


def test_persistent_connection_error_fails_after_two_attempts(executor, caplog):
    calls = []

    def task():
        calls.append(1)
        raise django.db.utils.OperationalError("server closed the connection")

    with caplog.at_level(logging.ERROR):
        run_task(task)

    assert len(calls) == 2
    exceptions = [r for r in caplog.records if r.exc_info is not None]
    assert len(exceptions) == 1
    assert "task failed" in exceptions[0].getMessage()


def test_first_failure_is_logged_as_warning_before_retry(executor, caplog):
    calls = []

    def task():
        calls.append(1)
        if len(calls) == 1:
            raise django.db.utils.OperationalError("connection already closed")

    with caplog.at_level(logging.WARNING):
        run_task(task)

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert len(warnings) == 1
    assert "retrying" in warnings[0].getMessage().lower()


def test_non_connection_error_is_not_retried(executor, caplog):
    calls = []

    def task():
        calls.append(1)
        raise ValueError("boom")

    with caplog.at_level(logging.ERROR):
        run_task(task)

    assert len(calls) == 1
    exceptions = [r for r in caplog.records if r.exc_info is not None]
    assert len(exceptions) == 1


def test_interface_error_is_retried(executor):
    calls = []

    def task():
        calls.append(1)
        if len(calls) == 1:
            raise django.db.utils.InterfaceError("connection already closed")

    run_task(task)

    assert len(calls) == 2


def test_retried_task_receives_args(executor):
    calls = []

    def task(arg, kwarg=None):
        calls.append((arg, kwarg))
        if len(calls) == 1:
            raise django.db.utils.OperationalError("server closed the connection")

    run_task(task, "a", kwarg="b")

    assert calls == [("a", "b"), ("a", "b")]
