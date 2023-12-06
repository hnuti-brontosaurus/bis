from os.path import basename
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db.models import *
from django.urls import reverse
from tinymce.models import HTMLField

from administration_units.models import AdministrationUnit
from bis.models import User
from event.models import Event
from game_book_categories.models import Tag, PhysicalCategory, MentalCategory, LocationCategory, \
    ParticipantNumberCategory, ParticipantAgeCategory, GameLengthCategory, PreparationLengthCategory, \
    OrganizersNumberCategory, MaterialRequirementCategory
from translation.translate import translate_model


class BaseModel(Model):
    class Meta:
        ordering = '-id',
        abstract = True

    def __str__(self):
        return getattr(self, 'name', super().__str__())

@translate_model
class Game(BaseModel):
    name = CharField(max_length=60)

    # internal
    is_hidden = BooleanField(default=False)
    game_id = UUIDField(default=uuid4, editable=False)  # revisions of same game have different id, same game_id
    created_at = DateTimeField(auto_now_add=True)

    # origin
    contributor = ForeignKey(User, on_delete=PROTECT, related_name='games')
    is_original = BooleanField(default=False)
    origin = TextField(blank=True)
    administration_unit = ForeignKey(AdministrationUnit, blank=True, null=True, on_delete=SET_NULL,
                                     related_name='games')
    # rating
    thumbs_up = ManyToManyField(User, related_name='thumbed_up_games', blank=True)
    favourites = ManyToManyField(User, related_name='favourite_games', blank=True)
    watchers = ManyToManyField(User, related_name='watched_games', blank=True)
    stars = PositiveSmallIntegerField(choices=[(i, '★' * i) for i in range(1, 6)], blank=True, null=True)
    is_verified = BooleanField(default=False)
    is_draft = BooleanField(default=True)

    # categories
    tags = ManyToManyField(Tag, related_name='games', blank=True)
    physical_category = ForeignKey(PhysicalCategory, on_delete=PROTECT, related_name='games')
    physical_note = TextField(blank=True)
    mental_category = ForeignKey(MentalCategory, on_delete=PROTECT, related_name='games')
    mental_note = TextField(blank=True)
    location_category = ManyToManyField(LocationCategory, related_name='games')
    location_note = TextField(blank=True)
    participant_number_category = ManyToManyField(ParticipantNumberCategory, related_name='games')
    participant_number_note = TextField(blank=True)
    participant_age_category = ManyToManyField(ParticipantAgeCategory, related_name='games')
    participant_age_note = TextField(blank=True)
    game_length_category = ForeignKey(GameLengthCategory, on_delete=PROTECT, related_name='games')
    game_length_note = TextField(blank=True)
    preparation_length_category = ForeignKey(PreparationLengthCategory, on_delete=PROTECT, related_name='games')
    preparation_length_note = TextField(blank=True)
    material_requirement_category = ForeignKey(MaterialRequirementCategory, on_delete=PROTECT, related_name='games')
    material_requirement_note = TextField(blank=True)
    organizers_number_category = ForeignKey(OrganizersNumberCategory, on_delete=PROTECT, related_name='games')
    organizers_number_note = TextField(blank=True)

    # description
    goal = HTMLField(blank=True)
    short_description = CharField(max_length=250)
    motivation = HTMLField(blank=True)
    description = HTMLField()
    material = HTMLField(blank=True)
    notes = HTMLField(blank=True)

    def clean(self):
        if not self.is_original and not self.origin:
            raise ValidationError("Původ hry musí být vyplněn, pokud nejsi autorem")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.clean()
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse('game', kwargs={'pk' : self.pk})

@translate_model
class BaseFile(BaseModel):
    file = FileField(upload_to='game_files')

    def __str__(self):
        return self.file.name

    def filename(self):
        return basename(self.file.name)

    class Meta:
        ordering = 'id',
        abstract = True

@translate_model
class GameFile(BaseFile):
    game = ForeignKey(Game, on_delete=CASCADE, related_name='files')

@translate_model
class Comment(BaseModel):
    game = ForeignKey(Game, on_delete=CASCADE, related_name='comments')
    author = ForeignKey(User, on_delete=PROTECT, related_name='game_comments')
    is_hidden = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    comment = TextField()

    def __str__(self):
        return f"Komentář"

    def get_absolute_url(self):
        return reverse('game', kwargs={'pk' : self.game.pk})

@translate_model
class CommentFile(BaseFile):
    comment = ForeignKey(Comment, on_delete=CASCADE, related_name='files')

@translate_model
class PlayedAt(BaseModel):
    game = ForeignKey(Game, on_delete=CASCADE, related_name='played_at')
    event = ForeignKey(Event, on_delete=CASCADE, related_name='played_games')
    comment = TextField()

    def __str__(self):
        return f"Uvedení na akci"

@translate_model
class PlayedAtFile(BaseFile):
    played_at = ForeignKey(PlayedAt, on_delete=CASCADE, related_name='files')

@translate_model
class GameList(BaseModel):
    name = CharField(max_length=60)
    owner = ForeignKey(User, on_delete=CASCADE, related_name='game_lists')
    games = ManyToManyField(Game, related_name='game_lists', blank=True)
