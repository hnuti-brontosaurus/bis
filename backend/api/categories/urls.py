from django.urls import path, include
from rest_framework import routers

from bis.helpers import to_snake_case
from categories.views import *
from regions.views import RegionViewSet

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
    LocationProgramCategoryViewSet,
    LocationAccessibilityCategoryViewSet,
    RoleCategoryViewSet,
    HealthInsuranceCompanyViewSet,
    PronounCategoryViewSet,
    RegionViewSet,
]:
    model_name = view_set.serializer_class.Meta.model.__name__
    model_name = to_snake_case(model_name)
    if model_name.endswith('y'):
        model_name = model_name[:-1] + 'ies'
    else:
        model_name += 's'

    router.register(model_name, view_set, model_name)

urlpatterns = [
    path('', include(router.urls)),
]
