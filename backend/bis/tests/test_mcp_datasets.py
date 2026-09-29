import datetime

import pytest
from administration_units.models import AdministrationUnit
from bis.models import Location, Membership
from bis.tests.test_mcp_visibility import make_event, make_user
from categories.models import (
    AdministrationUnitCategory,
    DonationSourceCategory,
    MembershipCategory,
    OpportunityCategory,
    OpportunityPriority,
)
from django.test import RequestFactory
from donations.models import Donation, Donor
from event.models import EventRecord, EventRegistration
from feedback.models import EventFeedback
from graphql import get_named_type, is_leaf_type, is_non_null_type
from opportunities.models import Opportunity
from questionnaire.models import EventApplication
from strawberry.utils.str_converters import to_camel_case
from xlsx_export.export import do_export_to_xlsx


@pytest.fixture
def schema(db):
    # project.urls pulls in api.urls, whose filters query the DB at import
    # time, so bis.mcp_schema must only be imported once the db fixture is
    # active.
    from bis.mcp_schema import schema

    return schema


@pytest.fixture
def one_of_each(db):
    user = make_user("someone@example.com")
    user.birthday = datetime.date(2000, 5, 17)
    user.save()

    event = make_event("Akce")
    EventRecord.objects.create(event=event).participants.add(user)
    registration = EventRegistration.objects.create(event=event)
    EventApplication.objects.create(
        event_registration=registration,
        user=user,
        state="pending",
        first_name="Test",
        last_name="User",
    )
    EventFeedback.objects.create(event=event, user=user)

    unit = AdministrationUnit.objects.create(
        name="Článek",
        abbreviation="CL",
        is_for_kids=False,
        email="clanek@example.com",
        category=AdministrationUnitCategory.objects.create(
            name="Základní článek", slug="basic_section"
        ),
        chairman=user,
        manager=user,
    )
    Membership.objects.create(
        user=user,
        category=MembershipCategory.objects.create(name="Člen", slug="adult"),
        administration_unit=unit,
    )

    donor = Donor.objects.create(user=user, basic_section_support=unit)
    Donation.objects.create(
        donor=donor,
        donated_at=datetime.date(2026, 3, 1),
        amount=500,
        donation_source=DonationSourceCategory.objects.create(
            name="Darujme", slug="darujme"
        ),
    )

    Opportunity.objects.create(
        category=OpportunityCategory.objects.create(
            name="Spolupráce", slug="collaboration"
        ),
        priority=OpportunityPriority.objects.create(name="Normální", slug="normal"),
        name="Příležitost",
        start=datetime.date(2026, 1, 1),
        end=datetime.date(2026, 2, 1),
        on_web_start=datetime.date(2026, 1, 1),
        on_web_end=datetime.date(2026, 2, 1),
        location=Location.objects.create(name="Někde"),
        contact_person=user,
    )


@pytest.fixture
def run(schema):
    bot = make_user("brontosaurus.bot@gmail.com")

    def _run(query, export=False):
        request = RequestFactory().get("/mcp")
        request.user = bot
        context = {"request": request, "_export": export, "_export_qs": {}}
        result = schema.execute_sync(query, context_value=context)
        assert result.errors is None, result.errors
        return result.data, context["_export_qs"]

    return _run


def every_field(type_, depth):
    selections = []
    for name, field in type_.fields.items():
        if any(is_non_null_type(arg.type) for arg in field.args.values()):
            continue
        field_type = get_named_type(field.type)
        if is_leaf_type(field_type):
            selections.append(name)
        elif depth and (nested := every_field(field_type, depth - 1)):
            selections.append(f"{name} {{ {nested} }}")
    return " ".join(selections)


def datasets():
    from bis.mcp_schema import DATASETS

    return list(DATASETS)


@pytest.mark.parametrize("dataset", datasets())
def test_dataset_resolves_every_field(schema, run, one_of_each, dataset):
    root = to_camel_case(dataset)
    row_type = get_named_type(schema._schema.query_type.fields[root].type)

    data, _ = run(f"{{ {root} {{ {every_field(row_type, depth=2)} }} }}")

    assert data[root]


@pytest.mark.parametrize("dataset", datasets())
def test_dataset_aggregates(run, one_of_each, dataset):
    data, _ = run(f"{{ aggregate(dataset: {dataset.upper()}) }}")

    assert data["aggregate"][0]["count"] >= 1


@pytest.mark.parametrize("dataset", datasets())
def test_dataset_exports(run, one_of_each, dataset):
    from bis.mcp_schema import DATASETS
    from xlsx_export.export import EXPORT_SERIALIZERS

    if DATASETS[dataset] not in EXPORT_SERIALIZERS:
        pytest.skip(f"{dataset} has no exporter")

    _, exported = run(f"{{ {to_camel_case(dataset)} {{ id }} }}", export=True)

    do_export_to_xlsx(exported[dataset])
