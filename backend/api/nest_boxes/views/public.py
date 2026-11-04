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
    IsBudkarOrReadOnly,
    NestBoxAPIMixin,
    help_articles,
)
from django.contrib.gis.db.models.functions import PointOnSurface
from django.db.models import Count
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from nest_boxes.models import Area, Batch, HelpArticle, HelpImage, in_use
from nest_boxes.permissions import can_manage_all, manageable_areas
from nest_boxes.statistics import default_season, season_statistics
from regions.models import Region
from rest_framework import mixins, viewsets
from rest_framework.fields import IntegerField
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
        areas = manageable_areas(user)
        return Response(
            {
                "is_authenticated": user.is_authenticated,
                "user": (
                    PersonSerializer(user).data | {"email": user.email}
                    if user.is_authenticated
                    else None
                ),
                "is_budkar": can_manage_all(user),
                "managed_area_ids": list(areas.values_list("id", flat=True)),
                "open_batch_count": Batch.objects.filter(
                    area__in=areas, closed_at=None
                ).count(),
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


class PublicRegionsView(NestBoxAPIMixin, APIView):
    """Every region with its outline and boxes in use, for the landing map."""

    def get(self, request):
        regions = Region.objects.annotate(
            marker=PointOnSurface("area"),
            box_count=Count("nest_boxes", filter=in_use("nest_boxes__")),
        )
        return Response(PublicRegionSerializer(regions, many=True).data)


class StatisticsView(NestBoxAPIMixin, APIView):
    def get(self, request):
        season = request.query_params.get("season")
        statistics = season_statistics(
            default_season()
            if season is None
            else IntegerField(min_value=1900).run_validation(season)
        )
        for row in statistics["areas"]:
            row["area"] = StatisticsAreaSerializer(row["area"]).data
        return Response(statistics)


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
    permission_classes = [IsBudkarOrReadOnly]
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
    permission_classes = [IsBudkarOrReadOnly]
    queryset = HelpImage.objects.all()
