from api.web.views import *
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

router.register("events", EventViewSet, "events")
router.register("opportunities", OpportunityViewSet, "opportunities")
router.register(
    "administration_units", AdministrationUnitViewSet, "administration_units"
)


urlpatterns = [
    path("", include(router.urls)),
]
