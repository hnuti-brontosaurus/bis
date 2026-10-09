import datetime

import pytest
from bis.models import User
from bis.tests.test_mcp_visibility import make_event, make_user
from categories.models import RoleCategory
from django.test import RequestFactory
from event.models import EventRecord

PII_FIELDS = {
    "firstName",
    "lastName",
    "nickname",
    "birthName",
    "vokativ",
    "phone",
    "email",
    "birthday",
    "street",
    "address",
    "zipCode",
    "city",
    "healthIssues",
    "behaviourIssues",
    "contactName",
    "contactPhone",
    "contactEmail",
    "organizers",
    "info",
    "ico",
    "bankAccountNumber",
}

# The `address` objects carry only the region; street/city/zipCode stay denied.
ALLOWED = {
    ("UserType", "address"),
    ("EventApplicationType", "address"),
    ("AdministrationUnitType", "address"),
    ("AdministrationSubUnitType", "address"),
    ("AdministrationUnitType", "bankAccountNumber"),
    ("OfferedHelpType", "info"),
    ("UserType", "healthIssues"),
    ("UserType", "behaviourIssues"),
    ("EventApplicationType", "healthIssues"),
}


@pytest.fixture
def schema(db):
    # project.urls pulls in api.urls, whose filters query the DB at import
    # time, so bis.mcp_schema must only be imported once the db fixture is
    # active.
    from bis.mcp_schema import schema

    return schema


@pytest.fixture
def run(schema):
    def _run(query, export=False):
        request = RequestFactory().get("/mcp")
        request.user = make_user("brontosaurus.bot@gmail.com")
        result = schema.execute_sync(
            query,
            context_value={"request": request, "_export": export, "_export_qs": {}},
        )
        return result

    return _run


def test_schema_exposes_no_pii(schema):
    leaks = [
        (type_.name, field_name)
        for type_ in schema._schema.type_map.values()
        for field_name in getattr(type_, "fields", {})
        if field_name in PII_FIELDS and (type_.name, field_name) not in ALLOWED
    ]
    assert leaks == []


def test_event_with_participants_resolves_without_pii(run):
    event = make_event("Akce")
    participant = make_user("participant@example.com")
    participant.birthday = datetime.date(2000, 5, 17)
    participant.save()
    record = EventRecord.objects.create(event=event)
    record.participants.add(participant)

    result = run(
        "{ events { name record { participantsCount participants { id birthYear } } } }"
    )

    assert result.errors is None
    assert result.data["events"] == [
        {
            "name": "Akce",
            "record": {
                "participantsCount": 1,
                "participants": [{"id": str(participant.id), "birthYear": 2000}],
            },
        }
    ]


def test_aggregate_groups_by_exposed_paths(run):
    make_event("One")

    result = run(
        '{ aggregate(dataset: EVENTS, groupBy: ["start__year", "category__slug"],'
        ' maxOf: ["duration"]) }'
    )

    assert result.errors is None
    assert result.data["aggregate"] == [
        {
            "start__year": 2026,
            "category__slug": "public__volunteering",
            "count": 1,
            "max": {"duration": 2},
        }
    ]


def test_aggregate_groups_users_by_birth_year(run):
    for email, month in [("a@example.com", 1), ("b@example.com", 6)]:
        User.objects.filter(id=make_user(email).id).update(
            birthday=datetime.date(1999, month, 1)
        )

    result = run(
        "{ aggregate(dataset: USERS, filters: {birthday__isnull: false},"
        ' groupBy: ["birth_year"]) }'
    )

    assert result.errors is None
    assert result.data["aggregate"] == [{"birth_year": 1999, "count": 2}]


@pytest.mark.parametrize(
    "path",
    [
        "email",
        "birthday",
        "birthday__year",
        "main_organizer__email",
        "record__participants__first_name",
        "birth_year__month",
    ],
)
def test_aggregate_rejects_hidden_paths(run, path):
    dataset = "USERS" if not path.startswith(("main", "record")) else "EVENTS"

    result = run(f'{{ aggregate(dataset: {dataset}, groupBy: ["{path}"]) }}')

    assert "Invalid path" in result.errors[0].message


def test_limit_is_capped(run):
    result = run("{ events(limit: 1001) { id } }")

    assert "at most 1000" in result.errors[0].message


def test_export_rejects_datasets_without_exporter(run):
    result = run("{ opportunities { id } }", export=True)

    assert "cannot be exported" in result.errors[0].message


@pytest.fixture
def tools(db):
    from bis.mcp import BISTools

    request = RequestFactory().get("/mcp")
    request.user = make_user("brontosaurus.bot@gmail.com")
    return BISTools(request=request)


def make_office_worker(email):
    user = make_user(email)
    user.roles.add(
        RoleCategory.objects.get_or_create(
            slug="office_worker", defaults={"name": "office_worker"}
        )[0]
    )
    return user


@pytest.fixture
def office_worker(db):
    return make_office_worker("office@example.com")


@pytest.fixture
def submitted(monkeypatch):
    from bis import mcp

    calls = []
    monkeypatch.setattr(
        mcp._export_executor, "submit", lambda fn, *args: calls.append(args)
    )
    return calls


def test_export_ignores_limit_and_uses_export_name(tools, submitted, office_worker):
    make_event("Akce")

    message = tools.query(
        "{ events(limit: 5000) { id } feedbacks { id } }",
        export=True,
        export_name="Akce 2026",
        export_to=office_worker.email,
    )

    assert message.startswith("Exporting Akce_2026_events, Akce_2026_feedbacks.")
    assert [(qs.count(), name) for qs, _, name in submitted] == [
        (1, "Akce_2026_events"),
        (0, "Akce_2026_feedbacks"),
    ]


def test_export_name_defaults_to_dataset(tools, submitted, office_worker):
    tools.query("{ events { id } }", export=True, export_to=office_worker.email)

    assert [name for _, _, name in submitted] == ["events"]


def test_too_long_export_name_is_rejected_before_exporting(
    tools, submitted, office_worker
):
    message = tools.query(
        "{ events { id } }",
        export=True,
        export_name="x" * 59,
        export_to=office_worker.email,
    )

    assert message.startswith("Error: export_name is too long")
    assert submitted == []


def test_bot_export_goes_to_export_to(tools, submitted, office_worker):
    message = tools.query(
        "{ events { id } }", export=True, export_to="Office@Example.com"
    )

    assert message.endswith("You will receive an email at office@example.com.")
    assert [email for _, email, _ in submitted] == ["office@example.com"]


@pytest.mark.parametrize(
    "export_to", [None, "brontosaurus.bot@gmail.com", "member@example.com", "x@y.cz"]
)
def test_bot_export_needs_a_recipient_who_sees_all(tools, submitted, export_to):
    make_user("member@example.com")

    message = tools.query("{ events { id } }", export=True, export_to=export_to)

    assert message.startswith("Error:")
    assert submitted == []


def test_bot_cannot_export_to_itself_even_with_a_role(tools, submitted):
    tools.request.user.roles.add(
        RoleCategory.objects.create(slug="office_worker", name="office_worker")
    )

    message = tools.query(
        "{ events { id } }", export=True, export_to="brontosaurus.bot@gmail.com"
    )

    assert message.startswith("Error:")
    assert submitted == []


def test_person_export_goes_to_own_email_and_rejects_export_to(
    db, submitted, office_worker
):
    from bis.mcp import BISTools

    request = RequestFactory().get("/mcp")
    request.user = office_worker
    tools = BISTools(request=request)

    tools.query("{ events { id } }", export=True)
    rejected = tools.query(
        "{ events { id } }", export=True, export_to="other@example.com"
    )

    assert [email for _, email, _ in submitted] == ["office@example.com"]
    assert rejected == "Error: export_to is only for the bot account."


def test_export_is_saved_and_emailed_under_its_name(
    db, settings, tmp_path, monkeypatch
):
    from bis import emails, mcp
    from event.models import Event

    settings.MEDIA_ROOT = tmp_path
    sent = []
    monkeypatch.setattr(emails, "text", lambda *args: sent.append(args))
    make_event("Akce")

    # __wrapped__ skips closes_db_connection, which would close the test's
    # transaction-wrapped connection.
    mcp._export_and_email.__wrapped__(Event.objects.all(), "me@example.com", "Akce")

    [saved] = (tmp_path / "saved_files").glob("*/Akce.xlsx")
    [(recipients, subject, body)] = sent
    assert recipients == ["me@example.com"]
    assert subject == "Export: Akce"
    assert f"/media/saved_files/{saved.parent.name}/Akce.xlsx" in body
    assert len(saved.parent.name) >= 16
