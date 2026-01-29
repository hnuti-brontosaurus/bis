"""
MCP (Model Context Protocol) tools for BIS.

This module exposes Django models and custom tools for AI agents
to interact with the BIS system via MCP.
"""

from mcp_server import MCPToolset, ModelQueryToolset

from bis.models import Location, User
from event.models import Event


class LocationQueryTool(ModelQueryToolset):
    """Query locations in the BIS system."""

    model = Location
    description = "Search and query locations (volunteering sites) in BIS"

    def get_queryset(self):
        return super().get_queryset().select_related("program", "region")


class EventQueryTool(ModelQueryToolset):
    """Query events in the BIS system."""

    model = Event
    description = "Search and query events (activities, camps, weekends) in BIS"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "location",
                "group",
                "category",
                "program",
                "intended_for",
                "main_organizer",
            )
            .prefetch_related("administration_units", "tags")
        )


class UserQueryTool(ModelQueryToolset):
    """Query users in the BIS system (respects permissions)."""

    model = User
    description = "Search and query users/members in BIS"

    def get_queryset(self):
        # Only return basic user info, respecting privacy
        qs = super().get_queryset()
        if self.request and self.request.user.is_authenticated:
            # Authenticated users can see more
            return qs.prefetch_related("roles", "memberships")
        # Anonymous users get limited data
        return qs.none()


class BISTools(MCPToolset):
    """Custom BIS tools for AI agents."""

    def get_upcoming_events(self, limit: int = 10) -> list[dict]:
        """Get upcoming public events.

        Args:
            limit: Maximum number of events to return (default 10, max 50)

        Returns:
            List of upcoming events with basic info
        """
        from django.utils import timezone

        limit = min(limit, 50)
        events = Event.objects.filter(
            start__gte=timezone.now().date(),
            is_canceled=False,
        ).order_by("start")[:limit]

        return [
            {
                "id": e.id,
                "name": e.name,
                "start": str(e.start),
                "end": str(e.end),
                "location": e.location.name if e.location else None,
                "category": str(e.category) if e.category else None,
            }
            for e in events
        ]

    def get_location_info(self, location_id: int) -> dict | None:
        """Get detailed information about a specific location.

        Args:
            location_id: The ID of the location

        Returns:
            Location details or None if not found
        """
        try:
            loc = Location.objects.get(id=location_id)
            return {
                "id": loc.id,
                "name": loc.name,
                "description": loc.description,
                "address": loc.address,
                "is_traditional": loc.is_traditional,
                "for_beginners": loc.for_beginners,
                "program": str(loc.program) if loc.program else None,
                "region": str(loc.region) if loc.region else None,
                "web": loc.web,
            }
        except Location.DoesNotExist:
            return None

    def search_events(
        self,
        query: str | None = None,
        location_name: str | None = None,
        year: int | None = None,
    ) -> list[dict]:
        """Search for events by various criteria.

        Args:
            query: Text to search in event names
            location_name: Filter by location name (partial match)
            year: Filter by year

        Returns:
            List of matching events (max 20)
        """
        from django.db.models import Q

        qs = Event.objects.all()

        if query:
            qs = qs.filter(name__icontains=query)

        if location_name:
            qs = qs.filter(location__name__icontains=location_name)

        if year:
            qs = qs.filter(start__year=year)

        events = qs.order_by("-start")[:20]

        return [
            {
                "id": e.id,
                "name": e.name,
                "start": str(e.start),
                "end": str(e.end),
                "location": e.location.name if e.location else None,
                "is_canceled": e.is_canceled,
            }
            for e in events
        ]
