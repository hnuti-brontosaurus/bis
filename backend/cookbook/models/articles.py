from common.thumbnails import ThumbnailImageField, get_thumbnail_path
from cookbook.models.base import BaseModel, ChangeMixin
from django.conf import settings
from django.db import models as m
from django.db.models import CASCADE
from tinymce.models import HTMLField
from translation.translate import translate_model


@translate_model
class Article(ChangeMixin, BaseModel):
    # One article per cookbook menu entry; the frontend routes and the menu
    # labels are keyed by these slugs.
    class Slug(m.TextChoices):
        MANIFEST = "manifest"
        HOW_TO = "how_to"
        RISKS = "risks"
        WHERE_TO_GO = "where_to_go"
        FAQ = "faq"
        BRONTO = "bronto"
        DUMPSTER_DIVING = "dumpster_diving"
        ZERO_WASTE = "zero_waste"
        JOIN_US = "join_us"

    slug = m.CharField(max_length=31, choices=Slug.choices, unique=True)
    content = HTMLField(blank=True)

    def __str__(self):
        return self.slug


@translate_model
class ArticleImage(BaseModel):
    article = m.ForeignKey(Article, related_name="images", on_delete=CASCADE)
    image = ThumbnailImageField(upload_to="articles")

    @property
    def src(self):
        return settings.MEDIA_URL + get_thumbnail_path(self.image.name, "large")
