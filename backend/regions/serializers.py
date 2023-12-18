from regions.models import Region
from rest_framework.serializers import ModelSerializer


class RegionSerializer(ModelSerializer):
    class Meta:
        model = Region
        exclude = ("area",)
