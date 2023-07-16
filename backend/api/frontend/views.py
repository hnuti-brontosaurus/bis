from django.http import HttpResponseForbidden
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_200_OK, HTTP_429_TOO_MANY_REQUESTS, HTTP_403_FORBIDDEN
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from api.frontend.filters import EventFilter, LocationFilter, UserFilter
from api.frontend.permissions import BISPermissions
from api.frontend.serializers import UserSerializer, EventSerializer, LocationSerializer, OpportunitySerializer, \
    FinanceReceiptSerializer, EventPhotoSerializer, EventPropagationImageSerializer, QuestionSerializer, \
    EventApplicationSerializer, GetUnknownUserRequestSerializer, EventDraftSerializer, DashboardItemSerializer, \
    EventRouterKwargsSerializer, UserRouterKwargsSerializer, UserSearchSerializer, AttendanceListPageSerializer, \
    GetAttendanceListRequestSerializer
from api.helpers import parse_request_data
from bis.models import User, Location
from bis.permissions import Permissions
from event.models import Event, EventFinanceReceipt, EventPhoto, EventPropagationImage, EventDraft, \
    EventAttendanceListPage
from login_code.models import ThrottleLog
from opportunities.models import Opportunity
from other.models import DashboardItem
from questionnaire.models import Question, EventApplication
from xlsx_export import export

safe_http_methods = [m.lower() for m in SAFE_METHODS]


class PermissionViewSetBase(ModelViewSet):
    lookup_field = 'id'
    permission_classes = [IsAuthenticated, BISPermissions]
    kwargs_serializer_class = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if self.kwargs_serializer_class:
            self.kwargs_serializer_class(data=self.kwargs).is_valid(raise_exception=True)

    def get_queryset(self):
        queryset = super(PermissionViewSetBase, self).get_queryset()
        perms = Permissions(self.request.user, self.serializer_class.Meta.model, 'frontend')
        return perms.filter_queryset(queryset)


class UserViewSet(PermissionViewSetBase):
    search_fields = 'all_emails__email', 'phone', 'first_name', 'last_name', 'nickname', 'birth_name'
    serializer_class = UserSerializer
    filterset_class = UserFilter
    queryset = User.objects.select_related(
        'close_person',
        'offers',
        'address',
        'address__region',
        'contact_address',
        'contact_address__region',
        'donor',
        'health_insurance_company',
        'pronoun',
    ).prefetch_related(
        'offers__programs',
        'offers__organizer_roles',
        'offers__team_roles',
        'all_emails',
        'donor__donations',
        'donor__donations__donation_source',
        'donor__variable_symbols',
        'memberships',
        'memberships__category',
        'qualifications',
        'qualifications__category',
        'qualifications__approved_by',
        'roles',
    )


class ParticipantsViewSet(UserViewSet):
    http_method_names = safe_http_methods
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(participated_in_events__event=self.kwargs['event_id'])


class RegisteredViewSet(UserViewSet):
    http_method_names = safe_http_methods
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(applications__event_registration__event=self.kwargs['event_id'])


class OrganizersViewSet(UserViewSet):
    http_method_names = safe_http_methods
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(events_where_was_organizer=self.kwargs['event_id'])


class EventViewSet(PermissionViewSetBase):
    search_fields = 'name',
    serializer_class = EventSerializer
    filterset_class = EventFilter
    queryset = Event.objects.select_related(
        'finance',
        'finance__grant_category',
        'propagation',
        'intended_for',
        'vip_propagation',
        'registration',
        'registration__questionnaire',
        'record',
        'category',
        'program',
    ).prefetch_related(
        'propagation__diets',
        'record__contacts',
    )


class ParticipatedInViewSet(EventViewSet):
    http_method_names = safe_http_methods
    kwargs_serializer_class = UserRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(record__participants=self.kwargs['user_id'])


class RegisteredInViewSet(EventViewSet):
    http_method_names = safe_http_methods
    kwargs_serializer_class = UserRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(registration__applications__user=self.kwargs['user_id'])


class WhereWasOrganizerViewSet(EventViewSet):
    http_method_names = safe_http_methods
    kwargs_serializer_class = UserRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(other_organizers=self.kwargs['user_id'])


class EventDraftViewSet(PermissionViewSetBase):
    serializer_class = EventDraftSerializer
    queryset = EventDraft.objects.all()


class DashboardItemViewSet(PermissionViewSetBase):
    serializer_class = DashboardItemSerializer
    http_method_names = safe_http_methods

    def get_queryset(self):
        return DashboardItem.get_items_for_user(self.request.user)


class LocationViewSet(PermissionViewSetBase):
    search_fields = 'name', 'description'
    serializer_class = LocationSerializer
    filterset_class = LocationFilter
    queryset = Location.objects.select_related(
        'patron',
        'contact_person',
        'region',
        'program',
        'accessibility_from_prague',
        'accessibility_from_brno',
    )


class OpportunityViewSet(PermissionViewSetBase):
    search_fields = 'name', 'introduction'
    serializer_class = OpportunitySerializer
    queryset = Opportunity.objects.select_related('category')
    kwargs_serializer_class = UserRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(contact_person=self.kwargs['user_id'])


class FinanceReceiptViewSet(PermissionViewSetBase):
    serializer_class = FinanceReceiptSerializer
    queryset = EventFinanceReceipt.objects.all()
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(finance__event=self.kwargs['event_id'])


class EventPropagationImageViewSet(PermissionViewSetBase):
    serializer_class = EventPropagationImageSerializer
    queryset = EventPropagationImage.objects.all()
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(propagation__event=self.kwargs['event_id'])


class EventPhotoViewSet(PermissionViewSetBase):
    serializer_class = EventPhotoSerializer
    queryset = EventPhoto.objects.all()
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(record__event=self.kwargs['event_id'])


class AttendanceListPageViewSet(PermissionViewSetBase):
    serializer_class = AttendanceListPageSerializer
    queryset = EventAttendanceListPage.objects.all()
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(record__event=self.kwargs['event_id'])


class QuestionViewSet(PermissionViewSetBase):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(questionnaire__event_registration__event=self.kwargs['event_id'])


class EventApplicationViewSet(PermissionViewSetBase):
    serializer_class = EventApplicationSerializer
    queryset = EventApplication.objects \
        .select_related('close_person', 'address', 'pronoun') \
        .prefetch_related('answers', 'answers__question')
    kwargs_serializer_class = EventRouterKwargsSerializer

    def get_queryset(self):
        return super().get_queryset().filter(event_registration__event=self.kwargs['event_id'])

    def get_permissions(self):
        if self.action == 'create':
            return []
        return super().get_permissions()


class UserSearchViewSet(ListModelMixin, GenericViewSet):
    lookup_field = 'id'
    permission_classes = [IsAuthenticated]
    search_fields = 'all_emails__email', 'phone', 'first_name', 'last_name', 'nickname', 'birth_name'
    serializer_class = UserSearchSerializer
    queryset = User.objects.select_related(
        'address',
    )


@extend_schema(parameters=[GetUnknownUserRequestSerializer],
               responses={
                   HTTP_200_OK: UserSerializer,
                   HTTP_404_NOT_FOUND: OpenApiResponse(description='Not found'),
                   HTTP_429_TOO_MANY_REQUESTS: OpenApiResponse(description='Too many requests for first_name + '
                                                                           'last_name, try again in one day'),
               })
@api_view(['get'])
@permission_classes([IsAuthenticated])
@parse_request_data(GetUnknownUserRequestSerializer, 'query_params')
def get_unknown_user(request, data):
    key = f"{data['first_name']}_{data['last_name']}_{request.user.id}"
    ThrottleLog.check_throttled('get_unknown_user', key, 3, 24)
    user = User.objects.filter(**data).first()

    if not user:
        raise NotFound()

    return Response(UserSerializer(instance=user, context={'request': request}).data)


@extend_schema(parameters=[GetAttendanceListRequestSerializer],
               responses={
                   HTTP_200_OK: None,
                   HTTP_404_NOT_FOUND: OpenApiResponse(description='Not found'),
                   HTTP_403_FORBIDDEN: OpenApiResponse(description='Forbidden'),
               })
@api_view(['get'])
@permission_classes([IsAuthenticated])
@parse_request_data(GetAttendanceListRequestSerializer, 'query_params')
def get_attendance_list(request, data, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not Permissions(request.user, Event, 'frontend').has_change_permission(event):
        return HttpResponseForbidden()
    return export.get_attendance_list(event)[data['formatting']]

@extend_schema(responses={
                   HTTP_200_OK: None,
                   HTTP_404_NOT_FOUND: OpenApiResponse(description='Not found'),
                   HTTP_403_FORBIDDEN: OpenApiResponse(description='Forbidden'),
               })
@api_view(['get'])
@permission_classes([IsAuthenticated])
def get_participants_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if not Permissions(request.user, Event, 'frontend').has_change_permission(event):
        return HttpResponseForbidden()

    return export.export_to_xlsx(..., ..., event.record.get_all_participants())