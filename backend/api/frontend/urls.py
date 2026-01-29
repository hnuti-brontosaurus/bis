from django.urls import include, path
from rest_framework_nested import routers

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

router = routers.DefaultRouter()

router.register("users", UserViewSet, "users")
router.register("search_users", UserSearchViewSet, "search_users")
router.register("events", EventViewSet, "events")
router.register("locations", LocationViewSet, "locations")
router.register("event_drafts", EventDraftViewSet, "event_drafts")
router.register("dashboard_items", DashboardItemViewSet, "dashboard_items")

users_router = routers.NestedDefaultRouter(router, "users", lookup="user")
users_router.register("opportunities", OpportunityViewSet, "user_opportunities")

users_router.register(
    "participated_in_events", ParticipatedInViewSet, "participated_in_events"
)
users_router.register(
    "registered_in_events", RegisteredInViewSet, "registered_in_events"
)
users_router.register(
    "events_where_was_organizer", WhereWasOrganizerViewSet, "events_where_was_organizer"
)

events_router = routers.NestedDefaultRouter(router, "events", lookup="event")
events_router.register("finance/receipts", FinanceReceiptViewSet, "finance_receipts")
events_router.register(
    "propagation/images", EventPropagationImageViewSet, "propagation_images"
)
events_router.register("record/photos", EventPhotoViewSet, "record_photos")
events_router.register(
    "record/attendance_list_pages", AttendanceListPageViewSet, "attendance_list_pages"
)
events_router.register(
    "registration/questionnaire/questions", QuestionViewSet, "questionnaire_questions"
)
events_router.register(
    "registration/applications", EventApplicationViewSet, "event_applications"
)
events_router.register("feedback_form/inquiries", InquiryViewSet, "feedback_inquiries")
events_router.register("feedbacks", EventFeedbackViewSet, "event_feedbacks")

events_router.register("record/participants", ParticipantsViewSet, "participants")
events_router.register("registered", RegisteredViewSet, "registered")
events_router.register("organizers", OrganizersViewSet, "organizers")

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
