from regions.models import Region
from regions.serializers import RegionSerializer
from rest_framework.viewsets import ReadOnlyModelViewSet


class RegionViewSet(ReadOnlyModelViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()
