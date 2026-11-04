import importlib

from categories.models import NestBoxEndReason
from django.apps import apps


def test_not_allowed_end_reason_is_added_back(db):
    migration = importlib.import_module(
        "nest_boxes.migrations.0004_not_allowed_end_reason"
    )
    migration.add_not_allowed(apps, None)
    migration.add_not_allowed(apps, None)

    reason = NestBoxEndReason.objects.get(slug="not_allowed")
    assert (reason.name, reason.spot_reusable) == ("nepovoleno", False)
