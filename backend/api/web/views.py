from administration_units.models import AdministrationUnit
from api.web.filters import AdministrationUnitFilter, EventFilter, OpportunityFilter
from api.web.serializers import (
    AdministrationUnitSerializer,
    EventSerializer,
    OpportunitySerializer,
)
from django.http import Http404
from django.utils.timezone import now
from event.models import Event
from opportunities.models import Opportunity
from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ReadOnlyModelViewSet


class EventViewSet(ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    filterset_class = EventFilter

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
            % (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        try:
            obj = get_object_or_404(queryset, **filter_kwargs)
        except Http404:
            obj = get_object_or_404(
                queryset, **{"_import_id": self.kwargs[lookup_url_kwarg]}
            )

        self.check_object_permissions(self.request, obj)
        return obj

    def get_queryset(self):
        queryset = (
            Event.objects.order_by("id")
            .select_related(
                "location",
                "category",
                "program",
                "propagation",
                "intended_for",
                "registration",
            )
            .prefetch_related(
                "propagation__images",
                "administration_units",
                "propagation__diets",
                "tags",
            )
        )

        if self.action == "list":
            queryset = queryset.filter(
                is_canceled=False, propagation__is_shown_on_web=True
            ).exclude(propagation__isnull=True)

        return queryset


class OpportunityViewSet(ReadOnlyModelViewSet):
    queryset = Opportunity.objects.order_by("priority", "start", "id").select_related(
        "category",
        "location",
        "contact_person",
    )
    serializer_class = OpportunitySerializer
    filterset_class = OpportunityFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                on_web_start__lte=now(),
                on_web_end__gte=now(),
            )
        )


class AdministrationUnitViewSet(ReadOnlyModelViewSet):
    queryset = (
        AdministrationUnit.objects.filter(
            existed_till__isnull=True,
        )
        .select_related(
            "category",
            "chairman",
            "vice_chairman",
            "manager",
        )
        .prefetch_related(
            "board_members",
            "sub_units",
            "sub_units__main_leader",
            "sub_units__sub_leaders",
            "sub_units__address",
        )
    )
    serializer_class = AdministrationUnitSerializer
    filterset_class = AdministrationUnitFilter
