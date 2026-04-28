from django.db.models import (
    CharField,
    Count,
    Exists,
    F,
    IntegerField,
    OuterRef,
    Prefetch,
    Q,
    Subquery,
    Value,
)
from django.db.models.functions import Coalesce, Greatest
from donations.models import Donor, DonorEvent

CALL_OUTCOME_SLUGS = frozenset(
    {"call_no_answer", "call_declined", "call_postponed", "call_reached"}
)


def _membership_qs(campaign):
    return Donor.objects.filter(
        Exists(
            DonorEvent.objects.filter(
                donor=OuterRef("pk"),
                event_type__slug="added_to_campaign",
                campaign=campaign,
            )
        )
    )


def _added_at_subq(campaign, outer_ref="pk"):
    return Subquery(
        DonorEvent.objects.filter(
            donor=OuterRef(outer_ref),
            campaign=campaign,
            event_type__slug="added_to_campaign",
        )
        .order_by("created_at")
        .values("created_at")[:1]
    )


def _latest_reminder_event_subq(campaign, outer_ref="pk"):
    return Subquery(
        DonorEvent.objects.filter(
            donor=OuterRef(outer_ref),
            campaign=campaign,
            reminder__isnull=False,
        )
        .order_by("-created_at")
        .values("created_at")[:1]
    )


def _window_start(campaign, outer_ref="pk"):
    """Greatest(added_at, Coalesce(latest_reminder_event_at, added_at))."""
    return Greatest(
        _added_at_subq(campaign, outer_ref),
        Coalesce(
            _latest_reminder_event_subq(campaign, outer_ref),
            _added_at_subq(campaign, outer_ref),
        ),
    )


def _annotate_worklist(qs, campaign):
    latest_reminder_due_subq = Subquery(
        DonorEvent.objects.filter(
            donor=OuterRef("pk"),
            campaign=campaign,
            reminder__isnull=False,
        )
        .order_by("-created_at")
        .values("reminder")[:1]
    )

    calls_in_window_subq = Subquery(
        DonorEvent.objects.filter(
            donor=OuterRef("pk"),
            campaign=campaign,
            event_type__slug__in=list(CALL_OUTCOME_SLUGS),
            created_at__gt=_window_start(campaign, outer_ref=OuterRef("pk")),
        )
        .values("donor")
        .annotate(c=Count("id"))
        .values("c"),
        output_field=IntegerField(),
    )

    _latest_call_qs = DonorEvent.objects.filter(
        donor=OuterRef("pk"),
        campaign=campaign,
        event_type__slug__in=list(CALL_OUTCOME_SLUGS),
    ).order_by("-created_at")

    latest_call_subq = Subquery(_latest_call_qs.values("created_at")[:1])
    latest_call_slug_subq = Subquery(
        _latest_call_qs.values("event_type__slug")[:1],
        output_field=CharField(),
    )

    last_nonempty_note_subq = Subquery(
        DonorEvent.objects.filter(
            donor=OuterRef("pk"),
            campaign=campaign,
        )
        .exclude(fundraisers_note="")
        .order_by("-created_at")
        .values("fundraisers_note")[:1],
        output_field=CharField(),
    )

    return qs.annotate(
        latest_reminder_due_at=latest_reminder_due_subq,
        calls_in_window=Coalesce(
            calls_in_window_subq, Value(0), output_field=IntegerField()
        ),
        latest_call_at=latest_call_subq,
        latest_call_slug=latest_call_slug_subq,
        last_nonempty_note=last_nonempty_note_subq,
    )


def _with_recent_events(qs, campaign):
    recent = Prefetch(
        "events",
        queryset=DonorEvent.objects.filter(campaign=campaign)
        .select_related("event_type")
        .order_by("-created_at"),
        to_attr="recent_campaign_events",
    )
    return qs.select_related("user", "user__pronoun").prefetch_related(recent)


def get_reminders_due(campaign):
    qs = _membership_qs(campaign)
    qs = _annotate_worklist(qs, campaign)
    return (
        _with_recent_events(qs, campaign)
        .filter(latest_reminder_due_at__isnull=False, calls_in_window=0)
        .order_by("latest_reminder_due_at")
    )


def get_worklist(campaign):
    qs = _membership_qs(campaign)
    qs = _annotate_worklist(qs, campaign)
    qs = qs.filter(calls_in_window__lt=4)
    qs = qs.exclude(latest_call_slug__isnull=False, latest_call_slug="call_reached")
    # Exclude donors shown in the reminders section (any reminder + no call since).
    # Use isnull=False to avoid NOT(NULL AND ...) = NULL incorrectly dropping rows.
    qs = qs.exclude(
        latest_reminder_due_at__isnull=False,
        calls_in_window=0,
    )
    return _with_recent_events(qs, campaign).order_by(
        F("latest_call_at").asc(nulls_first=True)
    )


def get_finished(campaign):
    qs = _membership_qs(campaign)
    qs = _annotate_worklist(qs, campaign)
    return (
        _with_recent_events(qs, campaign)
        .filter(Q(calls_in_window__gte=4) | Q(latest_call_slug="call_reached"))
        .order_by(F("latest_call_at").desc(nulls_last=True))
    )


def get_donor_campaign_context(donor, campaign):
    added_event = (
        DonorEvent.objects.filter(
            donor=donor,
            campaign=campaign,
            event_type__slug="added_to_campaign",
        )
        .order_by("created_at")
        .first()
    )
    added_at = added_event.created_at if added_event else None

    latest_reminder_event = (
        DonorEvent.objects.filter(
            donor=donor,
            campaign=campaign,
            reminder__isnull=False,
        )
        .order_by("-created_at")
        .first()
    )
    latest_reminder_event_at = (
        latest_reminder_event.created_at if latest_reminder_event else None
    )

    if latest_reminder_event_at and added_at:
        window_started_at = max(added_at, latest_reminder_event_at)
    else:
        window_started_at = added_at

    calls_in_window = 0
    if window_started_at:
        calls_in_window = DonorEvent.objects.filter(
            donor=donor,
            campaign=campaign,
            event_type__slug__in=CALL_OUTCOME_SLUGS,
            created_at__gt=window_started_at,
        ).count()

    history = list(
        DonorEvent.objects.filter(donor=donor, campaign=campaign)
        .select_related("event_type", "created_by")
        .order_by("-created_at")
    )

    return {
        "calls_in_window": calls_in_window,
        "window_started_at": window_started_at,
        "history": history,
    }
