"""The old database's free-text box fields, read into the new box's values."""

import re

from categories.models import NestBoxType

HoleShape = NestBoxType.HoleShape

OVAL = re.compile(r"(\d+(?:\.\d+)?)[x/*](\d+(?:\.\d+)?)(cm|mm)?")
ROUND = re.compile(r"(\d+(?:\.\d+)?)(cm|mm)?")
OPEN_FRONT_SHARE = re.compile(r"[123]/[234]")


def _millimetres(number, unit=None):
    """The form asked for cm; `0,32` were decimetres and `14,00` centimetres."""
    if unit == "mm":
        return number
    if unit == "cm":
        return number * 10
    if number < 1:
        return number * 100
    if number <= 15:
        return number * 10
    return number


def parse_hole(raw):
    """(shape, narrowest width in mm or None), or None when it can't be read."""
    value = (raw or "").strip().lower().replace(" ", "").replace(",", ".")
    if value in ("ovál", "oval"):
        return HoleShape.OVAL, None
    if value == "holobudka" or OPEN_FRONT_SHARE.fullmatch(value):
        return HoleShape.OPEN_FRONT, None
    if value.startswith("podéln"):
        return HoleShape.SLIT, None
    if match := OVAL.fullmatch(value):
        widths = float(match[1]), float(match[2])
        if max(widths) < 15:
            widths = tuple(width * 10 for width in widths)
        return HoleShape.OVAL, round(min(widths))
    if match := ROUND.fullmatch(value):
        return HoleShape.ROUND, round(_millimetres(float(match[1]), match[2]))
    return None


ENTRY_TIME = re.compile(r"^(\S+) - \d{4}-\d\d-\d\d \d\d:\d\d:\d\d$")
RENUMBERED = re.compile(r"^(\S+) \(do (\d{4}) č\. (\S+)\)$")
UNNAMED = "bez označení"


def parse_name(raw):
    """(name, previous name or "", owner note or "") from the old number field."""
    value = raw.strip()
    if match := ENTRY_TIME.match(value):
        return match[1], "", ""
    if match := RENUMBERED.match(value):
        return match[1], f"{match[3]} (do {match[2]})", ""
    if " " in value and not re.search(r"\d", value):
        return UNNAMED, "", value
    return value, "", ""
