import pytest
from api.web.serializers import (
    AdministrationUnitSerializer,
    EventSerializer,
    OpportunitySerializer,
)
from bis.data_sensitivity import (
    NOTES,
    SENSITIVITY,
    Level,
    documented_models,
    level_of,
    model_fields,
)
from rest_framework.serializers import (
    ListSerializer,
    ModelSerializer,
    SerializerMethodField,
)


def documented_fields():
    return {
        (model._meta.label, field.name): model
        for model in documented_models()
        for field in model_fields(model)
    }


def test_every_field_has_exactly_one_level():
    classified = [
        (label, name)
        for label, levels in SENSITIVITY.items()
        for names in levels.values()
        for name in names
    ]
    assert len(classified) == len(set(classified))
    assert set(classified) == set(documented_fields())


def test_notes_belong_to_documented_fields():
    fields = {f"{label}.{name}" for label, name in documented_fields()}
    assert set(NOTES) - fields == set()


@pytest.mark.django_db
def test_matches_mcp_schema():
    # bis.mcp_schema pulls in api.urls, whose filters query the DB on import
    from bis.mcp_schema import EXPOSED_FIELDS

    allowed = {
        True: {Level.PERSONAL},
        False: {Level.PUBLIC, Level.INTERNAL},
    }
    mismatches = [
        (model._meta.label, name, level_of(model, name))
        for model, fields in EXPOSED_FIELDS.items()
        for name, is_personal in fields.items()
        if (model._meta.label, name) in documented_fields()
        and level_of(model, name) not in allowed[is_personal]
    ]
    assert mismatches == []


def public_fields(serializer):
    if isinstance(serializer, ListSerializer):
        serializer = serializer.child
    model = serializer.Meta.model
    for field in serializer.fields.values():
        if isinstance(field, SerializerMethodField):
            continue
        if field.source in {f.name for f in model_fields(model)}:
            yield model, field.source
        if isinstance(field, (ModelSerializer, ListSerializer)):
            yield from public_fields(field)


def test_public_api_shows_only_public_or_personal_fields():
    mismatches = [
        (model._meta.label, name, level_of(model, name))
        for serializer in (
            EventSerializer(),
            OpportunitySerializer(),
            AdministrationUnitSerializer(),
        )
        for model, name in public_fields(serializer)
        if level_of(model, name) not in {Level.PUBLIC, Level.PERSONAL}
    ]
    assert mismatches == []


@pytest.mark.django_db
def test_docs_page_is_public(client):
    response = client.get("/docs/")
    assert response.status_code == 200
    assert "bis.User" in response.content.decode()
