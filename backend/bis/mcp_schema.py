"""GraphQL schema for BIS MCP tools."""

from __future__ import annotations

import strawberry
import strawberry_django
from django.core.exceptions import FieldError
from strawberry.scalars import JSON
from strawberry_django.optimizer import DjangoOptimizerExtension

from administration_units.models import AdministrationUnit
from bis.models import Location
from bis.permissions import Permissions
from categories.models import (
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    EventTag,
)
from event.models import Event, EventRecord
from feedback.models import EventFeedback, FeedbackForm, Inquiry, Reply
from regions.models import Region

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

# Exclude PII from Event and EventFeedback; geo fields from Region/Location.
# Everything else: all fields.


@strawberry_django.type(Region, exclude=["area"])
class RegionType:
    pass


@strawberry_django.type(EventCategory, fields="__all__")
class EventCategoryType:
    pass


@strawberry_django.type(EventGroupCategory, fields="__all__")
class EventGroupType:
    pass


@strawberry_django.type(EventProgramCategory, fields="__all__")
class EventProgramType:
    pass


@strawberry_django.type(EventIntendedForCategory, fields="__all__")
class EventIntendedForType:
    pass


@strawberry_django.type(EventTag, fields="__all__")
class EventTagType:
    pass


@strawberry_django.type(
    AdministrationUnit,
    exclude=[
        "chairman",
        "vice_chairman",
        "manager",
        "board_members",
        "gps_location",
        "image",
        "custom_statues",
        "phone",
        "_import_id",
        "_history",
        "_search_field",
    ],
)
class AdministrationUnitType:
    pass


@strawberry_django.type(
    Location,
    exclude=["gps_location", "_import_id", "_search_field"],
)
class LocationType:
    pass


@strawberry_django.type(FeedbackForm, fields="__all__")
class FeedbackFormType:
    inquiries: list[InquiryType]


@strawberry_django.type(Inquiry, fields="__all__")
class InquiryType:
    replies: list[ReplyType]


@strawberry_django.type(Reply, fields="__all__")
class ReplyType:
    pass


@strawberry_django.type(
    EventFeedback,
    exclude=["user", "name", "email"],
)
class EventFeedbackType:
    replies: list[ReplyType]


@strawberry_django.type(EventRecord, fields="__all__")
class EventRecordType:
    @strawberry.field
    def participants_count(self) -> int | None:
        try:
            return self.get_participants_count()
        except Exception:
            return None


@strawberry_django.type(
    Event,
    exclude=[
        "main_organizer",
        "other_organizers",
        "created_by",
        "internal_note",
        "_import_id",
        "_search_field",
    ],
)
class EventType:
    feedback_form: FeedbackFormType | None
    feedbacks: list[EventFeedbackType]
    record: EventRecordType | None
    tags: list[EventTagType]
    administration_units: list[AdministrationUnitType]
    location: LocationType | None
    category: EventCategoryType
    group: EventGroupType
    program: EventProgramType
    intended_for: EventIntendedForType


# ---------------------------------------------------------------------------
# Query
# ---------------------------------------------------------------------------


def _permitted_events(info):
    qs = Event.objects.all()
    return Permissions(info.context["request"].user, Event, "backend").filter_queryset(
        qs
    )


def _apply_filters(qs, filters):
    if not filters:
        return qs
    try:
        return qs.filter(**filters)
    except (FieldError, TypeError, ValueError) as e:
        raise ValueError(f"Invalid filter: {e}")


@strawberry.type
class Query:
    @strawberry.field
    def events(
        self,
        info: strawberry.types.Info,
        filters: JSON | None = None,
        ordering: str = "-start",
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventType]:
        """Query events with optional Django ORM filters.

        filters is a JSON dict of Django ORM lookups,
        e.g. {start__year: 2024, category__slug: "public__volunteering"}.
        """
        qs = _apply_filters(_permitted_events(info), filters)
        qs = qs.order_by(ordering)
        info.context.setdefault("_export_qs", {})["events"] = qs
        if info.context.get("_export"):
            return []
        return qs[offset : offset + limit]

    @strawberry.field
    def event(
        self,
        info: strawberry.types.Info,
        id: int,
    ) -> EventType | None:
        """Get a single event by ID."""
        return _permitted_events(info).filter(id=id).first()

    @strawberry.field
    def feedbacks(
        self,
        info: strawberry.types.Info,
        event_filters: JSON | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[EventFeedbackType]:
        """Query feedbacks. Use event_filters to filter by event attributes."""
        event_qs = _apply_filters(_permitted_events(info), event_filters)
        qs = EventFeedback.objects.filter(event__in=event_qs)
        info.context.setdefault("_export_qs", {})["feedbacks"] = qs
        if info.context.get("_export"):
            return []
        return qs[offset : offset + limit]


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

schema = strawberry.Schema(
    query=Query,
    extensions=[DjangoOptimizerExtension],
)
