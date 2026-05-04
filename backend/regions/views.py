from categories.views import CachedReadOnlyModelViewSet
from regions.models import Region
from regions.serializers import RegionSerializer


class RegionViewSet(CachedReadOnlyModelViewSet):
    serializer_class = RegionSerializer
    queryset = Region.objects.all()
