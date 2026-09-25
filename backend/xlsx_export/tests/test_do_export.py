import datetime

import pytest
from administration_units.models import AdministrationUnit
from bis.helpers import paused_validation
from bis.models import Location, Membership, User
from categories.models import (
    AdministrationUnitCategory,
    DonationSourceCategory,
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    MembershipCategory,
)
from django.db import transaction
from django.db.models import Min, Q, Sum
from donations.models import Donation, Donor
from event.models import Event, EventRegistration
from feedback.models import EventFeedback
from questionnaire.models import EventApplication
from xlsx_export.export import EXPORT_SERIALIZERS, do_export_to_xlsx
from xlsx_export.serializers import DonorExportSerializer

XLSX_MAGIC_BYTES = b"PK\x03\x04"


def make_user(email):
    return User.objects.create(
        email=email,
        first_name="Test",
        last_name="User",
        _str="Test User",
    )


@transaction.atomic
def seed_all_exportable_models():
    """Create one instance of every model in EXPORT_SERIALIZERS, with the
    related objects each export serializer touches."""
    with paused_validation():
        user = make_user("export@example.com")

        location = Location.objects.create(name="Test")

        event = Event.objects.create(
            name="Test event",
            start=datetime.date(2026, 1, 10),
            end=datetime.date(2026, 1, 11),
            duration=2,
            location=location,
            group=EventGroupCategory.objects.create(name="Akce", slug="weekend_event"),
            category=EventCategory.objects.create(
                name="Veřejné", slug="public__volunteering"
            ),
            program=EventProgramCategory.objects.create(name="Příroda", slug="nature"),
            intended_for=EventIntendedForCategory.objects.create(
                name="Pro všechny", slug="for_all"
            ),
        )

        administration_unit = AdministrationUnit.objects.create(
            name="Test unit",
            abbreviation="TU",
            category=AdministrationUnitCategory.objects.create(
                name="Klub", slug="club"
            ),
            is_for_kids=True,
            phone="+420123456789",
            email="unit@example.com",
            chairman=user,
            existed_since=datetime.date(2020, 1, 1),
        )

        Membership.objects.create(
            user=user,
            category=MembershipCategory.objects.create(name="Dospělý", slug="adult"),
            administration_unit=administration_unit,
            year=2026,
            _year=datetime.date(2026, 1, 1),
        )

        donor = Donor.objects.create(user=user)
        donation = Donation.objects.create(
            donor=donor,
            donation_source=DonationSourceCategory.objects.create(
                name="Darujme", slug="darujme"
            ),
            donated_at=datetime.date(2026, 1, 5),
            amount=200,
            info="Test donation",
        )

        EventRegistration.objects.create(event=event)
        EventApplication.objects.create(
            event_registration=event.registration,
            state="approved",
            first_name="Test",
            last_name="Uchazeč",
        )
        EventFeedback.objects.create(event=event)

        return donor, donation


@pytest.fixture
def seeded(db):
    return seed_all_exportable_models()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "model",
    sorted(EXPORT_SERIALIZERS, key=lambda model: model.__name__),
    ids=lambda model: model.__name__,
)
def test_export_works_on_a_plain_queryset(model, seeded):
    # The MCP export path passes a plain queryset, without the annotations
    # the admin changelist adds (Donor used to crash on a missing
    # donations_sum annotation).
    file = do_export_to_xlsx(model.objects.all())

    with open(file.name, "rb") as f:
        assert f.read(len(XLSX_MAGIC_BYTES)) == XLSX_MAGIC_BYTES


@pytest.mark.django_db
def test_donor_export_annotates_lifetime_donation_stats(seeded):
    donor, donation = seeded

    instance = DonorExportSerializer.get_related(Donor.objects.all()).get(pk=donor.pk)

    assert instance.donations_sum == donation.amount
    assert instance.first_donation == donation.donated_at
    assert instance.last_donation == donation.donated_at
    assert list(instance.donation_sources) == [str(donation.donation_source)]


@pytest.mark.django_db
def test_donor_export_keeps_admin_annotations(seeded):
    donor, donation = seeded
    other_source = DonationSourceCategory.objects.create(name="Převod", slug="transfer")
    Donation.objects.create(
        donor=donor,
        donation_source=other_source,
        donated_at=datetime.date(2025, 12, 1),
        amount=1000,
        info="Counted only by the admin changelist filter",
    )

    admin_queryset = Donor.objects.annotate(
        donations_sum=Sum(
            "donations__amount",
            filter=Q(donations__donation_source=other_source),
        ),
        first_donation=Min(
            "donations__donated_at",
            filter=Q(donations__donation_source=other_source),
        ),
    )

    instance = DonorExportSerializer.get_related(admin_queryset).get(pk=donor.pk)

    # Request-dependent admin annotations must win over the lifetime ones.
    assert instance.donations_sum == 1000
    assert instance.first_donation == datetime.date(2025, 12, 1)
    # Not pre-annotated by the admin, so the lifetime value fills in.
    assert instance.last_donation == donation.donated_at
    assert sorted(instance.donation_sources) == ["Darujme", "Převod"]
