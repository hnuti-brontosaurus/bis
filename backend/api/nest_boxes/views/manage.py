from api.nest_boxes.filters import (
    BatchFilter,
    CheckFilter,
    NestBoxFilter,
    SeasonStateFilter,
)
from api.nest_boxes.serializers import (
    AreaDetailSerializer,
    AreaSerializer,
    BatchSerializer,
    BoxIdsSerializer,
    BoxSerializer,
    BoxWarningsQuerySerializer,
    CheckPhotoUploadSerializer,
    CheckSerializer,
    EndBoxSerializer,
    GpxImportSerializer,
    HistorySerializer,
    ImportRowSerializer,
    MapBoxSerializer,
    box_warnings_data,
    warnings_data,
)
from api.nest_boxes.views.base import (
    IsManager,
    NestBoxAPIMixin,
    box_queryset,
    require_manage,
)
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Count, OuterRef, Prefetch, Q, Subquery
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.utils.text import get_valid_filename
from django.utils.timezone import localdate, now
from nest_boxes.boxes import (
    create_box,
    delete_box,
    end_box,
    season_state_counts,
    suggested_batch_boxes,
    update_box,
)
from nest_boxes.checks import (
    close_batch,
    confirm_batch,
    confirm_check,
    delete_check,
    edit_check,
    enter_check,
)
from nest_boxes.gpx import apply_import, export_gpx, import_rows, parse_gpx
from nest_boxes.models import Batch, Check, CheckPhoto, NestBox
from nest_boxes.permissions import can_manage_all, manageable_areas
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from xlsx_export.export import XLSXWriter, download
from xlsx_export.serializers import NestBoxExportSerializer


class ManagerViewSet(NestBoxAPIMixin, viewsets.ModelViewSet):
    permission_classes = [IsManager]

    def areas(self):
        return manageable_areas(self.request.user)


class AreaViewSet(ManagerViewSet):
    def get_queryset(self):
        areas = (
            self.areas()
            .with_markers()
            .select_related("administration_unit")
            .order_by("name")
        )
        if self.action == "retrieve":
            areas = areas.prefetch_related(Prefetch("boxes", queryset=box_queryset()))
        return areas

    def get_serializer_class(self):
        return AreaDetailSerializer if self.action == "retrieve" else AreaSerializer

    def require_manage_all(self):
        if not can_manage_all(self.request.user):
            raise PermissionDenied

    def perform_create(self, serializer):
        self.require_manage_all()
        serializer.save()

    def perform_update(self, serializer):
        # A board member moving the area to another unit would give it away
        unit = serializer.validated_data.get("administration_unit")
        if unit and unit != serializer.instance.administration_unit:
            self.require_manage_all()
        serializer.save()

    def perform_destroy(self, instance):
        self.require_manage_all()
        instance.delete()

    @action(detail=False)
    def season_states(self, request):
        """Per area, how many of the boxes the filters pick are in each season state."""
        boxes = SeasonStateFilter(
            request.query_params,
            NestBox.objects.with_season_state().filter(area__in=self.areas()),
        )
        if not boxes.is_valid():
            raise ValidationError(boxes.errors)
        return Response(season_state_counts(boxes.qs))

    def filtered_boxes(self, area):
        return NestBoxFilter(
            self.request.query_params,
            box_queryset().filter(area=area).select_related("type", "end_reason"),
        ).qs

    @action(detail=True, url_path="export.gpx")
    def export_gpx(self, request, pk):
        area = self.get_object()
        response = HttpResponse(
            export_gpx(self.filtered_boxes(area)), content_type="application/gpx+xml"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{get_valid_filename(area.name)}.gpx"'
        )
        return response

    @action(detail=True, url_path="export.xlsx")
    def export_xlsx(self, request, pk):
        area = self.get_object()
        name = get_valid_filename(area.name)
        writer = XLSXWriter(name)
        writer.from_queryset(
            self.filtered_boxes(area), NestBoxExportSerializer, "Budky"
        )
        return download(writer.get_file(), f"{name}.xlsx")

    @action(detail=True, methods=["post"])
    def import_gpx(self, request, pk):
        area = self.get_object()
        serializer = GpxImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        rows = import_rows(area, parse_gpx(data["gpx"]), data["type"])
        if data["apply"]:
            apply_import(
                area,
                rows,
                set(data["skip"]),
                request.user,
                localdate(),
                data["installed_on"],
                data["type"],
            )
        return Response(
            {
                "rows": ImportRowSerializer(rows, many=True).data,
                "applied": data["apply"],
            }
        )


class BoxViewSet(ManagerViewSet):
    serializer_class = BoxSerializer
    filterset_class = NestBoxFilter
    search_fields = ("name", "previous_names")

    def get_queryset(self):
        return box_queryset().filter(area__in=self.areas())

    def respond(self, box, status=None):
        box = self.get_queryset().get(pk=box.pk)
        return Response(
            self.get_serializer(box).data | {"warnings": box_warnings_data(box)},
            status=status,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        values = dict(serializer.validated_data)
        require_manage(request.user, values["area"])
        batch = values.pop("batch", None)
        if batch and batch.area != values["area"]:
            raise ValidationError({"batch_id": "Obchůzka patří k jiné oblasti."})
        box = create_box(values, request.user, localdate())
        if batch:
            batch.boxes.add(box)
        return self.respond(box, HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        if "area" in serializer.validated_data:
            require_manage(request.user, serializer.validated_data["area"])
        update_box(
            serializer.instance, serializer.validated_data, request.user, localdate()
        )
        return self.respond(serializer.instance)

    def perform_destroy(self, instance):
        delete_box(instance)

    @action(detail=False)
    def map(self, request):
        """Every box of the manager's areas, unpaginated and with the map's fields only."""
        boxes = self.get_queryset().select_related(None)
        return Response(MapBoxSerializer(boxes, many=True).data)

    @action(detail=True)
    def history(self, request, pk):
        history = self.get_object().history.select_related("user")
        return Response(HistorySerializer(history, many=True).data)

    @action(detail=True, methods=["post"])
    def end(self, request, pk):
        box = self.get_object()
        serializer = EndBoxSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        end_box(
            box,
            serializer.validated_data["end_reason"],
            serializer.validated_data["ended_on"],
            request.user,
        )
        return self.respond(box)

    @action(detail=False)
    def warnings(self, request):
        serializer = BoxWarningsQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        require_manage(request.user, data["area"])
        return Response(
            warnings_data(
                data["area"],
                data.get("location"),
                data.get("type"),
                data.get("name"),
                data.get("exclude"),
            )
        )


class CheckViewSet(ManagerViewSet):
    serializer_class = CheckSerializer
    filterset_class = CheckFilter

    def get_queryset(self):
        return (
            Check.objects.filter(box__area__in=self.areas())
            .select_related("entered_by", "confirmed_by")
            .prefetch_related("occupants", "photos")
        )

    def respond(self, check, status=None):
        return Response(
            self.get_serializer(self.get_queryset().get(pk=check.pk)).data,
            status=status,
        )

    def perform_destroy(self, instance):
        delete_check(instance)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        check, occupants = serializer.build()
        require_manage(request.user, check.box.area)
        if check.batch and check.batch.area_id != check.box.area_id:
            raise ValidationError({"batch_id": "Obchůzka patří k jiné oblasti."})
        if check.made_at is None:
            check.made_at = now()
        enter_check(check, occupants, request.user)
        return self.respond(check, HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            self.get_object(), data=request.data, partial=kwargs.get("partial", False)
        )
        serializer.is_valid(raise_exception=True)
        check, occupants = serializer.build()
        if "occupants" not in serializer.validated_data:
            occupants = list(check.occupants.all())
        edit_check(check, occupants, request.user)
        return self.respond(check)

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk):
        check = self.get_object()
        confirm_check(check, request.user)
        return self.respond(check)


class CheckPhotoViewSet(
    NestBoxAPIMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Photos are POSTed one by one with the check's id as `parent_id`."""

    permission_classes = [IsManager]
    serializer_class = CheckPhotoUploadSerializer

    def get_queryset(self):
        return CheckPhoto.objects.filter(
            box_check__box__area__in=manageable_areas(self.request.user)
        )

    def perform_create(self, serializer):
        require_manage(
            self.request.user, serializer.validated_data["box_check"].box.area
        )
        serializer.save()


def batch_queryset():
    """With the progress counts the batch page and the open batches badge show."""
    checked_boxes = (
        NestBox.objects.filter(
            batches=OuterRef("pk"), checks__season=Check.current_season()
        )
        .order_by()
        .values("batches")
        .annotate(count=Count("pk", distinct=True))
        .values("count")
    )
    return (
        Batch.objects.annotate(
            box_count=Count("boxes", distinct=True),
            pending_count=Count(
                "checks", filter=Q(checks__is_confirmed=False), distinct=True
            ),
            checked_count=Coalesce(Subquery(checked_boxes), 0),
        )
        .select_related("area", "created_by", "confirmed_by")
        .prefetch_related(Prefetch("boxes", queryset=NestBox.objects.only("pk")))
    )


class BatchViewSet(ManagerViewSet):
    serializer_class = BatchSerializer
    filterset_class = BatchFilter

    def get_queryset(self):
        return batch_queryset().filter(area__in=self.areas())

    def respond(self, batch, status=None):
        return Response(
            self.get_serializer(self.get_queryset().get(pk=batch.pk)).data,
            status=status,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        area = serializer.validated_data["area"]
        require_manage(request.user, area)
        boxes = serializer.validated_data.get("boxes")
        if boxes is None:
            serializer.validated_data["boxes"] = list(
                suggested_batch_boxes(area, Check.current_season())
            )
        batch = serializer.save(created_by=request.user)
        return self.respond(batch, HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        return self.respond(self.get_object())

    @action(detail=False)
    def open(self, request):
        batches = self.get_queryset().filter(closed_at=None)
        return Response(self.get_serializer(batches, many=True).data)

    @action(detail=False)
    def suggested(self, request):
        """The boxes a new batch of `?area=` starts with."""
        area = self.areas().filter(pk=request.query_params.get("area")).first()
        if area is None:
            raise ValidationError({"area": "Neznámá oblast."})
        boxes = suggested_batch_boxes(area, Check.current_season())
        return Response({"box_ids": list(boxes.values_list("pk", flat=True))})

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk):
        batch = self.get_object()
        confirm_batch(batch, request.user)
        return self.respond(batch)

    @action(detail=True, methods=["post"])
    def close(self, request, pk):
        batch = self.get_object()
        close_batch(batch)
        return self.respond(batch)

    def box_ids(self, batch):
        serializer = BoxIdsSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        boxes = NestBox.objects.filter(
            pk__in=serializer.validated_data["box_ids"], area=batch.area
        )
        if len(boxes) != len(set(serializer.validated_data["box_ids"])):
            raise ValidationError({"box_ids": "Některé budky nejsou v této oblasti."})
        return boxes

    @action(detail=True, methods=["post"])
    def add_boxes(self, request, pk):
        batch = self.get_object()
        batch.boxes.add(*self.box_ids(batch))
        return self.respond(batch)

    @action(detail=True, methods=["post"])
    def remove_boxes(self, request, pk):
        batch = self.get_object()
        batch.boxes.remove(*self.box_ids(batch))
        return self.respond(batch)
