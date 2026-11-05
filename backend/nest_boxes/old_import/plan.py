"""Turns the old tables into the new boxes and checks, without touching the database.

The rules are the ones decided in old_budky/docs (data-cleanup.md, notes-analysis.md,
new-model.md); implementation.md lists them.
"""

import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import date, datetime

from nest_boxes.models import Check, NestBox
from nest_boxes.old_import import notes
from nest_boxes.old_import.values import parse_hole, parse_name

TABLES = {
    "areas",
    "checks",
    "locations",
    "nestboxes",
    "nestbox_occupied",
    "nestbox_types",
    "users",
}
Status, Found, Cleaning = NestBox.Status, Check.Found, Check.Cleaning
Content, BoxLeft = Check.Content, Check.BoxLeft

# Locations whose name starts with this are statuses, not places
PSEUDO_LOCATION_PREFIX = "_"
RETIRED_LOCATION = "hřbitov"
# Mikulčický luh, 16 November 2025: whole areas saved with the default "Ne"
# while only part of the place was cleaned (data-cleanup.md B1)
SUSPECT_BATCH_DATE = date(2025, 11, 16)
SUSPECT_BATCH_MAX_OCCUPIED_SHARE = 0.25
# Who entered an area's data lately says who looks after it now
ENTRIES_SINCE = "2022"
OCCUPIED_FIELDS = {"ano", "myši", "vosy", "netopýři"}
FIELD_ANIMALS = {"myši": "mysi", "vosy": "vosy", "netopýři": "netopyri"}
OLD_TYPES = {
    "koňadra": "velky_sykornik",
    "modřinka": "maly_sykornik",
    "lejsek": "lejskovnik",
    "rehek": "polobudka",
    "strakapoud": "spackovnik",
    "špaček": "spackovnik",
    "šoupálek": "soupalkovnik",
    "sovinec": "sovinec",
    "poštolka": "polobudka",
    "doupňák": "doupnak",
    "dudek": "kavkovnik",
    "mandelík": "kavkovnik",
    "kavka": "kavkovnik",
    "netopýří": "netopyrnik",
    "skorec": "polobudka",
    "krutihlav": "velky_sykornik",
    "červenka": "polobudka",
    "veverka": "special",
}


@dataclass
class Reading:
    found: str
    cleaning: str = ""
    not_cleaned_reason: str | None = None
    contents: list = field(default_factory=list)
    occupants: set = field(default_factory=set)
    eggs_left: bool | None = None
    dead_birds: bool | None = None
    breeding_note: str = ""
    box_left: str = ""

    @property
    def is_inspection(self):
        return self.found != Found.FOUND or bool(self.contents)


@dataclass
class PlannedCheck:
    date: date
    made_at: datetime
    old_user_id: int | None
    note: str
    reading: Reading
    # A unit other than the area's did the work; the note only named it
    unit_name: str = ""


@dataclass
class PlannedBox:
    old_id: int | None
    old_area_id: int
    name: str
    location: tuple
    old_user_id: int | None
    created_at: datetime
    previous_names: str = ""
    note: str = ""
    elevation: int | None = None
    hole: tuple | None = None
    old_type: str | None = None
    opening: str = ""
    material: str = ""
    status: str = Status.IN_USE
    installed_on: date | None = None
    ended_on: date | None = None
    end_reason: str | None = None
    checks: list = field(default_factory=list)

    def end(self, day, reason):
        self.status, self.ended_on, self.end_reason = Status.ENDED, day, reason


@dataclass
class Plan:
    areas: dict
    boxes: list
    unit_names: set
    # old area id -> Counters of old user ids: since ENTRIES_SINCE, then all time
    entries: dict
    data_users: set
    inactive_users: set
    report: Counter
    undecided: dict  # what -> old box ids


def _date(value):
    return None if value.startswith("0000") else date.fromisoformat(value)


def _datetime(value, day):
    return (
        datetime.fromisoformat(value) if value else datetime(*day.timetuple()[:3], 12)
    )


def _int(value):
    return None if value is None else int(value)


def metres(a, b):
    lat1, lng1, lat2, lng2 = map(math.radians, (*a, *b))
    h = (
        math.sin((lat2 - lat1) / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    )
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def read_check(occupancy, note, repair_flag, unseen_default=False):
    """What one old check says, once its note takes precedence over its fields."""
    labels = notes.labels(note)
    if "not_reached" in labels:
        return Reading(found=Found.NOT_REACHED)
    if occupancy == "nenalezena" or "not_found" in labels:
        return Reading(found=Found.NOT_FOUND)

    bird = bool(labels & notes.BIRD_EVIDENCE) or (
        occupancy == "ano" and "other_animal" not in labels
    )
    animal = "other_animal" in labels or occupancy in FIELD_ANIMALS
    maintenance = (
        not occupancy and labels & notes.MAINTENANCE and not labels & notes.EVIDENCE
    )
    reading = Reading(found=Found.FOUND)
    if bird or animal:
        reading.contents = [Content.BIRD_NEST] * bird + [Content.OTHER_ANIMAL] * animal
    elif labels & notes.UNSEEN_INSIDE or occupancy == "nelze čistit":
        reading.contents = [Content.UNKNOWN]
    elif maintenance or occupancy == "stažena":
        reading.contents = []
    elif unseen_default and not occupancy:
        reading.contents = [Content.UNKNOWN]
    else:
        reading.contents = [Content.NOTHING]

    if "could_not_open" in labels:
        reading.cleaning = Cleaning.NOT_CLEANED
        reading.not_cleaned_reason = "could_not_open"
    elif labels & {"not_inspected", "not_cleaned"} or occupancy == "nelze čistit":
        reading.cleaning = Cleaning.NOT_CLEANED
        reading.not_cleaned_reason = notes.not_cleaned_reason(note)
    elif reading.contents and not unseen_default:
        reading.cleaning = Cleaning.CLEANED

    if bird:
        reading.occupants |= notes.birds(note)
    if animal:
        named = notes.animals(note)
        reading.occupants |= named or {FIELD_ANIMALS.get(occupancy, "nevim")}
        if occupancy == "vosy" and "srsni" in named:
            reading.occupants.discard("vosy")
    reading.eggs_left = True if "eggs" in labels else None
    reading.dead_birds = True if "dead_animal" in labels else None
    reading.breeding_note = (
        "úspěšné hnízdění"
        if "breeding_succeeded" in labels
        else (
            "neúspěšné hnízdění"
            if "breeding_failed" in labels
            else "pokus o obsazení"
            if "occupation_attempt" in labels
            else ""
        )
    )

    repaired = labels & {"repaired_done", "hung"} and not labels & {
        "repair_needed",
        "replace_needed",
    }
    if "taken_down" in labels or occupancy == "stažena":
        reading.box_left = BoxLeft.TAKEN_DOWN
    elif "replace_needed" in labels or (
        labels & notes.ENDING and not notes.asks_to_move(labels, note)
    ):
        reading.box_left = BoxLeft.NEEDS_REPLACING
    elif repaired:
        reading.box_left = BoxLeft.FINE
    elif labels & {"repair_needed", "fell_down"} or repair_flag == "1":
        reading.box_left = BoxLeft.NEEDS_REPAIR
    elif repair_flag is not None or labels:
        reading.box_left = BoxLeft.FINE
    return reading


def merge(checks):
    """One check per season: strongest contents, latest box state, the cleaning visit's date."""
    if len(checks) == 1:
        return checks[0]
    cleaned = [c for c in checks if c.reading.cleaning == Cleaning.CLEANED]
    chosen = (cleaned or checks)[-1]
    found = [c for c in checks if c.reading.found == Found.FOUND]
    occupied = [
        c
        for c in found
        if {Content.BIRD_NEST, Content.OTHER_ANIMAL} & set(c.reading.contents)
    ]
    evidence = (
        occupied
        or [c for c in found if Content.NOTHING in c.reading.contents]
        or [c for c in found if c.reading.contents]
    )
    contents = sorted({content for c in evidence for content in c.reading.contents})
    if occupied:
        contents = [
            c for c in contents if c in (Content.BIRD_NEST, Content.OTHER_ANIMAL)
        ]
    reading = replace(
        chosen.reading,
        found=Found.FOUND if found else chosen.reading.found,
        contents=contents,
        occupants=set().union(*(c.reading.occupants for c in occupied)),
        eggs_left=any(c.reading.eggs_left for c in checks) or None,
        dead_birds=any(c.reading.dead_birds for c in checks) or None,
        breeding_note="; ".join(
            dict.fromkeys(
                c.reading.breeding_note for c in checks if c.reading.breeding_note
            )
        ),
        box_left=checks[-1].reading.box_left,
    )
    if found and not chosen.reading.contents and contents:
        reading.cleaning = next(
            (c.reading.cleaning for c in evidence if c.reading.cleaning), ""
        )
        reading.not_cleaned_reason = next(
            (c.reading.not_cleaned_reason for c in evidence if c.reading.cleaning), None
        )
    note = "\n".join(f"{c.date.isoformat()}: {c.note}" for c in checks if c.note)
    return replace(chosen, reading=reading, note=note)


class Planner:
    def __init__(self, tables):
        self.tables = tables
        self.report = Counter()
        self.undecided = defaultdict(list)
        self.occupancy = {row["id"]: row["name"] for row in tables["nestbox_occupied"]}
        self.types = {row["id"]: row["name"] for row in tables["nestbox_types"]}
        locations = {row["id"]: row["name"] for row in tables["locations"]}
        self.areas = {int(row["id"]): row for row in tables["areas"]}
        self.area_location = {
            area_id: locations[row["id_location"]]
            for area_id, row in self.areas.items()
        }
        self.checks = defaultdict(list)
        for row in tables["checks"]:
            self.checks[row["id_nestbox"]].append(row)
        for rows in self.checks.values():
            rows.sort(key=lambda row: (row["date"], int(row["id"])))
        self.suspect_areas = self._suspect_batch_areas()

    def is_pseudo(self, area_id):
        return self.area_location[area_id].startswith(PSEUDO_LOCATION_PREFIX)

    def _suspect_batch_areas(self):
        batch = defaultdict(Counter)
        boxes = {row["id"]: row for row in self.tables["nestboxes"]}
        for row in self.tables["checks"]:
            if _date(row["date"]) == SUSPECT_BATCH_DATE:
                counts = batch[int(boxes[row["id_nestbox"]]["id_area"])]
                counts["checks"] += 1
                counts["occupied"] += (
                    self.occupancy.get(row["id_nestbox_occupied"]) in OCCUPIED_FIELDS
                )
        return {
            area
            for area, counts in batch.items()
            if counts["occupied"] / counts["checks"] < SUSPECT_BATCH_MAX_OCCUPIED_SHARE
        }

    def _is_placeholder(self, row, box):
        """The date hung, stored by the old form as a first check."""
        day = _date(row["date"])
        return (
            row["id_nestbox_occupied"] is None
            and not row["note"].strip()
            and row["needs_reparation"] in ("0", None)
            and (day is None or day <= date.fromisoformat(box["created"][:10]))
        )

    def _real_area(self, box, real_boxes):
        if not self.is_pseudo(int(box["id_area"])):
            return int(box["id_area"])
        location = float(box["gps_lat"]), float(box["gps_lng"])
        nearest = min(
            real_boxes,
            key=lambda other: metres(
                location, (float(other["gps_lat"]), float(other["gps_lng"]))
            ),
        )
        return int(nearest["id_area"])

    def _box(self, row, area_id):
        name, previous, name_note = parse_name(row["number"])
        elevation = _int(row["elevation"])
        box = PlannedBox(
            old_id=int(row["id"]),
            old_area_id=area_id,
            name=name,
            previous_names=previous,
            note=name_note,
            location=(float(row["gps_lat"]), float(row["gps_lng"])),
            elevation=elevation or None,
            old_user_id=_int(row["id_user"]),
            created_at=datetime.fromisoformat(row["created"]),
            old_type=self.types.get(row["id_nestbox_type"]),
        )
        if hole := (row["diameter"] or "").strip():
            box.hole = parse_hole(hole)
            if box.hole is None:
                box.note = "\n".join(
                    filter(None, [box.note, f"otvor ve staré databázi: {hole}"])
                )
                self.undecided["hole unreadable, kept in the note"].append(box.old_id)
        return box

    def _attributes(self, box, texts):
        """Box attributes the notes name; the latest mention wins."""
        previous = [box.previous_names] if box.previous_names else []
        for text in texts:
            box.opening = notes.opening(text) or box.opening
            box.material = notes.material(text) or box.material
            previous += notes.previous_names(text)
            # How to get to the box is what the volunteers' note is for
            if "access" in notes.labels(text) and text.strip() not in box.note:
                box.note = "\n".join(filter(None, [box.note, text.strip()]))
        box.previous_names = ", ".join(dict.fromkeys(previous))

    def _segments(self, row, area_id):
        """The old record as one box per physical box: a replacement starts a new one."""
        box = self._box(row, area_id)
        rows = list(self.checks[row["id"]])
        if rows and self._is_placeholder(rows[0], row):
            box.installed_on = _date(rows.pop(0)["date"])
            self.report["placeholder checks turned into installation dates"] += 1
        segments = [box]
        replacement_years = set()
        box_note_year = (
            notes.year(row["note"]) if "replaced" in notes.labels(row["note"]) else None
        )
        previous = None
        for index, check in enumerate(rows):
            day = _date(check["date"])
            occupancy = self.occupancy.get(check["id_nestbox_occupied"], "")
            note = check["note"].strip()
            if (
                area_id in self.suspect_areas
                and day == SUSPECT_BATCH_DATE
                and not occupancy
                and not note
            ):
                self.report["blank checks of the 2025-11-16 batch dropped"] += 1
                continue
            labels = notes.labels(note)
            if (
                box_note_year
                and day.year == box_note_year
                and box_note_year not in replacement_years
            ):
                labels |= {"replaced"}
            reading = read_check(
                occupancy,
                note,
                check["needs_reparation"],
                unseen_default=area_id in self.suspect_areas
                and day == SUSPECT_BATCH_DATE
                and not occupancy,
            )
            planned = PlannedCheck(
                date=day,
                made_at=_datetime(check["created"], day),
                old_user_id=_int(check["id_user"]),
                note="" if "performed_by_unit" in labels else note,
                reading=reading,
                unit_name=notes.normalized(note)
                if "performed_by_unit" in labels
                else "",
            )
            current = segments[-1]
            first = not current.checks and current.installed_on is None
            if "replaced" in labels or ("hung" in labels and not first):
                year = notes.year(note) if "replaced" in labels else None
                if year and year > day.year:
                    labels = labels - {"replaced"} | {"replace_needed"}
                elif (year or day.year) in replacement_years:
                    labels = labels - {"replaced"}
                elif "hung" in labels and "replaced" not in labels:
                    if current.status == Status.MISSING or (
                        previous
                        and previous.reading.box_left == BoxLeft.NEEDS_REPLACING
                    ):
                        labels |= {"replaced"}
            if "replaced" in labels and (current.checks or current.installed_on):
                replacement_years.add(notes.year(note) or day.year)
                new = replace(
                    current,
                    old_id=None,
                    status=Status.IN_USE,
                    installed_on=day,
                    checks=[],
                )
                current.end(day, "worn_out")
                current.old_id, current.note = None, ""
                segments.append(new)
                self.report["replacements split into a new box"] += 1
                if reading.found == Found.FOUND and reading.contents:
                    current.checks.append(planned)
                elif reading.found != Found.FOUND:
                    new.checks.append(planned)
                    new.status = Status.MISSING
                elif labels - notes.INSTALLATION - {"taken_down"}:
                    new.note = "\n".join(filter(None, [new.note, f"{day}: {note}"]))
                previous = planned
                continue
            if first and labels & notes.INSTALLATION and not reading.is_inspection:
                current.installed_on = day
                self.report["installation notes turned into installation dates"] += 1
                if labels - notes.INSTALLATION:
                    current.note = "\n".join(
                        filter(None, [current.note, f"{day}: {note}"])
                    )
                continue
            current.checks.append(planned)
            previous = planned
            is_last = index == len(rows) - 1
            if labels & notes.ENDING and reading.found != Found.NOT_REACHED:
                if notes.asks_to_move(labels, note):
                    self.report["boxes kept, their note asks to move them"] += 1
                elif is_last:
                    current.end(day, notes.end_reason(labels, note))
                    continue
                else:
                    self.undecided[
                        "note says the box ended, checked later, kept"
                    ].append(int(row["id"]))
            if reading.found == Found.NOT_FOUND:
                current.status = Status.MISSING
            elif reading.found == Found.FOUND:
                current.status = (
                    Status.TAKEN_DOWN
                    if reading.box_left == BoxLeft.TAKEN_DOWN
                    else Status.IN_USE
                )

        last = segments[-1]
        last.old_id = int(row["id"])
        if self.is_pseudo(int(row["id_area"])) and last.status != Status.ENDED:
            if RETIRED_LOCATION in self.area_location[int(row["id_area"])]:
                end = last.checks[-1].date if last.checks else last.created_at.date()
                last.end(end, "worn_out")
                self.report["boxes ended by the retired-boxes location"] += 1
            else:
                last.status = Status.TAKEN_DOWN
                self.report["boxes taken down by the repair location"] += 1
        box_note = (row["note"] or "").strip()
        if notes.is_recorded(box_note) and (
            not box_note_year or box_note_year in replacement_years
        ):
            self.report["box notes left out, their values are in the fields"] += 1
        else:
            last.note = "\n".join(filter(None, [last.note, box_note]))
        texts = [box_note] + [c["note"] for c in rows]
        for segment in segments:
            self._attributes(segment, texts)
            left = segment.checks[-1].reading.box_left if segment.checks else ""
            # The same values: a hanging box's shape is part of its status
            if segment.status == Status.IN_USE and left in (
                BoxLeft.NEEDS_REPAIR,
                BoxLeft.NEEDS_REPLACING,
            ):
                segment.status = left
            by_season = defaultdict(list)
            for check in segment.checks:
                by_season[Check.season_of(check.date)].append(check)
            self.report["checks merged into another of the same season"] += sum(
                len(group) - 1 for group in by_season.values()
            )
            segment.checks = [merge(group) for group in by_season.values()]
        return segments

    def plan(self):
        rows = self.tables["nestboxes"]
        real = [row for row in rows if not self.is_pseudo(int(row["id_area"]))]
        boxes = []
        for row in rows:
            boxes += self._segments(row, self._real_area(row, real))

        entries = defaultdict(Counter)
        recent = defaultdict(Counter)
        area_of = {row["id"]: self._real_area(row, real) for row in rows}
        for row in rows:
            entries[area_of[row["id"]]][_int(row["id_user"])] += 1
            if row["created"] >= ENTRIES_SINCE:
                recent[area_of[row["id"]]][_int(row["id_user"])] += 1
        for row in self.tables["checks"]:
            area = area_of[row["id_nestbox"]]
            entries[area][_int(row["id_user"])] += 1
            if row["date"] >= ENTRIES_SINCE:
                recent[area][_int(row["id_user"])] += 1
        for counter in (*entries.values(), *recent.values()):
            counter.pop(None, None)
        active = {int(u["id"]) for u in self.tables["users"] if u["active"] == "1"}
        data_users = {user for counter in entries.values() for user in counter}

        used_areas = {box.old_area_id for box in boxes}
        self.report["empty or test areas dropped"] = sum(
            area_id not in used_areas and not self.is_pseudo(area_id)
            for area_id in self.areas
        )
        unit_names = {
            notes.normalized(c["note"])
            for c in self.tables["checks"]
            if "performed_by_unit" in notes.labels(c["note"])
        }
        return Plan(
            areas={
                area_id: self.areas[area_id]["name"] for area_id in sorted(used_areas)
            },
            boxes=boxes,
            unit_names=unit_names,
            entries={area: (recent[area], entries[area]) for area in used_areas},
            data_users=data_users & active,
            inactive_users=data_users - active,
            report=self.report,
            undecided=self.undecided,
        )


def plan(tables):
    return Planner(tables).plan()
