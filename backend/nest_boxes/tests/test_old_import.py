from datetime import date
from io import StringIO

import pytest
from administration_units.models import AdministrationUnit
from bis.helpers import paused_validation
from bis.models import User
from categories.models import AdministrationUnitCategory
from django.core.management import call_command
from nest_boxes.models import Area, Check, NestBox
from nest_boxes.old_import.dump import parse_dump
from nest_boxes.old_import.values import parse_hole, parse_name

DUMP = r"""-- Adminer 4.8.1 MySQL dump

INSERT INTO `locations` (`id`, `name`) VALUES
(1,	'Lokalita'),
(2,	'_hřbitov pro dosloužilé budky');

INSERT INTO `areas` (`id`, `id_location`, `name`) VALUES
(1,	1,	'Les'),
(2,	1,	'test'),
(3,	2,	'_dosloužilé');

INSERT INTO `nestbox_occupied` (`id`, `name`) VALUES
(1,	'ano'),
(5,	'nenalezena'),
(6,	'stažena');

INSERT INTO `nestbox_types` (`id`, `name`) VALUES
(2,	'koňadra'),
(8,	'modřinka');

INSERT INTO `users` (`id`, `email`, `password`, `name`, `role`, `active`) VALUES
(1,	'Budkar@Example.com',	'x',	'Budkař',	2,	1),
(2,	'nikdo@example.com',	'x',	'Nikdo',	2,	1);

INSERT INTO `nestboxes` (`id`, `number`, `id_area`, `gps_lat`, `gps_lng`, `diameter`, `created`, `note`, `elevation`, `id_user`, `id_nestbox_type`) VALUES
(1,	'1',	1,	50.08000000,	14.42000000,	'3,4',	'2016-01-07 10:00:00',	'horní',	0,	1,	2),
(2,	'N2',	1,	50.08100000,	14.42000000,	'',	'2016-01-07 10:00:00',	'u \'cesty\'\nvysoko',	300,	2,	8),
(3,	'3',	3,	50.08000500,	14.42000000,	NULL,	'2016-01-07 10:00:00',	NULL,	NULL,	1,	NULL);

INSERT INTO `checks` (`id`, `id_nestbox`, `date`, `id_nestbox_occupied`, `note`, `id_user`, `created`, `needs_reparation`) VALUES
(1,	1,	'2015-04-18',	NULL,	'',	1,	'2016-01-07 10:00:00',	NULL),
(2,	1,	'2016-02-27',	1,	'',	1,	'2016-03-01 10:00:00',	0),
(3,	1,	'2016-11-10',	NULL,	'opravit otvor',	1,	'2016-11-12 10:00:00',	0),
(4,	1,	'2017-03-04',	1,	'sýkora',	1,	'2017-03-05 10:00:00',	0),
(5,	1,	'2018-03-10',	1,	'vyměněna za novou 2018',	1,	NULL,	0),
(6,	1,	'2019-03-09',	NULL,	'nenalezena',	2,	'2019-03-10 10:00:00',	0),
(7,	2,	'2016-02-27',	NULL,	'',	2,	'2016-03-01 10:00:00',	0),
(8,	2,	'2017-03-04',	6,	'stažena na opravu',	2,	'2017-03-05 10:00:00',	1),
(9,	3,	'2016-02-27',	1,	'',	1,	'2016-03-01 10:00:00',	0);

INSERT INTO `wp_options` (`option_id`, `option_name`) VALUES
(1,	'ignored');
"""


@pytest.fixture
def headquarters(db):
    with paused_validation():
        return AdministrationUnit.objects.create(
            name="Ústředí",
            abbreviation="HB",
            is_for_kids=False,
            phone="+420123456789",
            email="hq@example.com",
            category=AdministrationUnitCategory.objects.create(
                name="Ústředí", slug="headquarter"
            ),
        )


@pytest.fixture
def run_import(tmp_path, movement, headquarters):
    path = tmp_path / "dump.sql"
    path.write_text(DUMP, encoding="utf-8")

    def run():
        output = StringIO()
        call_command("import_old_nest_boxes", path, stdout=output)
        return output.getvalue()

    return run


def test_parse_dump_reads_values_and_skips_other_tables():
    tables = parse_dump(DUMP, {"nestboxes", "checks"})

    assert set(tables) == {"nestboxes", "checks"}
    assert tables["nestboxes"][1]["note"] == "u 'cesty'\nvysoko"
    assert tables["nestboxes"][2]["diameter"] is None
    assert tables["checks"][0]["id_nestbox_occupied"] is None


@pytest.mark.parametrize(
    "raw, hole",
    [
        ("3,4", ("round", 34)),
        ("0,32", ("round", 32)),
        ("28 mm", ("round", 28)),
        ("14,00", ("round", 140)),
        ("3x4", ("oval", 30)),
        ("3/4", ("open_front", None)),
        ("ovál", ("oval", None)),
        ("3+", None),
    ],
)
def test_parse_hole(raw, hole):
    assert parse_hole(raw) == hole


def test_parse_name_moves_old_numbers_aside():
    assert parse_name("007 (do 2025 č. 037)") == ("007", "037 (do 2025)", "")
    assert parse_name("budka od Někoho") == ("bez označení", "", "budka od Někoho")


def test_import(run_import):
    budkar = User.objects.create(email="budkar@example.com")

    output = run_import()

    area = Area.objects.get()
    assert area.name == "Les"
    assert area.administration_unit.abbreviation == "HB"

    replaced, replacement = NestBox.objects.filter(name="1").order_by("installed_on")
    assert replaced.installed_on == date(2015, 4, 18)
    assert (replaced.status, replaced.ended_on, replaced.end_reason.slug) == (
        NestBox.Status.ENDED,
        date(2018, 3, 10),
        "worn_out",
    )
    assert replaced.old_id is None
    assert (replacement.old_id, replacement.status) == (1, NestBox.Status.MISSING)
    assert replacement.installed_on == date(2018, 3, 10)
    for box in NestBox.objects.filter(name="1").with_is_verified():
        assert (box.hole_shape, box.hole_size, box.type.slug) == (
            "round",
            34,
            "velky_sykornik",
        )
        assert box.opening == NestBox.Opening.ROOF
        assert box.elevation is None
        assert not box.is_verified

    first, merged, last = replaced.checks.order_by("date")
    assert first.contents == [Check.Content.BIRD_NEST]
    assert merged.date == date(2017, 3, 4)
    assert merged.contents == [Check.Content.BIRD_NEST]
    assert [o.slug for o in merged.occupants.all()] == ["sykora"]
    assert merged.note == "2016-11-10: opravit otvor\n2017-03-04: sýkora"
    assert last.date == date(2018, 3, 10)
    assert replacement.checks.get().found == Check.Found.NOT_FOUND
    assert all(
        check.is_confirmed and check.is_historical for check in Check.objects.all()
    )

    taken_down = NestBox.objects.get(name="N2")
    assert taken_down.status == NestBox.Status.TAKEN_DOWN
    assert taken_down.note == "u 'cesty'\nvysoko"
    assert taken_down.checks.count() == 2

    retired = NestBox.objects.get(old_id=3)
    assert retired.area == area
    assert (retired.status, retired.end_reason.slug) == (
        NestBox.Status.ENDED,
        "worn_out",
    )

    assert User.objects.get(pk=budkar.pk).is_nest_box_manager
    assert "no BIS account by email: 2\n" in output
    assert "@" not in output


def test_import_replaces_the_previous_import(run_import):
    run_import()
    run_import()

    assert NestBox.objects.count() == 4
    assert Check.objects.count() == 7
