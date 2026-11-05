from api.nest_boxes.serializers import (
    HelpArticleSerializer,
    HelpImageSerializer,
    PersonSerializer,
    PublicAreaSerializer,
    PublicRegionSerializer,
    StatisticsAreaSerializer,
    WantToHangSerializer,
    categories_data,
)
from api.nest_boxes.views.base import (
    IsManagerOrReadOnly,
    NestBoxAPIMixin,
    help_articles,
)
from django.contrib.gis.db.models.functions import PointOnSurface
from django.db.models import Count
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from nest_boxes.models import (
    Area,
    Batch,
    HelpArticle,
    HelpImage,
    NestBox,
    NestBoxType,
)
from nest_boxes.permissions import is_manager
from nest_boxes.public_cache import cached
from nest_boxes.statistics import (
    default_season,
    season_statistics,
    statistics_by_season,
)
from regions.models import Region
from rest_framework import mixins, viewsets
from rest_framework.fields import IntegerField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from nest_boxes import emails


class WhoAmIView(NestBoxAPIMixin, APIView):
    # The SPA sends the token back as X-CSRFToken on every write
    @method_decorator(ensure_csrf_cookie)
    def get(self, request):
        user = request.user
        manager = is_manager(user)
        return Response(
            {
                "is_authenticated": user.is_authenticated,
                "user": (
                    PersonSerializer(user).data | {"email": user.email}
                    if user.is_authenticated
                    else None
                ),
                "is_manager": manager,
                "open_batch_count": (
                    Batch.objects.filter(closed_at=None).count() if manager else 0
                ),
            }
        )


class PublicAreaViewSet(
    NestBoxAPIMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    """Areas as markers with counts. Never a box's coordinates."""

    serializer_class = PublicAreaSerializer
    queryset = (
        Area.objects.with_markers()
        .select_related("administration_unit")
        .order_by("name")
    )
    filterset_fields = ("administration_unit",)


# Where the landing map shows the boxes outside every Czech region
ABROAD_MARKER = {"type": "Point", "coordinates": [17.4194825, 50.7438250]}


def _cached(request, compute):
    return Response(cached(request.get_full_path(), compute))


def _regions():
    # Counted apart: grouped by region, the marker would be computed per box
    counts = dict(
        NestBox.objects.in_use().values_list("region").annotate(Count("pk")).order_by()
    )
    regions = Region.objects.defer("area").annotate(marker=PointOnSurface("area"))
    abroad = {
        "id": "abroad",
        "name": "V zahraničí",
        "marker": ABROAD_MARKER,
        "box_count": counts.get(None, 0),
    }
    return [
        *(
            {**region, "box_count": counts.get(region["id"], 0)}
            for region in PublicRegionSerializer(regions, many=True).data
        ),
        abroad,
    ]


class PublicRegionsView(NestBoxAPIMixin, APIView):
    """Every region with its boxes in use, for the landing map, and the boxes
    abroad as one more region."""

    def get(self, request):
        return _cached(request, _regions)


def _types(request):
    return PrimaryKeyRelatedField(
        queryset=NestBoxType.objects.all(), many=True, required=False
    ).run_validation(request.query_params.getlist("type"))


def _serialize_areas(statistics):
    for row in statistics["areas"]:
        row["area"] = StatisticsAreaSerializer(row["area"]).data
    return statistics


class StatisticsView(NestBoxAPIMixin, APIView):
    def get(self, request):
        season = request.query_params.get("season")
        season = (
            default_season()
            if season is None
            else IntegerField(min_value=1900).run_validation(season)
        )
        types = _types(request)
        return _cached(
            request, lambda: _serialize_areas(season_statistics(season, types))
        )


class SeasonStatisticsView(NestBoxAPIMixin, APIView):
    def get(self, request):
        types = _types(request)
        return _cached(request, lambda: _serialize_areas(statistics_by_season(types)))


class WantToHangThrottle(UserRateThrottle):
    rate = "10/hour"


class WantToHangView(NestBoxAPIMixin, APIView):
    throttle_classes = [WantToHangThrottle]

    def post(self, request):
        serializer = WantToHangSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        emails.want_to_hang(serializer.validated_data)
        return Response(status=HTTP_204_NO_CONTENT)


class CategoriesView(NestBoxAPIMixin, APIView):
    def get(self, request):
        return Response(categories_data())


class HelpArticleViewSet(
    NestBoxAPIMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "slug"
    serializer_class = HelpArticleSerializer
    permission_classes = [IsManagerOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        return help_articles()

    def get_object(self):
        if self.kwargs["slug"] not in HelpArticle.Slug.values:
            raise Http404
        return super().get_object()


class HelpImageViewSet(
    NestBoxAPIMixin, mixins.CreateModelMixin, viewsets.GenericViewSet
):
    """An image is uploaded the moment it is inserted; the article save deletes it."""

    serializer_class = HelpImageSerializer
    permission_classes = [IsManagerOrReadOnly]
    queryset = HelpImage.objects.all()
