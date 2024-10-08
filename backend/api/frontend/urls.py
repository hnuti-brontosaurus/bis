from api import frontend
from api.frontend.views import (
    AttendanceListPageViewSet,
    DashboardItemViewSet,
    EventApplicationViewSet,
    EventDraftViewSet,
    EventFeedbackViewSet,
    EventPhotoViewSet,
    EventPropagationImageViewSet,
    EventViewSet,
    FinanceReceiptViewSet,
    InquiryViewSet,
    LocationViewSet,
    OpportunityViewSet,
    OrganizersViewSet,
    ParticipantsViewSet,
    ParticipatedInViewSet,
    QuestionViewSet,
    RegisteredInViewSet,
    RegisteredViewSet,
    UserSearchViewSet,
    UserViewSet,
    WhereWasOrganizerViewSet,
)
from django.urls import include, path
from rest_framework_nested import routers

router = routers.DefaultRouter()

router.register("users", UserViewSet, "users")
router.register("search_users", UserSearchViewSet, "search_users")
router.register("events", EventViewSet, "events")
router.register("locations", LocationViewSet, "locations")
router.register("event_drafts", EventDraftViewSet, "event_drafts")
router.register("dashboard_items", DashboardItemViewSet, "dashboard_items")

users_router = routers.NestedDefaultRouter(router, "users", lookup="user")
users_router.register("opportunities", OpportunityViewSet)

users_router.register("participated_in_events", ParticipatedInViewSet)
users_router.register("registered_in_events", RegisteredInViewSet)
users_router.register("events_where_was_organizer", WhereWasOrganizerViewSet)

events_router = routers.NestedDefaultRouter(router, "events", lookup="event")
events_router.register("finance/receipts", FinanceReceiptViewSet)
events_router.register("propagation/images", EventPropagationImageViewSet)
events_router.register("record/photos", EventPhotoViewSet)
events_router.register("record/attendance_list_pages", AttendanceListPageViewSet)
events_router.register("registration/questionnaire/questions", QuestionViewSet)
events_router.register("registration/applications", EventApplicationViewSet)
events_router.register("record/feedback_form/inquiries", InquiryViewSet)
events_router.register("record/feedbacks", EventFeedbackViewSet)

events_router.register("record/participants", ParticipantsViewSet)
events_router.register("registered", RegisteredViewSet)
events_router.register("organizers", OrganizersViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(users_router.urls)),
    path("", include(events_router.urls)),
    path("get_unknown_user/", frontend.views.get_unknown_user),
    path("get_unknown_user_by_email/", frontend.views.get_unknown_user_by_email),
    path("export_users/", frontend.views.export_users),
    path(
        "events/<int:event_id>/get_attendance_list/", frontend.views.get_attendance_list
    ),
    path(
        "events/<int:event_id>/get_participants_list/",
        frontend.views.get_participants_list,
    ),
    path("events/<int:event_id>/export_files/", frontend.views.export_files),
    path("events/<int:event_id>/get_feedbacks/", frontend.views.get_feedbacks),
]
