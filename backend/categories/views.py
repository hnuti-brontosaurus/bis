from bis.cache import CachedViewSetMixin
from categories.models import (
    AdministrationUnitCategory,
    DietCategory,
    DonationSourceCategory,
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    EventTag,
    GrantCategory,
    HealthInsuranceCompany,
    LocationAccessibilityCategory,
    LocationProgramCategory,
    MembershipCategory,
    OpportunityCategory,
    OpportunityPriority,
    OrganizerRoleCategory,
    PronounCategory,
    QualificationCategory,
    RoleCategory,
    TeamRoleCategory,
)
from categories.serializers import (
    AdministrationUnitCategorySerializer,
    DietCategorySerializer,
    DonationSourceCategorySerializer,
    EventCategorySerializer,
    EventGroupCategorySerializer,
    EventIntendedForCategorySerializer,
    EventProgramCategorySerializer,
    EventTagSerializer,
    GrantCategorySerializer,
    HealthInsuranceCompanySerializer,
    LocationAccessibilityCategorySerializer,
    LocationProgramCategorySerializer,
    MembershipCategorySerializer,
    OpportunityCategorySerializer,
    OpportunityPrioritySerializer,
    OrganizerRoleCategorySerializer,
    PronounCategorySerializer,
    QualificationCategorySerializer,
    RoleCategorySerializer,
    TeamRoleCategorySerializer,
)
from rest_framework.viewsets import ReadOnlyModelViewSet


class CachedReadOnlyModelViewSet(CachedViewSetMixin, ReadOnlyModelViewSet):
    cache_namespace = "categories"


class GrantCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = GrantCategorySerializer
    queryset = GrantCategory.objects.all()


class EventIntendedForCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = EventIntendedForCategorySerializer
    queryset = EventIntendedForCategory.objects.all()


class DietCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = DietCategorySerializer
    queryset = DietCategory.objects.all()


class QualificationCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = QualificationCategorySerializer
    queryset = QualificationCategory.objects.all()


class AdministrationUnitCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = AdministrationUnitCategorySerializer
    queryset = AdministrationUnitCategory.objects.all()


class MembershipCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = MembershipCategorySerializer
    queryset = MembershipCategory.objects.all()


class EventGroupCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = EventGroupCategorySerializer
    queryset = EventGroupCategory.objects.all()


class EventCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = EventCategorySerializer
    queryset = EventCategory.objects.all()


class EventTagViewSet(CachedReadOnlyModelViewSet):
    serializer_class = EventTagSerializer
    queryset = EventTag.objects.all()


class EventProgramCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = EventProgramCategorySerializer
    queryset = EventProgramCategory.objects.all()


class DonationSourceCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = DonationSourceCategorySerializer
    queryset = DonationSourceCategory.objects.all()


class OrganizerRoleCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = OrganizerRoleCategorySerializer
    queryset = OrganizerRoleCategory.objects.all()


class TeamRoleCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = TeamRoleCategorySerializer
    queryset = TeamRoleCategory.objects.all()


class OpportunityCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = OpportunityCategorySerializer
    queryset = OpportunityCategory.objects.all()


class OpportunityPriorityViewSet(CachedReadOnlyModelViewSet):
    serializer_class = OpportunityPrioritySerializer
    queryset = OpportunityPriority.objects.all()


class LocationProgramCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = LocationProgramCategorySerializer
    queryset = LocationProgramCategory.objects.all()


class LocationAccessibilityCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = LocationAccessibilityCategorySerializer
    queryset = LocationAccessibilityCategory.objects.all()


class RoleCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = RoleCategorySerializer
    queryset = RoleCategory.objects.all()


class HealthInsuranceCompanyViewSet(CachedReadOnlyModelViewSet):
    serializer_class = HealthInsuranceCompanySerializer
    queryset = HealthInsuranceCompany.objects.all()


class PronounCategoryViewSet(CachedReadOnlyModelViewSet):
    serializer_class = PronounCategorySerializer
    queryset = PronounCategory.objects.all()
