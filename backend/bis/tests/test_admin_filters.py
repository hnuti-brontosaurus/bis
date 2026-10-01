from datetime import date

import pytest
from bis.admin_filters import ActiveQualificationFilter, HasFeedbackFilter
from bis.helpers import paused_validation
from bis.models import Qualification, User
from categories.models import QualificationCategory
from django.contrib import admin
from django.test import RequestFactory
from event.models import Event


@pytest.fixture
def qualified(db):
    user = User.objects.create(first_name="Qualified")
    # Qualification.clean() wants an approver qualified to approve it
    with paused_validation():
        for slug in ("first", "second"):
            Qualification.objects.create(
                user=user,
                category=QualificationCategory.objects.create(name=slug, slug=slug),
                valid_since=date.today(),
                valid_till=date.today(),
                approved_by=user,
            )
    return user


def filtered(
    value, filter_class=ActiveQualificationFilter, model=User, lookup="qualifications"
):
    params = {filter_class.parameter_name: [value]} if value else {}
    list_filter = filter_class(
        RequestFactory().get("/"), params, model, admin.site._registry[model]
    )
    queryset = model.objects.prefetch_related(lookup)
    return list_filter.queryset(None, queryset)


def test_yes_lists_a_user_with_two_matches_once(qualified):
    unqualified = User.objects.create(first_name="Unqualified")

    assert list(filtered("yes")) == [qualified]
    assert list(filtered("no")) == [unqualified]


@pytest.mark.parametrize("value", [None, "yes", "no"])
@pytest.mark.parametrize(
    "filter_class, model, lookup",
    [
        (ActiveQualificationFilter, User, "qualifications"),
        (HasFeedbackFilter, Event, "tags"),
    ],
)
def test_keeps_the_prefetch_of_the_model_admin(filter_class, model, lookup, value):
    queryset = filtered(value, filter_class, model, lookup)
    assert queryset._prefetch_related_lookups == (lookup,)
