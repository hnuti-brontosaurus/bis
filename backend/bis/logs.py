"""Structured logs: one JSON line per record, one file per hour, read back by MCP.

The MCP `logs` tool is the only reader, so records are shaped for filtering:

- the message is a fixed phrase, optionally ending in a value from a small
  closed set (a command name, a status code); filter on the phrase
- everything that varies per occurrence goes into `extra={"data": {...}}`
- `data` refers to people by id, never by name or contact, so the files hold no
  PII by construction; exception texts are written by libraries and can quote
  an address, which is why emails and phone numbers are masked on the way in
- an operation that takes time logs `Started` / `Finished` / `Failed` around
  one shared core, see `operation`
"""

import json
import logging
import re
import shutil
import traceback
from collections import Counter
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import UTC, datetime, timedelta
from pathlib import Path
from time import monotonic
from uuid import uuid4
from zoneinfo import ZoneInfo

from django.conf import settings
from django.utils.functional import SimpleLazyObject

HOUR_FORMAT = "%Y-%m-%dT%H"
CAPACITY_LIMIT = 0.9
DATA_LIMIT = 20_000
MAX_ROWS = 1000

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"\+\d[\d ]{7,}\d")

request_id = ContextVar("request_id", default=None)
current_request = ContextVar("current_request", default=None)


def start_trace(kind, request=None):
    """Give every record logged from here on in this context one shared id."""
    request_id.set(f"{kind}_{uuid4().hex}")
    current_request.set(request)


def current_user_id():
    """Return the id of the request's user, once something has authenticated it.

    Session auth leaves `request.user` lazy until first use and DRF replaces it
    with the token's user inside the view. Resolving the lazy object here would
    run a query from inside a log call, so a record logged before either
    happened simply has no user.
    """
    request = current_request.get()
    user = getattr(request, "user", None)
    if isinstance(user, SimpleLazyObject):
        user = getattr(request, "_cached_user", None)
    user_id = getattr(user, "id", None)
    return user_id and str(user_id)


@contextmanager
def operation(name, **data):
    """Log `Started`, then `Finished` or `Failed`, around the block.

    `name` is the shared core, a short lowercase phrase such as
    `running nightly command`, so that one filter follows the operation.
    """
    logging.info(f"Started {name}", extra={"data": data})
    start = monotonic()
    try:
        yield
    except Exception:
        logging.exception(
            f"Failed {name}", extra={"data": data, "duration": monotonic() - start}
        )
        raise
    logging.info(
        f"Finished {name}", extra={"data": data, "duration": monotonic() - start}
    )


def mask_pii(value):
    if isinstance(value, str):
        return PHONE.sub("<phone>", EMAIL.sub("<email>", value))
    if isinstance(value, dict):
        return {key: mask_pii(item) for key, item in value.items()}
    if isinstance(value, list):
        return [mask_pii(item) for item in value]
    return value


def describe(record):
    """Return the masked message, data and traceback of a record.

    The class of a logged exception is the bounded part of it, so it joins the
    message; its text varies per occurrence and goes to `data`.
    """
    message = record.getMessage()
    data = getattr(record, "data", None) or {}
    error = record.exc_info[1] if record.exc_info else None
    trace = None
    if error is not None:
        message = f"{message}: {type(error).__name__}"
        data = {"error": str(error), **data}
        trace = mask_pii("".join(traceback.format_exception(error)))

    data = mask_pii(json.loads(json.dumps(data, default=str)))
    return mask_pii(message), data, trace


def local_time(record):
    return datetime.fromtimestamp(record.created, ZoneInfo(settings.TIME_ZONE))


class JsonFormatter(logging.Formatter):
    def format(self, record):
        message, data, trace = describe(record)
        duration = getattr(record, "duration", None)
        entry = {
            "time": local_time(record).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "message": message,
            "request_id": request_id.get(),
            "user_id": getattr(record, "user_id", None) or current_user_id(),
            "duration": duration and round(duration, 3),
            "data": data or None,
            "traceback": trace,
        }

        serialized = json.dumps(data, ensure_ascii=False)
        if len(serialized) > DATA_LIMIT:
            entry["data"] = {"truncated": serialized[:DATA_LIMIT]}
            entry["data_size"] = len(serialized)

        return json.dumps(
            {key: value for key, value in entry.items() if value is not None},
            ensure_ascii=False,
        )


class ConsoleFormatter(logging.Formatter):
    def format(self, record):
        message, data, trace = describe(record)
        parts = [
            local_time(record).strftime("%Y-%m-%d %H:%M:%S"),
            record.levelname,
            message,
        ]
        if data:
            parts.append(json.dumps(data, ensure_ascii=False))
        if trace:
            parts.append("\n" + trace.rstrip())
        return " ".join(parts)


def free_space(directory, keep):
    """Delete the oldest log files while the volume is over `CAPACITY_LIMIT`.

    The amount to free is computed once and counted down by file size, rather
    than re-reading the usage after each delete: a filesystem that frees blocks
    asynchronously (zfs, which the production volume is) keeps reporting the
    old usage for a few seconds, and a loop trusting it would delete every file.
    """
    usage = shutil.disk_usage(directory)
    excess = usage.used - CAPACITY_LIMIT * usage.total
    for path in sorted(directory.glob("*.jsonl")):
        if excess <= 0 or path.name >= keep:
            return
        excess -= path.stat().st_blocks * 512
        path.unlink()


class HourlyFileHandler(logging.Handler):
    """Append each record to `<directory>/<utc hour>.jsonl`.

    The file is unbuffered and opened for append, so a record is one `write`
    call and lines from the server and from a management command running next
    to it never interleave.
    """

    def __init__(self, directory):
        super().__init__()
        self.directory = Path(directory)
        self.path = None
        self.file = None

    def emit(self, record):
        try:
            hour = datetime.fromtimestamp(record.created, UTC)
            path = self.directory / f"{hour.strftime(HOUR_FORMAT)}.jsonl"
            if path != self.path:
                self.open(path)
            self.file.write(self.format(record).encode() + b"\n")
        except Exception:
            self.handleError(record)

    def open(self, path):
        self.close_file()
        self.directory.mkdir(parents=True, exist_ok=True)
        free_space(self.directory, keep=path.name)
        self.file = path.open("ab", buffering=0)
        self.path = path

    def close_file(self):
        if self.file:
            self.file.close()
        self.file = self.path = None

    def close(self):
        self.close_file()
        super().close()


def parse_time(value):
    time = datetime.fromisoformat(value)
    if time.tzinfo is None:
        time = time.replace(tzinfo=ZoneInfo(settings.TIME_ZONE))
    return time


def read(directory, since, until):
    """Yield the raw line and the parsed entry of each record, newest first."""
    for path in sorted(Path(directory).glob("*.jsonl"), reverse=True):
        hour = datetime.strptime(path.stem, HOUR_FORMAT).replace(tzinfo=UTC)
        if hour > until or hour + timedelta(hours=1) <= since:
            continue
        for line in reversed(path.read_text().splitlines()):
            entry = json.loads(line)
            if since <= datetime.fromisoformat(entry["time"]) <= until:
                yield line, entry


def field(entry, path):
    if path == "hour":
        return entry["time"][:13]
    if path == "day":
        return entry["time"][:10]
    value = entry
    for key in path.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    return value


def field_in(entry, path, expected):
    expected = expected if isinstance(expected, list) else [expected]
    return field(entry, path) in expected


def search(
    directory,
    since=None,
    until=None,
    level="INFO",
    message=None,
    text=None,
    filters=None,
    exclude=None,
    group_by=None,
    limit=100,
    offset=0,
    tracebacks=False,
):
    if limit > MAX_ROWS:
        raise ValueError(f"limit must be at most {MAX_ROWS}, use offset to page")

    until = parse_time(until) if until else datetime.now(UTC)
    since = parse_time(since) if since else until - timedelta(days=1)
    levels = logging.getLevelNamesMapping()
    minimal_level = levels[level.upper()]

    def matching():
        for line, entry in read(directory, since, until):
            if levels[entry["level"]] < minimal_level:
                continue
            if message and message.lower() not in entry["message"].lower():
                continue
            if text and text.lower() not in line.lower():
                continue
            if not all(field_in(entry, *item) for item in (filters or {}).items()):
                continue
            if any(field_in(entry, *item) for item in (exclude or {}).items()):
                continue
            yield entry

    if group_by:
        counts = Counter(
            tuple(json.dumps(field(entry, path)) for path in group_by)
            for entry in matching()
        )
        return [
            {**dict(zip(group_by, map(json.loads, group))), "count": count}
            for group, count in counts.most_common(MAX_ROWS)
        ]

    rows = []
    for index, entry in enumerate(matching()):
        if index >= offset + limit:
            break
        if index >= offset:
            if not tracebacks:
                entry.pop("traceback", None)
            rows.append(entry)
    return rows
