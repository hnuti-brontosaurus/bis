from categories.views import (
    AdministrationUnitCategoryViewSet,
    DietCategoryViewSet,
    DonationSourceCategoryViewSet,
    EventCategoryViewSet,
    EventGroupCategoryViewSet,
    EventIntendedForCategoryViewSet,
    EventProgramCategoryViewSet,
    EventTagViewSet,
    GrantCategoryViewSet,
    HealthInsuranceCompanyViewSet,
    LocationAccessibilityCategoryViewSet,
    LocationProgramCategoryViewSet,
    MembershipCategoryViewSet,
    OpportunityCategoryViewSet,
    OpportunityPriorityViewSet,
    OrganizerRoleCategoryViewSet,
    PronounCategoryViewSet,
    QualificationCategoryViewSet,
    RoleCategoryViewSet,
    TeamRoleCategoryViewSet,
)
from django.urls import include, path
from regions.views import RegionViewSet
from rest_framework import routers

from bis.helpers import to_snake_case

router = routers.DefaultRouter()

for view_set in [
    GrantCategoryViewSet,
    EventIntendedForCategoryViewSet,
    DietCategoryViewSet,
    QualificationCategoryViewSet,
    AdministrationUnitCategoryViewSet,
    MembershipCategoryViewSet,
    EventGroupCategoryViewSet,
    EventCategoryViewSet,
    EventTagViewSet,
    EventProgramCategoryViewSet,
    DonationSourceCategoryViewSet,
    OrganizerRoleCategoryViewSet,
    TeamRoleCategoryViewSet,
    OpportunityCategoryViewSet,
    OpportunityPriorityViewSet,
    LocationProgramCategoryViewSet,
    LocationAccessibilityCategoryViewSet,
    RoleCategoryViewSet,
    HealthInsuranceCompanyViewSet,
    PronounCategoryViewSet,
    RegionViewSet,
]:
    model_name = view_set.serializer_class.Meta.model.__name__
    model_name = to_snake_case(model_name)
    if model_name.endswith("y"):
        model_name = model_name[:-1] + "ies"
    else:
        model_name += "s"

    router.register(model_name, view_set, model_name)

urlpatterns = [
    path("", include(router.urls)),
]
