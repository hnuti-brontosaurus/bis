import datetime

import pytest
from bis.models import User
from categories.models import DonationSourceCategory
from django.contrib.admin.sites import site
from django.test import RequestFactory
from donations.models import Donation, Donor
from xlsx_export.serializers import DonorExportSerializer


@pytest.fixture
def donor(db):
    user = User.objects.create(email="donor@example.com", _str="Donor")
    donor = Donor.objects.create(user=user)
    source = DonationSourceCategory.objects.create(name="Darujme", slug="darujme")
    for year, amount in [(2025, 100), (2026, 500)]:
        Donation.objects.create(
            donor=donor,
            donated_at=datetime.date(year, 3, 1),
            amount=amount,
            donation_source=source,
        )
    return donor


def export_row(queryset):
    queryset = DonorExportSerializer.get_related(queryset)
    return DonorExportSerializer(queryset.get()).data


def test_export_computes_donation_stats_itself(donor):
    row = export_row(Donor.objects.all())

    assert row["donations_sum"] == 600
    assert row["first_donation"] == "2025-03-01"
    assert row["last_donation"] == "2026-03-01"
    assert row["donation_sources"] == ["Darujme"]


def test_admin_export_keeps_sum_scoped_to_changelist_filter(donor):
    request = RequestFactory().get(
        "/admin/donations/donor/",
        {"donated_at__range__gte": "2026-01-01"},
    )
    request.user = User.objects.create(email="admin@example.com", _str="Admin")
    request.user.is_superuser = True
    model_admin = site._registry[Donor]
    changelist = model_admin.get_changelist_instance(request)

    row = export_row(changelist.get_queryset(request))

    assert row["donations_sum"] == 500
