from datetime import date
from uuid import uuid4

from administration_units.models import AdministrationUnit
from bis.models import User
from categories.models import (
    NestBoxEndReason,
    NestBoxNotCleanedReason,
    NestBoxOccupant,
    NestBoxType,
)
from common.thumbnails import ThumbnailImageField, get_thumbnail_path
from django.conf import settings
from django.contrib.gis.db import models as m
from django.contrib.gis.db.models.aggregates import Collect
from django.contrib.gis.db.models.functions import Centroid
from django.contrib.postgres.fields import ArrayField
from django.db import connection
from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    Case,
    Count,
    F,
    FilteredRelation,
    OuterRef,
    Q,
    Value,
    When,
)
from django.utils.timezone import localdate
from regions.models import Region
from tinymce.models import HTMLField
from translation.translate import translate_model


def in_use(prefix=""):
    """Hanging: the only boxes spacing and statistics see."""
    return Q(**{f"{prefix}status": NestBox.Status.IN_USE})


# A verified box this close to another should be moved
EXISTING_ANY_TYPE_LIMIT = 5
EXISTING_SAME_TYPE_LIMIT = 15
# Placing or moving a box this close to another asks first
PLACING_ANY_TYPE_LIMIT = 15
PLACING_SAME_TYPE_LIMIT = 50


class AreaQuerySet(m.QuerySet):
    def with_markers(self):
        """The marker is the centroid of the area's boxes in use; null without any."""
        return self.annotate(
            marker=Centroid(Collect("boxes__location", filter=in_use("boxes__"))),
            box_count=Count("boxes", filter=in_use("boxes__")),
        )


@translate_model
class Area(m.Model):
    name = m.CharField(max_length=127, unique=True)
    administration_unit = m.ForeignKey(
        AdministrationUnit, related_name="nest_box_areas", on_delete=PROTECT
    )
    note = m.TextField(blank=True)

    objects = AreaQuerySet.as_manager()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class SeasonState(m.TextChoices):
    PLANNED = "planned", "plánovaná"
    TO_CHECK = "to_check", "ke kontrole"
    ATTENTION = "attention", "pozornost"
    DONE = "done", "hotovo"


class NestBoxQuerySet(m.QuerySet):
    def in_use(self):
        return self.filter(in_use())

    def with_is_verified(self):
        """Verified means checked in the field since the import: a confirmed check
        that is not historical. Until then its imported data is not trusted."""
        return self.annotate(
            is_verified=m.Exists(
                Check.objects.filter(
                    box=OuterRef("pk"), is_confirmed=True, is_historical=False
                )
            )
        )

    def with_should_be_moved(self):
        """Waits until verified: imported positions are too often copied."""
        return self.with_is_verified().annotate(
            should_be_moved=m.ExpressionWrapper(
                in_use()
                & Q(is_verified=True)
                & (
                    Q(closest_distance__lt=EXISTING_ANY_TYPE_LIMIT)
                    | Q(closest_same_type_distance__lt=EXISTING_SAME_TYPE_LIMIT)
                ),
                output_field=m.BooleanField(),
            )
        )

    def with_season_state(self):
        """`season_state`, one of SeasonState, or null for an ended box.

        A pending check counts as if it were confirmed: its status and condition
        are what confirming it would leave on the box, see `checks._box_values`.
        """
        Status, Found, BoxLeft = NestBox.Status, Check.Found, Check.BoxLeft
        repairs = (NestBox.Condition.NEEDS_REPAIR, NestBox.Condition.NEEDS_REPLACING)
        pending = Q(season_check__is_confirmed=False)
        returnable = pending & Q(status__in=RETURNABLE_STATUSES)
        found = Q(season_check__found=Found.FOUND)
        return (
            self.with_should_be_moved()
            .annotate(
                season_check=FilteredRelation(
                    "checks", condition=Q(checks__season=Check.current_season())
                ),
                season_status=Case(
                    When(
                        returnable & Q(season_check__found=Found.NOT_FOUND),
                        then=Value(Status.MISSING),
                    ),
                    When(
                        returnable
                        & found
                        & Q(season_check__box_left=BoxLeft.TAKEN_DOWN),
                        then=Value(Status.TAKEN_DOWN),
                    ),
                    When(returnable & found, then=Value(Status.IN_USE)),
                    When(
                        pending
                        & Q(
                            status=Status.PLANNED, season_check__box_changes__hung=True
                        ),
                        then=Value(Status.IN_USE),
                    ),
                    default=F("status"),
                ),
                season_condition=Case(
                    When(
                        returnable
                        & found
                        & Q(season_check__box_left__in=(BoxLeft.FINE, *repairs)),
                        then=F("season_check__box_left"),
                    ),
                    default=F("condition"),
                ),
            )
            .annotate(
                season_state=Case(
                    When(status=Status.ENDED, then=None),
                    When(season_status=Status.PLANNED, then=Value(SeasonState.PLANNED)),
                    When(
                        Q(season_status__in=(Status.MISSING, Status.TAKEN_DOWN))
                        | Q(season_condition__in=repairs)
                        | Q(
                            season_check__cleaning__in=(
                                Check.Cleaning.NOT_CLEANED,
                                Check.Cleaning.COULD_NOT_OPEN,
                            )
                        )
                        | Q(should_be_moved=True),
                        then=Value(SeasonState.ATTENTION),
                    ),
                    When(found, then=Value(SeasonState.DONE)),
                    When(type__needs_cleaning=False, then=Value(SeasonState.DONE)),
                    default=Value(SeasonState.TO_CHECK),
                    output_field=m.CharField(),
                )
            )
        )


@translate_model
class NestBox(m.Model):
    class Status(m.TextChoices):
        PLANNED = "planned", "plánovaná"
        IN_USE = "in_use", "vyvěšená"
        TAKEN_DOWN = "taken_down", "sundaná na opravu"
        MISSING = "missing", "nenalezená"
        ENDED = "ended", "zaniklá"

    class Condition(m.TextChoices):
        FINE = "fine", "v pořádku"
        NEEDS_REPAIR = "needs_repair", "potřebuje opravu"
        NEEDS_REPLACING = "needs_replacing", "potřebuje vyměnit"

    class Opening(m.TextChoices):
        FRONT = "front", "přední stěnou"
        ROOF = "roof", "střechou"
        SIDE = "side", "boční stěnou"
        NONE = "none", "neotevírá se"

    class Material(m.TextChoices):
        WOOD = "wood", "dřevo"
        WOOD_CEMENT = "wood_cement", "dřevocement"
        PLASTIC = "plastic", "plast"
        OTHER = "other", "jiný"

    id = m.UUIDField(primary_key=True, default=uuid4)
    area = m.ForeignKey(Area, related_name="boxes", on_delete=PROTECT)
    name = m.CharField(max_length=63)
    previous_names = m.TextField(blank=True)
    status = m.CharField(max_length=15, choices=Status.choices)
    condition = m.CharField(
        max_length=15, choices=Condition.choices, default=Condition.FINE
    )

    location = m.PointField()
    planned_radius = m.PositiveIntegerField(null=True, blank=True)
    region = m.ForeignKey(
        Region,
        related_name="nest_boxes",
        on_delete=PROTECT,
        null=True,
        blank=True,
        editable=False,
    )
    elevation = m.IntegerField(null=True, blank=True)

    type = m.ForeignKey(
        NestBoxType,
        related_name="nest_boxes",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    hole_shape = m.CharField(
        max_length=15, choices=NestBoxType.HoleShape.choices, blank=True
    )
    hole_size = m.PositiveSmallIntegerField(null=True, blank=True)
    opening = m.CharField(max_length=15, choices=Opening.choices, blank=True)
    material = m.CharField(max_length=15, choices=Material.choices, blank=True)
    # The one note of a box, shown to volunteers on the batch link too
    note = m.TextField(blank=True)

    installed_on = m.DateField(null=True, blank=True)
    ended_on = m.DateField(null=True, blank=True)
    end_reason = m.ForeignKey(
        NestBoxEndReason,
        related_name="nest_boxes",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    closest_distance = m.FloatField(null=True, blank=True, editable=False)
    closest_same_type_distance = m.FloatField(null=True, blank=True, editable=False)

    old_id = m.IntegerField(null=True, blank=True, unique=True)
    created_at = m.DateTimeField(auto_now_add=True)
    created_by = m.ForeignKey(
        User,
        related_name="created_nest_boxes",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    objects = NestBoxQuerySet.as_manager()

    class Meta:
        ordering = ("area", "name")

    def __str__(self):
        return f"{self.area} {self.name}"

    @property
    def is_new(self):
        """A volunteer hung it through a batch link and no check confirmed it yet:
        planned, by nobody signed in. Its check is what hangs it."""
        return self.status == NestBox.Status.PLANNED and self.created_by_id is None

    def save(self, *args, **kwargs):
        self.region = Region.objects.filter(area__contains=self.location).first()
        previous_area_id = (
            None
            if self._state.adding
            else NestBox.objects.filter(pk=self.pk)
            .values_list("area_id", flat=True)
            .first()
        )
        super().save(*args, **kwargs)
        NestBox.recompute_distances(self.area_id)
        if previous_area_id not in (None, self.area_id):
            NestBox.recompute_distances(previous_area_id)

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        NestBox.recompute_distances(self.area_id)
        return result

    @classmethod
    def recompute_distances(cls, area_id):
        table = cls._meta.db_table
        with connection.cursor() as cursor:
            cursor.execute(
                f"""
                UPDATE {table} AS box
                SET closest_distance = nearest.any_type,
                    closest_same_type_distance = nearest.same_type
                FROM (
                    SELECT box.id,
                        MIN(ST_Distance(box.location::geography,
                                        other.location::geography)) AS any_type,
                        MIN(ST_Distance(box.location::geography,
                                        other.location::geography))
                            FILTER (WHERE other.type_id = box.type_id) AS same_type
                    FROM {table} AS box
                    LEFT JOIN {table} AS other
                        ON other.area_id = box.area_id
                        AND other.id <> box.id
                        AND other.status = %(in_use)s
                        AND box.status = %(in_use)s
                    WHERE box.area_id = %(area_id)s
                    GROUP BY box.id
                ) AS nearest
                WHERE box.id = nearest.id
                """,
                {"area_id": area_id, "in_use": cls.Status.IN_USE},
            )


# A check can move a box between these, see `checks._box_values`
RETURNABLE_STATUSES = (
    NestBox.Status.IN_USE,
    NestBox.Status.MISSING,
    NestBox.Status.TAKEN_DOWN,
)


@translate_model
class Batch(m.Model):
    area = m.ForeignKey(Area, related_name="batches", on_delete=CASCADE)
    name = m.CharField(max_length=127)
    token = m.UUIDField(default=uuid4, unique=True, editable=False)
    boxes = m.ManyToManyField(NestBox, related_name="batches", blank=True)
    cleaned_by = m.ForeignKey(
        AdministrationUnit, related_name="nest_box_batches", on_delete=PROTECT
    )
    created_by = m.ForeignKey(
        User,
        related_name="created_nest_box_batches",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    created_at = m.DateTimeField(auto_now_add=True)
    closed_at = m.DateTimeField(null=True, blank=True)
    confirmed_at = m.DateTimeField(null=True, blank=True)
    confirmed_by = m.ForeignKey(
        User,
        related_name="confirmed_nest_box_batches",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.area} {self.name}"

    def save(self, *args, **kwargs):
        if self.cleaned_by_id is None:
            self.cleaned_by_id = self.area.administration_unit_id
        super().save(*args, **kwargs)


@translate_model
class Check(m.Model):
    class Found(m.TextChoices):
        FOUND = "found", "nalezena"
        NOT_FOUND = "not_found", "nenalezena"
        NOT_REACHED = "not_reached", "nedostali jsme se k ní"

    class Cleaning(m.TextChoices):
        CLEANED = "cleaned", "vyčištěna"
        NOT_CLEANED = "not_cleaned", "nevyčištěna"
        COULD_NOT_OPEN = "could_not_open", "nešla otevřít"

    class Content(m.TextChoices):
        NOTHING = "nothing", "nic"
        BIRD_NEST = "bird_nest", "ptačí hnízdo"
        OTHER_ANIMAL = "other_animal", "jiné zvíře"
        UNKNOWN = "unknown", "nevím"

    class BoxLeft(m.TextChoices):
        FINE = "fine", "v pořádku"
        NEEDS_REPAIR = "needs_repair", "potřebuje opravu"
        NEEDS_REPLACING = "needs_replacing", "potřebuje vyměnit"
        TAKEN_DOWN = "taken_down", "sundaná na opravu"

    id = m.UUIDField(primary_key=True, default=uuid4)
    box = m.ForeignKey(NestBox, related_name="checks", on_delete=CASCADE)
    date = m.DateField()
    season = m.PositiveSmallIntegerField(editable=False)
    made_at = m.DateTimeField()
    batch = m.ForeignKey(
        Batch, related_name="checks", on_delete=SET_NULL, null=True, blank=True
    )

    entered_by = m.ForeignKey(
        User,
        related_name="entered_nest_box_checks",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    volunteer_nickname = m.CharField(max_length=63, blank=True)
    volunteer_email = m.EmailField(blank=True)

    is_confirmed = m.BooleanField(default=False)
    confirmed_at = m.DateTimeField(null=True, blank=True)
    confirmed_by = m.ForeignKey(
        User,
        related_name="confirmed_nest_box_checks",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    cleaned_by = m.ForeignKey(
        AdministrationUnit, related_name="nest_box_checks", on_delete=PROTECT
    )

    found = m.CharField(max_length=15, choices=Found.choices)
    cleaning = m.CharField(max_length=15, choices=Cleaning.choices, blank=True)
    not_cleaned_reason = m.ForeignKey(
        NestBoxNotCleanedReason,
        related_name="checks",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )
    contents = ArrayField(
        m.CharField(max_length=15, choices=Content.choices), blank=True
    )
    occupants = m.ManyToManyField(NestBoxOccupant, related_name="checks", blank=True)
    eggs_left = m.BooleanField(null=True, blank=True)
    dead_birds = m.BooleanField(null=True, blank=True)
    breeding_note = m.TextField(blank=True)
    box_left = m.CharField(max_length=15, choices=BoxLeft.choices, blank=True)
    box_changes = m.JSONField(default=dict, blank=True)
    note = m.TextField(blank=True)
    is_historical = m.BooleanField(default=False)

    class Meta:
        ordering = ("-date",)
        constraints = [
            m.UniqueConstraint(
                fields=["box", "season"], name="one_nest_box_check_per_season"
            )
        ]

    def __str__(self):
        return f"{self.box} {self.date}"

    @staticmethod
    def season_of(day):
        """A season runs July to June and is named after the year it starts in."""
        return day.year if day.month >= 7 else day.year - 1

    @staticmethod
    def current_season():
        return Check.season_of(localdate())

    @staticmethod
    def season_start(season):
        return date(season, 7, 1)

    @staticmethod
    def season_end(season):
        return date(season + 1, 6, 30)

    def save(self, *args, **kwargs):
        self.season = self.season_of(self.date)
        if self.cleaned_by_id is None:
            self.cleaned_by_id = (
                self.batch.cleaned_by_id
                if self.batch
                else self.box.area.administration_unit_id
            )
        super().save(*args, **kwargs)


@translate_model
class CheckPhoto(m.Model):
    box_check = m.ForeignKey(Check, related_name="photos", on_delete=CASCADE)
    photo = ThumbnailImageField(upload_to="nest_box_checks")
    order = m.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")


@translate_model
class NestBoxHistory(m.Model):
    box = m.ForeignKey(NestBox, related_name="history", on_delete=CASCADE)
    date = m.DateField()
    user = m.ForeignKey(
        User,
        related_name="nest_box_changes",
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    box_check = m.ForeignKey(
        Check, related_name="box_history", on_delete=SET_NULL, null=True, blank=True
    )
    changes = m.JSONField()

    class Meta:
        ordering = ("-date", "-id")


@translate_model
class HelpArticle(m.Model):
    class Slug(m.TextChoices):
        FOUND = "found"
        CLEANING = "cleaning"
        CONTENTS = "contents"
        OCCUPANTS = "occupants"
        BOX_LEFT = "box_left"
        BOX_CHANGES = "box_changes"
        HOLE = "hole"
        TYPE = "type"
        OPENING = "opening"
        HANGING = "hanging"
        CLEANING_HOWTO = "cleaning_howto"
        ABOUT = "about"

    slug = m.CharField(max_length=31, choices=Slug.choices, unique=True)
    title = m.CharField(max_length=127, blank=True)
    content = HTMLField(blank=True)

    class Meta:
        ordering = ("slug",)

    def __str__(self):
        return self.slug


@translate_model
class HelpImage(m.Model):
    article = m.ForeignKey(HelpArticle, related_name="images", on_delete=CASCADE)
    image = ThumbnailImageField(upload_to="nest_box_help")

    @property
    def src(self):
        return settings.MEDIA_URL + get_thumbnail_path(self.image.name, "large")
