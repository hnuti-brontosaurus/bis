import sys
from types import ModuleType

import pytest
from bis.scheduler import is_running_under_server


@pytest.fixture(autouse=True)
def no_run_main(monkeypatch):
    monkeypatch.delenv("RUN_MAIN", raising=False)


@pytest.mark.parametrize(
    "argv,run_main,expected",
    [
        (["manage.py", "migrate"], None, False),
        (["manage.py", "shell"], None, False),
        # runserver's autoreloader runs the app in two processes and both reach
        # ready(); only the serving child gets RUN_MAIN. Starting in both gives
        # two scheduler threads, so every scheduled command fires twice.
        (["manage.py", "runserver", "0:8000"], None, False),
        (["manage.py", "runserver", "0:8000"], "true", True),
        # --noreload has no child and so never sets RUN_MAIN.
        (["manage.py", "runserver", "--noreload", "0:8000"], None, True),
    ],
)
def test_scheduler_starts_only_in_the_serving_process(
    monkeypatch, argv, run_main, expected
):
    monkeypatch.setattr(sys, "argv", argv)
    if run_main is not None:
        monkeypatch.setenv("RUN_MAIN", run_main)

    assert is_running_under_server() is expected


def test_scheduler_starts_under_gunicorn(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["gunicorn"])
    monkeypatch.setitem(sys.modules, "gunicorn", ModuleType("gunicorn"))

    assert is_running_under_server() is True
