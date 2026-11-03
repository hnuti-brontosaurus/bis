"""Reads the rows of an Adminer / MariaDB dump without running any of it."""

import re
from collections import defaultdict

INSERT = re.compile(r"^INSERT INTO `(\w+)` \(([^)]*)\) VALUES\s*", re.MULTILINE)
VALUE = re.compile(r"\s*('(?:[^'\\]|\\.|'')*'|NULL|-?[0-9.]+)\s*([,)])")
ESCAPES = {"n": "\n", "r": "\r", "t": "\t", "0": "\0", "Z": "\x1a"}
ESCAPE = re.compile(r"\\(.)|''", re.DOTALL)


class DumpError(ValueError):
    pass


def _unquote(token):
    if token == "NULL":
        return None
    if not token.startswith("'"):
        return token
    return ESCAPE.sub(
        lambda match: ESCAPES.get(match[1], match[1]) if match[1] else "'",
        token[1:-1],
    )


def _rows(text, position):
    """The tuples of one INSERT starting at `position`, and where it ended."""
    rows = []
    while True:
        while text[position] in " \t\r\n,":
            position += 1
        if text[position] == ";":
            return rows, position
        if text[position] != "(":
            raise DumpError(f"expected a row at offset {position}")
        position += 1
        row = []
        while True:
            match = VALUE.match(text, position)
            if not match:
                raise DumpError(f"unreadable value at offset {position}")
            row.append(_unquote(match[1]))
            position = match.end()
            if match[2] == ")":
                break
        rows.append(row)


def parse_dump(text, tables):
    """{table: [row dicts]} for the given tables, every value a string or None."""
    result = defaultdict(list)
    position = 0
    while match := INSERT.search(text, position):
        table = match[1]
        columns = [column.strip(" `") for column in match[2].split(",")]
        rows, position = _rows(text, match.end())
        if table in tables:
            for row in rows:
                if len(row) != len(columns):
                    raise DumpError(f"{table}: row of {len(row)} values")
                result[table].append(dict(zip(columns, row)))
    if missing := set(tables) - set(result):
        raise DumpError(f"tables missing from the dump: {sorted(missing)}")
    return dict(result)
