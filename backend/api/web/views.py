from django.utils.timezone import now
from rest_framework.viewsets import ReadOnlyModelViewSet

from administration_units.models import AdministrationUnit
from api.web.filters import EventFilter, OpportunityFilter, AdministrationUnitFilter
from api.web.serializers import EventSerializer, OpportunitySerializer, AdministrationUnitSerializer
from event.models import Event
from opportunities.models import Opportunity


class EventViewSet(ReadOnlyModelViewSet):
    serializer_class = EventSerializer
    filterset_class = EventFilter

    def get_queryset(self):
        queryset = Event.objects.exclude(
            propagation__isnull=True
        ).order_by('start').select_related(
            'location',
            'category',
            'program',
            'propagation',
            'intended_for',
            'registration',
        ).prefetch_related(
            'propagation__images',
            'administration_units',
            'propagation__diets',
        )

        if self.action == 'list':
            queryset = queryset.filter(
                is_canceled=False,
                propagation__is_shown_on_web=True
            )

        return queryset


class OpportunityViewSet(ReadOnlyModelViewSet):
    queryset = Opportunity.objects.order_by('start').select_related(
        'category',
        'location',
        'contact_person',
    )
    serializer_class = OpportunitySerializer
    filterset_class = OpportunityFilter

    def get_queryset(self):
        return super().get_queryset().filter(
            on_web_start__lte=now(),
            on_web_end__gte=now(),
        )


class AdministrationUnitViewSet(ReadOnlyModelViewSet):
    queryset = AdministrationUnit.objects.filter(
        existed_till__isnull=True,
    ).select_related(
        'category',
        'chairman',
        'vice_chairman',
        'manager',
    ).prefetch_related(
        'board_members'
    )
    serializer_class = AdministrationUnitSerializer
    filterset_class = AdministrationUnitFilter
