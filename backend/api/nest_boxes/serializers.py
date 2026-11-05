from administration_units.models import AdministrationUnit
from api.cookbook.serializers import ArticleHTMLField, KeepsContentImages
from bis.models import User
from categories.models import (
    NestBoxEndReason,
    NestBoxNotCleanedReason,
    NestBoxOccupant,
    NestBoxType,
)
from django.core.exceptions import ValidationError as DjangoValidationError
from nest_boxes.boxes import duplicate_names, spacing_warnings
from nest_boxes.checks import parse_box_changes
from nest_boxes.emails import BOX_COUNTS, BOX_SOURCES
from nest_boxes.gpx import ImportRow
from nest_boxes.models import (
    Area,
    Batch,
    Check,
    CheckPhoto,
    HelpArticle,
    HelpImage,
    NestBox,
    NestBoxHistory,
)
from regions.models import Region
from rest_framework import serializers
from rest_framework.fields import (
    BooleanField,
    CharField,
    ChoiceField,
    DateField,
    DateTimeField,
    EmailField,
    FloatField,
    IntegerField,
    ListField,
    UUIDField,
)
from rest_framework.relations import PrimaryKeyRelatedField, SlugRelatedField
from rest_framework.serializers import (
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    as_serializer_error,
)
from rest_framework_gis.fields import GeometryField

# Degrees, about 400 m: a region's outline is only drawn on a map of the country
OUTLINE_TOLERANCE = 0.004


def related(model, source, **kwargs):
    return PrimaryKeyRelatedField(source=source, queryset=model.objects.all(), **kwargs)


def optional_related(model, source):
    return related(model, source, required=False, allow_null=True)


class UnitSerializer(ModelSerializer):
    class Meta:
        model = AdministrationUnit
        fields = ("id", "name", "abbreviation")


class PersonSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name")


class NestBoxTypeSerializer(ModelSerializer):
    class Meta:
        model = NestBoxType
        fields = (
            "id",
            "slug",
            "name",
            "order",
            "needs_cleaning",
            "hole_shape",
            "hole_min",
            "hole_max",
            "official_hole_min",
            "official_hole_max",
        )


class NestBoxOccupantSerializer(ModelSerializer):
    class Meta:
        model = NestBoxOccupant
        fields = ("id", "slug", "name", "order", "is_bird")


class NestBoxEndReasonSerializer(ModelSerializer):
    class Meta:
        model = NestBoxEndReason
        fields = ("id", "slug", "name", "order", "spot_reusable")


class NestBoxNotCleanedReasonSerializer(ModelSerializer):
    class Meta:
        model = NestBoxNotCleanedReason
        fields = ("id", "slug", "name", "order", "contents_known", "occupant_id")


def categories_data():
    return {
        "types": NestBoxTypeSerializer(NestBoxType.objects.all(), many=True).data,
        "occupants": NestBoxOccupantSerializer(
            NestBoxOccupant.objects.all(), many=True
        ).data,
        "end_reasons": NestBoxEndReasonSerializer(
            NestBoxEndReason.objects.all(), many=True
        ).data,
        "not_cleaned_reasons": NestBoxNotCleanedReasonSerializer(
            NestBoxNotCleanedReason.objects.all(), many=True
        ).data,
    }


class PublicAreaSerializer(ModelSerializer):
    administration_unit = UnitSerializer()
    marker = GeometryField()
    box_count = IntegerField()

    class Meta:
        model = Area
        fields = ("id", "name", "administration_unit", "marker", "box_count")


class PublicRegionSerializer(ModelSerializer):
    marker = GeometryField(precision=4)
    outline = SerializerMethodField()
    box_count = IntegerField()

    class Meta:
        model = Region
        fields = ("id", "name", "marker", "outline", "box_count")

    def get_outline(self, region):
        outline = region.area.simplify(OUTLINE_TOLERANCE, preserve_topology=True)
        return GeometryField(precision=4).to_representation(outline)


class StatisticsAreaSerializer(ModelSerializer):
    administration_unit = UnitSerializer()

    class Meta:
        model = Area
        fields = ("id", "name", "administration_unit")


class WantToHangSerializer(Serializer):
    name = CharField(max_length=127)
    email = EmailField()
    phone = CharField(max_length=63, required=False, allow_blank=True, default="")
    place = CharField(max_length=255)
    box_count = ChoiceField(
        choices=list(BOX_COUNTS), required=False, allow_null=True, default=None
    )
    box_source = ChoiceField(
        choices=list(BOX_SOURCES), required=False, allow_null=True, default=None
    )
    message = CharField(required=False, allow_blank=True, default="")


class SpacingWarningSerializer(Serializer):
    box_id = UUIDField(source="box.id")
    box_name = CharField(source="box.name")
    location = GeometryField(source="box.location")
    distance = FloatField()
    is_same_type = BooleanField()
    should_be_moved = BooleanField()


class DuplicateNameSerializer(ModelSerializer):
    class Meta:
        model = NestBox
        fields = ("id", "name", "location")


def warnings_data(area, location, box_type, name, exclude_id=None):
    """The questions to ask before placing a box: spacing and a name already painted."""
    spacing = spacing_warnings(area, location, box_type, exclude_id) if location else []
    duplicates = duplicate_names(area, name, exclude_id) if name else []
    return {
        "spacing": SpacingWarningSerializer(spacing, many=True).data,
        "duplicate_names": DuplicateNameSerializer(duplicates, many=True).data,
    }


def box_warnings_data(box):
    return warnings_data(box.area, box.location, box.type, box.name, box.pk)


class BoxChangesField(serializers.JSONField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if not isinstance(data, dict):
            raise serializers.ValidationError("Očekává se objekt.")
        try:
            parse_box_changes(data)
        except DjangoValidationError as error:
            raise serializers.ValidationError(as_serializer_error(error)["box_changes"])
        return data


BOX_FIELDS = (
    "id",
    "area_id",
    "name",
    "previous_names",
    "status",
    "location",
    "planned_radius",
    "region_id",
    "elevation",
    "type_id",
    "hole_shape",
    "hole_size",
    "opening",
    "material",
    "note",
    "installed_on",
    "ended_on",
    "end_reason_id",
    "is_verified",
    "is_new",
    "closest_distance",
    "closest_same_type_distance",
    "should_be_moved",
    "season_state",
    "last_checked_on",
    "old_id",
    "created_at",
    "created_by",
    "batch_id",
)


class BoxSerializer(ModelSerializer):
    id = UUIDField(required=False)
    area_id = related(Area, "area")
    type_id = optional_related(NestBoxType, "type")
    end_reason_id = PrimaryKeyRelatedField(source="end_reason", read_only=True)
    region_id = PrimaryKeyRelatedField(source="region", read_only=True)
    # Plans the new box into that batch
    batch_id = PrimaryKeyRelatedField(
        source="batch",
        queryset=Batch.objects.all(),
        write_only=True,
        required=False,
        allow_null=True,
    )
    created_by = PersonSerializer(read_only=True)
    is_verified = BooleanField(read_only=True)
    is_new = BooleanField(read_only=True)
    should_be_moved = BooleanField(read_only=True)
    season_state = CharField(read_only=True, allow_null=True)
    last_checked_on = DateField(read_only=True)

    class Meta:
        model = NestBox
        fields = BOX_FIELDS
        read_only_fields = (
            "ended_on",
            "closest_distance",
            "closest_same_type_distance",
            "old_id",
            "created_at",
        )

    def validate_status(self, status):
        if status == NestBox.Status.ENDED:
            raise serializers.ValidationError(
                "Budka se ukončuje vlastní akcí, ne změnou stavu."
            )
        return status

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            for name in ("id", "batch_id"):
                fields[name].read_only = True
        return fields


class BoxWarningsQuerySerializer(Serializer):
    area = related(Area, None)
    location = GeometryField(required=False)
    type = optional_related(NestBoxType, None)
    name = CharField(required=False, allow_blank=True)
    exclude = UUIDField(required=False)


class EndBoxSerializer(Serializer):
    end_reason_id = related(NestBoxEndReason, "end_reason")
    ended_on = DateField()


class HistorySerializer(ModelSerializer):
    user = PersonSerializer()

    class Meta:
        model = NestBoxHistory
        fields = ("id", "date", "user", "box_check_id", "changes")


class LinkBoxSerializer(ModelSerializer):
    """What a volunteer sees of a box."""

    type_id = PrimaryKeyRelatedField(source="type", read_only=True)
    is_verified = BooleanField(read_only=True)
    is_new = BooleanField(read_only=True)
    season_state = CharField(read_only=True)

    class Meta:
        model = NestBox
        fields = (
            "id",
            "name",
            "status",
            "season_state",
            "location",
            "planned_radius",
            "elevation",
            "type_id",
            "hole_shape",
            "hole_size",
            "opening",
            "material",
            "note",
            "installed_on",
            "is_verified",
            "is_new",
        )
        read_only_fields = fields


class NewBoxCheckSerializer(Serializer):
    id = UUIDField()
    date = DateField()
    made_at = DateTimeField()
    volunteer_nickname = CharField(max_length=63, allow_blank=True)
    volunteer_email = EmailField(allow_blank=True)


class LinkNewBoxSerializer(ModelSerializer):
    """A box a volunteer hung, with the ids of the box and of its check made on
    the phone, so that a resend from the outbox updates both."""

    id = UUIDField()
    type_id = related(NestBoxType, "type")
    check = NewBoxCheckSerializer()

    class Meta:
        model = NestBox
        fields = (
            "id",
            "name",
            "location",
            "type_id",
            "hole_shape",
            "hole_size",
            "opening",
            "material",
            "note",
            "installed_on",
            "check",
        )
        extra_kwargs = {"note": {"required": False}}


class CheckPhotoSerializer(ModelSerializer):
    class Meta:
        model = CheckPhoto
        fields = ("id", "order", "photo")


class CheckPhotoUploadSerializer(CheckPhotoSerializer):
    parent_id = related(Check, "box_check")

    class Meta(CheckPhotoSerializer.Meta):
        fields = (*CheckPhotoSerializer.Meta.fields, "parent_id")


CHECK_FIELDS = (
    "id",
    "box_id",
    "date",
    "season",
    "made_at",
    "batch_id",
    "volunteer_nickname",
    "is_confirmed",
    "found",
    "cleaning",
    "not_cleaned_reason_id",
    "contents",
    "occupant_ids",
    "eggs_left",
    "dead_birds",
    "breeding_note",
    "box_left",
    "box_changes",
    "note",
    "photos",
)


class BaseCheckSerializer(ModelSerializer):
    box_id = related(NestBox, "box")
    not_cleaned_reason_id = optional_related(
        NestBoxNotCleanedReason, "not_cleaned_reason"
    )
    occupant_ids = related(NestBoxOccupant, "occupants", many=True, required=False)
    contents = ListField(child=ChoiceField(choices=Check.Content.choices))
    box_changes = BoxChangesField(required=False)
    photos = CheckPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Check
        fields = CHECK_FIELDS
        read_only_fields = ("season", "is_confirmed")
        # (box, season) is checked by the domain functions: the season is derived
        validators = []

    def build(self):
        """The unsaved check and its occupants, for the domain functions to store."""
        data = dict(self.validated_data)
        occupants = data.pop("occupants", [])
        if self.instance is None:
            return Check(**data), occupants
        for name, value in data.items():
            setattr(self.instance, name, value)
        return self.instance, occupants


class CheckSerializer(BaseCheckSerializer):
    id = UUIDField(required=False)
    made_at = DateTimeField(required=False)
    batch_id = optional_related(Batch, "batch")
    cleaned_by_id = optional_related(AdministrationUnit, "cleaned_by")
    entered_by = PersonSerializer(read_only=True)
    confirmed_by = PersonSerializer(read_only=True)

    class Meta(BaseCheckSerializer.Meta):
        fields = (
            *CHECK_FIELDS,
            "volunteer_email",
            "cleaned_by_id",
            "entered_by",
            "confirmed_at",
            "confirmed_by",
            "is_historical",
        )
        read_only_fields = (
            *BaseCheckSerializer.Meta.read_only_fields,
            "confirmed_at",
            "is_historical",
        )

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            for name in ("id", "box_id", "batch_id"):
                fields[name].read_only = True
        return fields


class LinkCheckSerializer(BaseCheckSerializer):
    """A volunteer's check. The client makes the id and the time, for offline resends."""

    id = UUIDField()

    class Meta(BaseCheckSerializer.Meta):
        fields = (*CHECK_FIELDS, "volunteer_email")
        read_only_fields = (*BaseCheckSerializer.Meta.read_only_fields, "batch_id")
        extra_kwargs = {"volunteer_email": {"write_only": True}}


class BatchSerializer(ModelSerializer):
    area_id = related(Area, "area")
    cleaned_by_id = optional_related(AdministrationUnit, "cleaned_by")
    # Left out on create: the suggested boxes, see `suggested_batch_boxes`
    box_ids = related(NestBox, "boxes", many=True, required=False)
    area_name = CharField(source="area.name", read_only=True)
    created_by = PersonSerializer(read_only=True)
    confirmed_by = PersonSerializer(read_only=True)
    box_count = IntegerField(read_only=True)
    checked_count = IntegerField(read_only=True)
    pending_count = IntegerField(read_only=True)

    class Meta:
        model = Batch
        fields = (
            "id",
            "area_id",
            "area_name",
            "name",
            "token",
            "box_ids",
            "cleaned_by_id",
            "created_by",
            "created_at",
            "closed_at",
            "confirmed_at",
            "confirmed_by",
            "box_count",
            "checked_count",
            "pending_count",
        )
        read_only_fields = ("token", "created_at", "closed_at", "confirmed_at")

    def get_fields(self):
        fields = super().get_fields()
        if self.instance is not None:
            fields["area_id"].read_only = True
        return fields

    def validate(self, attrs):
        area = attrs.get("area") or self.instance.area
        if any(box.area_id != area.pk for box in attrs.get("boxes", [])):
            raise serializers.ValidationError(
                {"box_ids": "Některé budky nejsou v této oblasti."}
            )
        return attrs


class BoxIdsSerializer(Serializer):
    box_ids = ListField(child=UUIDField())


class LinkBatchSerializer(ModelSerializer):
    cleaned_by = UnitSerializer()

    class Meta:
        model = Batch
        fields = ("id", "name", "token", "cleaned_by", "created_at")


class LinkAreaSerializer(ModelSerializer):
    administration_unit = UnitSerializer()

    class Meta:
        model = Area
        fields = ("id", "name", "administration_unit")


class MapBoxSerializer(ModelSerializer):
    """What the map of all boxes draws, filters and lists; a box's page loads the rest."""

    is_verified = BooleanField()
    is_new = BooleanField()
    should_be_moved = BooleanField()
    season_state = CharField(allow_null=True)
    last_checked_on = DateField()

    class Meta:
        model = NestBox
        fields = (
            "id",
            "name",
            "previous_names",
            "area_id",
            "location",
            "planned_radius",
            "type_id",
            "status",
            "is_verified",
            "is_new",
            "should_be_moved",
            "season_state",
            "last_checked_on",
        )
        read_only_fields = fields


class AreaSerializer(ModelSerializer):
    administration_unit_id = related(AdministrationUnit, "administration_unit")
    administration_unit = UnitSerializer(read_only=True)
    marker = GeometryField(read_only=True)
    box_count = IntegerField(read_only=True)

    class Meta:
        model = Area
        fields = (
            "id",
            "name",
            "administration_unit_id",
            "administration_unit",
            "note",
            "marker",
            "box_count",
        )


class AreaDetailSerializer(AreaSerializer):
    boxes = BoxSerializer(many=True, read_only=True)

    class Meta(AreaSerializer.Meta):
        fields = (*AreaSerializer.Meta.fields, "boxes")


class GpxImportSerializer(Serializer):
    gpx = CharField()
    installed_on = DateField(required=False, allow_null=True, default=None)
    type_id = related(NestBoxType, "type", allow_null=True, default=None)
    apply = BooleanField(default=False)
    # Row indexes the manager unticked in the review
    skip = ListField(child=IntegerField(), required=False, default=list)


class ImportRowSerializer(Serializer):
    name = CharField()
    location = GeometryField()
    action = ChoiceField(
        choices=[
            ImportRow.Action.NEW,
            ImportRow.Action.MOVE,
            ImportRow.Action.UNCHANGED,
            ImportRow.Action.AMBIGUOUS,
        ]
    )
    box_id = UUIDField(source="box.id", allow_null=True, default=None)
    moved_by = FloatField(allow_null=True)
    warnings = SpacingWarningSerializer(many=True)
    close_rows = ListField(child=IntegerField())


class HelpHTMLField(ArticleHTMLField):
    """The help editor's markup: the cookbook articles' plus tables."""

    tags = ArticleHTMLField.tags | {"table", "tbody", "tr", "th", "td"}


class HelpArticleSerializer(KeepsContentImages, ModelSerializer):
    content = HelpHTMLField(allow_blank=True)

    class Meta:
        model = HelpArticle
        fields = ("slug", "title", "content")
        read_only_fields = ("slug",)


class HelpImageSerializer(ModelSerializer):
    article = SlugRelatedField(slug_field="slug", queryset=HelpArticle.objects.all())
    src = CharField(read_only=True)

    class Meta:
        model = HelpImage
        fields = ("id", "article", "image", "src")
        extra_kwargs = {"image": {"write_only": True}}
