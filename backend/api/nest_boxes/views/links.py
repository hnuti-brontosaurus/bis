"""What a volunteer holding a batch link may do: no account, only the batch's boxes."""

from api.nest_boxes.serializers import (
    CheckPhotoUploadSerializer,
    HelpArticleSerializer,
    LinkAreaSerializer,
    LinkBatchSerializer,
    LinkBoxSerializer,
    LinkCheckSerializer,
    LinkNewBoxSerializer,
    box_warnings_data,
    categories_data,
)
from api.nest_boxes.views.base import NestBoxAPIMixin, help_articles
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from nest_boxes.checks import ensure_open, submit_box, submit_check
from nest_boxes.models import Batch, Check, NestBox
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView


def open_batch(token):
    batch = get_object_or_404(
        Batch.objects.select_related("area__administration_unit", "cleaned_by"),
        token=token,
    )
    ensure_open(batch)
    return batch


class LinkView(NestBoxAPIMixin, APIView):
    def get(self, request, token):
        """Everything the phone stores for offline use when the link is opened."""
        batch = open_batch(token)
        season = Check.current_season()
        boxes = NestBox.objects.with_season_state().filter(batches=batch)
        checks = Check.objects.filter(
            box__in=batch.boxes.all(), season=season
        ).prefetch_related("occupants", "photos")
        return Response(
            {
                "batch": LinkBatchSerializer(batch).data,
                "area": LinkAreaSerializer(batch.area).data,
                "season": season,
                "boxes": LinkBoxSerializer(boxes, many=True).data,
                "checks": LinkCheckSerializer(checks, many=True).data,
                "categories": categories_data(),
                "help_articles": HelpArticleSerializer(help_articles(), many=True).data,
            }
        )


class LinkChecksView(NestBoxAPIMixin, APIView):
    def post(self, request, token):
        """Upsert by the client's id; `accepted` is false when a later check won."""
        batch = open_batch(token)
        serializer = LinkCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check, occupants = serializer.build()
        stored = submit_check(batch, check, occupants)
        accepted = stored is check
        box = NestBox.objects.with_season_state().get(pk=stored.box_id)
        return Response(
            {
                "accepted": accepted,
                "check": LinkCheckSerializer(stored).data,
                "season_state": box.season_state,
            },
            status=HTTP_201_CREATED if accepted else HTTP_200_OK,
        )


class LinkBoxesView(NestBoxAPIMixin, APIView):
    def post(self, request, token):
        """A box the volunteer hung and its check, or a resend of them."""
        batch = open_batch(token)
        serializer = LinkNewBoxSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = dict(serializer.validated_data)
        check = Check(**values.pop("check"))
        box, check = submit_box(batch, values, check)
        box = NestBox.objects.with_season_state().get(pk=box.pk)
        return Response(
            LinkBoxSerializer(box).data
            | {
                "check": LinkCheckSerializer(check).data,
                "warnings": box_warnings_data(box),
            },
            status=HTTP_201_CREATED,
        )


class LinkCheckPhotosView(NestBoxAPIMixin, APIView):
    def post(self, request, token):
        batch = open_batch(token)
        serializer = CheckPhotoUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check = serializer.validated_data["box_check"]
        if check.batch_id != batch.pk or check.is_confirmed:
            raise PermissionDenied
        # The phone resends a photo whose answer it lost; the order names it
        check.photos.filter(order=serializer.validated_data.get("order", 0)).delete()
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)
