from rest_framework.serializers import ModelSerializer

from categories.models import *


class GrantCategorySerializer(ModelSerializer):
    class Meta:
        model = GrantCategory
        exclude = ()


class EventIntendedForCategorySerializer(ModelSerializer):
    class Meta:
        model = EventIntendedForCategory
        exclude = ()


class DietCategorySerializer(ModelSerializer):
    class Meta:
        model = DietCategory
        exclude = ()


class QualificationCategorySerializer(ModelSerializer):
    class Meta:
        model = QualificationCategory
        exclude = ()


class AdministrationUnitCategorySerializer(ModelSerializer):
    class Meta:
        model = AdministrationUnitCategory
        exclude = ()


class MembershipCategorySerializer(ModelSerializer):
    class Meta:
        model = MembershipCategory
        exclude = ()


class EventGroupCategorySerializer(ModelSerializer):
    class Meta:
        model = EventGroupCategory
        exclude = ()


class EventCategorySerializer(ModelSerializer):
    class Meta:
        model = EventCategory
        exclude = ()


class EventProgramCategorySerializer(ModelSerializer):
    class Meta:
        model = EventProgramCategory
        exclude = ()


class DonationSourceCategorySerializer(ModelSerializer):
    class Meta:
        model = DonationSourceCategory
        exclude = '_import_id',


class OrganizerRoleCategorySerializer(ModelSerializer):
    class Meta:
        model = OrganizerRoleCategory
        exclude = ()


class TeamRoleCategorySerializer(ModelSerializer):
    class Meta:
        model = TeamRoleCategory
        exclude = ()


class OpportunityCategorySerializer(ModelSerializer):
    class Meta:
        model = OpportunityCategory
        exclude = ()


class LocationProgramCategorySerializer(ModelSerializer):
    class Meta:
        model = LocationProgramCategory
        exclude = ()


class LocationAccessibilityCategorySerializer(ModelSerializer):
    class Meta:
        model = LocationAccessibilityCategory
        exclude = ()


class RoleCategorySerializer(ModelSerializer):
    class Meta:
        model = RoleCategory
        exclude = ()


class HealthInsuranceCompanySerializer(ModelSerializer):
    class Meta:
        model = HealthInsuranceCompany
        exclude = ()


class PronounCategorySerializer(ModelSerializer):
    class Meta:
        model = PronounCategory
        exclude = ()
