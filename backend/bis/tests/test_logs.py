import json
import logging
from collections import namedtuple
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest
from bis import logs
from bis.mcp import BISTools


@pytest.fixture
def log(tmp_path):
    handler = logs.HourlyFileHandler(tmp_path)
    handler.setFormatter(logs.JsonFormatter())
    logger = logging.Logger("test")
    logger.addHandler(handler)
    logs.start_trace("test")
    yield logger
    handler.close()


def entries(directory):
    return [
        json.loads(line)
        for path in sorted(directory.glob("*.jsonl"))
        for line in path.read_text().splitlines()
    ]


def test_record_is_one_json_line_in_the_file_of_its_utc_hour(log, tmp_path):
    log.info("Sent email", extra={"data": {"template_id": 162}, "duration": 0.5004})

    [path] = tmp_path.iterdir()
    assert path.name == datetime.now(UTC).strftime("%Y-%m-%dT%H.jsonl")
    [entry] = entries(tmp_path)
    assert entry["message"] == "Sent email"
    assert entry["level"] == "INFO"
    assert entry["data"] == {"template_id": 162}
    assert entry["duration"] == 0.5
    assert "traceback" not in entry


def test_exception_class_joins_the_message_and_its_text_goes_to_data(log, tmp_path):
    try:
        raise ValueError("row 17 is broken")
    except ValueError:
        log.exception("Failed importing donations")

    [entry] = entries(tmp_path)
    assert entry["message"] == "Failed importing donations: ValueError"
    assert entry["data"] == {"error": "row 17 is broken"}
    assert "ValueError: row 17 is broken" in entry["traceback"]


def test_emails_and_phones_are_masked_everywhere(log, tmp_path):
    try:
        raise ValueError("Key (email)=(jan.novak@example.com) already exists")
    except ValueError:
        log.exception(
            "Failed saving user",
            extra={"data": {"nested": ["call +420 777 123 456", {"id": 5}]}},
        )

    [line] = next(tmp_path.iterdir()).read_text().splitlines()
    assert "example.com" not in line
    assert "777" not in line
    entry = json.loads(line)
    assert entry["data"]["error"] == "Key (email)=(<email>) already exists"
    assert entry["data"]["nested"] == ["call <phone>", {"id": 5}]


def test_oversized_data_is_truncated(log, tmp_path):
    log.info("Big", extra={"data": {"payload": "x" * 50_000}})

    [entry] = entries(tmp_path)
    assert len(entry["data"]["truncated"]) == logs.DATA_LIMIT
    assert entry["data_size"] > 50_000


def test_request_id_is_shared_within_a_trace(log, tmp_path):
    logs.start_trace("cron")
    log.info("one")
    log.info("two")
    logs.start_trace("cron")
    log.info("three")

    one, two, three = (entry["request_id"] for entry in entries(tmp_path))
    assert one == two != three
    assert one.startswith("cron_")


def test_user_id_comes_from_the_authenticated_request(log, tmp_path):
    logs.start_trace("request", SimpleNamespace(user=SimpleNamespace(id=12)))
    log.info("with user")
    logs.start_trace("cron")
    log.info("without user")
    log.info("about a user", extra={"user_id": "34"})

    with_user, without_user, about_user = entries(tmp_path)
    assert with_user["user_id"] == "12"
    assert about_user["user_id"] == "34"
    assert "user_id" not in without_user


def test_operation_logs_start_and_finish_or_failure(caplog):
    caplog.set_level(logging.INFO)
    with logs.operation("running nightly command"):
        pass
    with pytest.raises(RuntimeError), logs.operation("running daily command"):
        raise RuntimeError

    assert [record.getMessage() for record in caplog.records] == [
        "Started running nightly command",
        "Finished running nightly command",
        "Started running daily command",
        "Failed running daily command",
    ]


Usage = namedtuple("Usage", "total used free")


def test_free_space_deletes_only_the_oldest_files_needed(tmp_path, monkeypatch):
    for hour in ("01", "02", "03", "04"):
        (tmp_path / f"2026-01-01T{hour}.jsonl").write_bytes(b"x" * 8192)
    block_size = (tmp_path / "2026-01-01T01.jsonl").stat().st_blocks * 512
    # reports the same usage however much was deleted, like zfs does at first
    monkeypatch.setattr(
        logs.shutil,
        "disk_usage",
        lambda directory: Usage(1000, 900 + block_size + 1, 0),
    )

    logs.free_space(tmp_path, keep="2026-01-01T04.jsonl")

    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "2026-01-01T03.jsonl",
        "2026-01-01T04.jsonl",
    ]


def test_free_space_never_deletes_the_current_file(tmp_path, monkeypatch):
    (tmp_path / "2026-01-01T01.jsonl").write_bytes(b"x")
    monkeypatch.setattr(
        logs.shutil, "disk_usage", lambda directory: Usage(1000, 1000, 0)
    )

    logs.free_space(tmp_path, keep="2026-01-01T01.jsonl")

    assert len(list(tmp_path.iterdir())) == 1


def test_free_space_keeps_everything_under_the_limit(tmp_path, monkeypatch):
    (tmp_path / "2026-01-01T01.jsonl").write_bytes(b"x")
    monkeypatch.setattr(
        logs.shutil, "disk_usage", lambda directory: Usage(1000, 899, 101)
    )

    logs.free_space(tmp_path, keep="2026-01-01T02.jsonl")

    assert len(list(tmp_path.iterdir())) == 1


@pytest.fixture
def stored(tmp_path):
    records = {
        "2026-03-01T09": [
            ("09:10", "INFO", "request", "Finished GET request on a with 200", 1),
            ("09:20", "ERROR", "root", "Failed job sync: HTTPError", None),
        ],
        "2026-03-01T10": [
            ("10:05", "INFO", "root", "Sent email", 1),
            ("10:30", "INFO", "root", "Sent email", 2),
        ],
    }
    for hour, rows in records.items():
        lines = [
            json.dumps(
                {
                    "time": f"2026-03-01T{time}:00.000+00:00",
                    "level": level,
                    "logger": logger,
                    "message": message,
                    "user_id": user_id,
                    "data": {"template_id": 162},
                    "traceback": "Traceback",
                }
            )
            for time, level, logger, message, user_id in rows
        ]
        (tmp_path / f"{hour}.jsonl").write_text("\n".join(lines) + "\n")
    return tmp_path


WHOLE_DAY = {"since": "2026-03-01T00:00+00:00", "until": "2026-03-02T00:00+00:00"}


def messages(rows):
    return [row["message"] for row in rows]


def test_search_lists_newest_first_without_tracebacks(stored):
    rows = logs.search(stored, **WHOLE_DAY)

    assert [row["time"][11:16] for row in rows] == ["10:30", "10:05", "09:20", "09:10"]
    assert all("traceback" not in row for row in rows)
    assert "traceback" in logs.search(stored, **WHOLE_DAY, tracebacks=True)[0]


def test_search_respects_the_time_range_within_a_file(stored):
    rows = logs.search(
        stored, since="2026-03-01T09:15+00:00", until="2026-03-01T10:10+00:00"
    )

    assert [row["time"][11:16] for row in rows] == ["10:05", "09:20"]


def test_search_reads_a_naive_time_as_prague(stored):
    rows = logs.search(stored, since="2026-03-01T11:20", until="2026-03-01T12:00")

    assert [row["time"][11:16] for row in rows] == ["10:30"]


def test_search_filters(stored):
    assert messages(logs.search(stored, **WHOLE_DAY, level="error")) == [
        "Failed job sync: HTTPError"
    ]
    assert len(logs.search(stored, **WHOLE_DAY, message="sent EMAIL")) == 2
    assert len(logs.search(stored, **WHOLE_DAY, text="httperror")) == 1
    assert len(logs.search(stored, **WHOLE_DAY, filters={"user_id": 1})) == 2
    assert len(logs.search(stored, **WHOLE_DAY, filters={"user_id": [1, 2]})) == 3
    assert len(logs.search(stored, **WHOLE_DAY, filters={"data.template_id": 162})) == 4
    assert len(logs.search(stored, **WHOLE_DAY, exclude={"logger": "request"})) == 3


def test_search_pages(stored):
    rows = logs.search(stored, **WHOLE_DAY, limit=2, offset=1)

    assert [row["time"][11:16] for row in rows] == ["10:05", "09:20"]
    with pytest.raises(ValueError):
        logs.search(stored, **WHOLE_DAY, limit=logs.MAX_ROWS + 1)


def test_search_groups(stored):
    assert logs.search(stored, **WHOLE_DAY, group_by=["message"])[0] == {
        "message": "Sent email",
        "count": 2,
    }
    assert logs.search(stored, **WHOLE_DAY, group_by=["hour", "level"]) == [
        {"hour": "2026-03-01T10", "level": "INFO", "count": 2},
        {"hour": "2026-03-01T09", "level": "ERROR", "count": 1},
        {"hour": "2026-03-01T09", "level": "INFO", "count": 1},
    ]


@pytest.mark.parametrize(
    "is_superuser,is_bot,allowed",
    [(False, False, False), (True, False, True), (False, True, True)],
)
def test_mcp_logs_are_for_superusers_and_the_bot(
    stored, settings, is_superuser, is_bot, allowed
):
    settings.LOG_DIR = stored
    user = SimpleNamespace(id=1, is_superuser=is_superuser, is_bot=is_bot)
    tools = BISTools(request=SimpleNamespace(user=user))

    result = tools.logs(**WHOLE_DAY)

    assert isinstance(result, list) is allowed
