"""The first version of every help article, shipped with the code so that each
environment gets it. `<slug>.html` is an article's content in the form the API
stores it (`HelpHTMLField`), except that an image is `src="images/<file>"`."""

import re
from pathlib import Path

from common.thumbnails import get_thumbnail_path
from django.conf import settings
from django.core.files import File

DIRECTORY = Path(__file__).parent
IMAGE = re.compile(r'(<img src=")images/([^"]+)(")')


def image_src(image):
    return settings.MEDIA_URL + get_thumbnail_path(image.name, "large")


def articles():
    """{slug: content as shipped}"""
    return {path.stem: path.read_text().strip() for path in DIRECTORY.glob("*.html")}


def load_help(article_model, image_model):
    """Fills the articles whose content is still empty, so an edited article is
    never overwritten. Takes the models, because a migration passes its own."""
    for slug, content in articles().items():
        article, _ = article_model.objects.get_or_create(slug=slug)
        if not article.content:
            fill(article, content, image_model)


def fill(article, content, image_model):
    def upload(match):
        image = image_model(article=article)
        with open(DIRECTORY / "images" / match[2], "rb") as file:
            image.image.save(match[2], File(file), save=False)
        image.save()
        return match[1] + image_src(image.image) + match[3]

    article.content = IMAGE.sub(upload, content)
    article.save()
