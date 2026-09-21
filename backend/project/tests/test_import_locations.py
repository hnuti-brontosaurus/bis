import pytest
from categories.models import LocationAccessibilityCategory, LocationProgramCategory


def get_command():
    from bis.management.commands.import_locations import Command

    return Command()


@pytest.fixture
def command(db):
    LocationProgramCategory.objects.create(name="Příroda", slug="nature")
    LocationProgramCategory.objects.create(name="Památky", slug="monuments")
    LocationAccessibilityCategory.objects.create(name="Snadná", slug="good")
    LocationAccessibilityCategory.objects.create(name="Střední", slug="ok")
    LocationAccessibilityCategory.objects.create(name="Obtížná", slug="bad")
    return get_command()


def make_attribute(attribute_id, value):
    return {"attribute": {"id": attribute_id}, "value": value}


@pytest.mark.django_db
def test_parse_attribute_list_value(command):
    parsed = command.parse_attribute(make_attribute(8118, ["jckv"]))
    assert parsed["accessibility_from_brno"].slug == "bad"


@pytest.mark.django_db
def test_parse_attribute_bare_string_value(command):
    # Mapotic normally returns select values as a list, but POIs edited in
    # a certain way come back with a bare string; indexing it used to cut
    # the string to its first character and crash on the choices map.
    parsed = command.parse_attribute(make_attribute(8118, "jckv"))
    assert parsed["accessibility_from_brno"].slug == "bad"


@pytest.mark.django_db
def test_parse_attribute_empty_value(command):
    assert command.parse_attribute(make_attribute(8118, [])) == {}
    assert command.parse_attribute(make_attribute(8119, None)) == {}


@pytest.mark.django_db
def test_parse_attribute_is_full_string_value(command):
    parsed = command.parse_attribute(make_attribute(2259, "nrrx"))
    assert parsed["is_full"] is True
    parsed = command.parse_attribute(make_attribute(2259, ["kgeh"]))
    assert parsed["is_full"] is False
