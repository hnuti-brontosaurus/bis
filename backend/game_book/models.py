from os.path import basename
from uuid import uuid4

from administration_units.models import AdministrationUnit
from bis.models import User
from django.core.exceptions import ValidationError
from django.db import models as m
from django.db.models import CASCADE, PROTECT, SET_NULL
from django.urls import reverse
from event.models import Event
from game_book_categories.models import (
    GameLengthCategory,
    LocationCategory,
    MaterialRequirementCategory,
    MentalCategory,
    OrganizersNumberCategory,
    ParticipantAgeCategory,
    ParticipantNumberCategory,
    PhysicalCategory,
    PreparationLengthCategory,
    Tag,
)
from tinymce.models import HTMLField
from translation.translate import translate_model


class BaseModel(m.Model):
    class Meta:
        ordering = ("-id",)
        abstract = True

    def __str__(self):
        return getattr(self, "name", super().__str__())


@translate_model
class Game(BaseModel):
    name = m.CharField(max_length=60)

    # internal
    is_hidden = m.BooleanField(default=False)
    game_id = m.UUIDField(
        default=uuid4, editable=False
    )  # revisions of same game have different id, same game_id
    created_at = m.DateTimeField(auto_now_add=True)

    # origin
    contributor = m.ForeignKey(User, on_delete=PROTECT, related_name="games")
    is_original = m.BooleanField(default=False)
    origin = m.TextField(blank=True)
    administration_unit = m.ForeignKey(
        AdministrationUnit,
        blank=True,
        null=True,
        on_delete=SET_NULL,
        related_name="games",
    )
    # rating
    thumbs_up = m.ManyToManyField(User, related_name="thumbed_up_games", blank=True)
    favourites = m.ManyToManyField(User, related_name="favourite_games", blank=True)
    watchers = m.ManyToManyField(User, related_name="watched_games", blank=True)
    stars = m.PositiveSmallIntegerField(
        choices=[(i, "★" * i) for i in range(1, 6)], blank=True, null=True
    )
    is_verified = m.BooleanField(default=False)
    is_draft = m.BooleanField(default=True)

    # categories
    tags = m.ManyToManyField(Tag, related_name="games", blank=True)
    physical_category = m.ForeignKey(
        PhysicalCategory, on_delete=PROTECT, related_name="games"
    )
    physical_note = m.TextField(blank=True)
    mental_category = m.ForeignKey(
        MentalCategory, on_delete=PROTECT, related_name="games"
    )
    mental_note = m.TextField(blank=True)
    location_category = m.ManyToManyField(LocationCategory, related_name="games")
    location_note = m.TextField(blank=True)
    participant_number_category = m.ManyToManyField(
        ParticipantNumberCategory, related_name="games"
    )
    participant_number_note = m.TextField(blank=True)
    participant_age_category = m.ManyToManyField(
        ParticipantAgeCategory, related_name="games"
    )
    participant_age_note = m.TextField(blank=True)
    game_length_category = m.ForeignKey(
        GameLengthCategory, on_delete=PROTECT, related_name="games"
    )
    game_length_note = m.TextField(blank=True)
    preparation_length_category = m.ForeignKey(
        PreparationLengthCategory, on_delete=PROTECT, related_name="games"
    )
    preparation_length_note = m.TextField(blank=True)
    material_requirement_category = m.ForeignKey(
        MaterialRequirementCategory, on_delete=PROTECT, related_name="games"
    )
    material_requirement_note = m.TextField(blank=True)
    organizers_number_category = m.ForeignKey(
        OrganizersNumberCategory, on_delete=PROTECT, related_name="games"
    )
    organizers_number_note = m.TextField(blank=True)

    # description
    goal = HTMLField(blank=True)
    short_description = m.CharField(max_length=250)
    motivation = HTMLField(blank=True)
    description = HTMLField()
    material = HTMLField(blank=True)
    notes = HTMLField(blank=True)

    def clean(self):
        if not self.is_original and not self.origin:
            raise ValidationError("Původ hry musí být vyplněn, pokud nejsi autorem")

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.clean()
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse("game", kwargs={"pk": self.pk})


@translate_model
class BaseFile(BaseModel):
    file = m.FileField(upload_to="game_files")

    def __str__(self):
        return self.file.name

    def filename(self):
        return basename(self.file.name)

    class Meta:
        ordering = ("id",)
        abstract = True


@translate_model
class GameFile(BaseFile):
    game = m.ForeignKey(Game, on_delete=CASCADE, related_name="files")


@translate_model
class Comment(BaseModel):
    game = m.ForeignKey(Game, on_delete=CASCADE, related_name="comments")
    author = m.ForeignKey(User, on_delete=PROTECT, related_name="game_comments")
    is_hidden = m.BooleanField(default=False)
    created_at = m.DateTimeField(auto_now_add=True)
    comment = m.TextField()

    def __str__(self):
        return "Komentář"

    def get_absolute_url(self):
        return reverse("game", kwargs={"pk": self.game.pk})


@translate_model
class CommentFile(BaseFile):
    comment = m.ForeignKey(Comment, on_delete=CASCADE, related_name="files")


@translate_model
class PlayedAt(BaseModel):
    game = m.ForeignKey(Game, on_delete=CASCADE, related_name="played_at")
    event = m.ForeignKey(Event, on_delete=CASCADE, related_name="played_games")
    comment = m.TextField()

    def __str__(self):
        return "Uvedení na akci"


@translate_model
class PlayedAtFile(BaseFile):
    played_at = m.ForeignKey(PlayedAt, on_delete=CASCADE, related_name="files")


@translate_model
class GameList(BaseModel):
    name = m.CharField(max_length=60)
    owner = m.ForeignKey(User, on_delete=CASCADE, related_name="game_lists")
    games = m.ManyToManyField(Game, related_name="game_lists", blank=True)
