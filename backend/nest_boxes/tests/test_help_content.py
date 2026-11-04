import pytest
from api.nest_boxes.serializers import HelpArticleSerializer, HelpHTMLField
from nest_boxes.help_content import DIRECTORY, IMAGE, articles, load_help
from nest_boxes.models import HelpArticle, HelpImage


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


def test_every_article_is_shipped():
    assert set(articles()) == set(HelpArticle.Slug.values)


@pytest.mark.parametrize("slug", HelpArticle.Slug.values)
def test_shipped_content_is_what_the_editor_saves(slug):
    content = articles()[slug]
    assert HelpHTMLField().to_internal_value(content) == content


def test_every_shipped_image_is_used_and_exists():
    used = {
        match[2] for content in articles().values() for match in IMAGE.finditer(content)
    }
    assert used == {path.name for path in (DIRECTORY / "images").iterdir()}


@pytest.mark.parametrize("slug", HelpArticle.Slug.values)
def test_links_between_articles_lead_to_articles(slug):
    remaining = articles()[slug]
    for target in HelpArticle.Slug.values:
        remaining = remaining.replace(f'href="/budky/napoveda/{target}/"', "")
    assert "/budky/napoveda/" not in remaining


def test_load_fills_only_empty_articles(db, media, settings):
    HelpArticle.objects.create(slug=HelpArticle.Slug.ABOUT, content="<p>Vlastní</p>")

    load_help(HelpArticle, HelpImage)
    load_help(HelpArticle, HelpImage)

    assert HelpArticle.objects.get(slug="about").content == "<p>Vlastní</p>"
    assert HelpArticle.objects.count() == len(HelpArticle.Slug)
    article = HelpArticle.objects.get(slug="type")
    image = article.images.get()
    assert f'<img src="{image.src}"' in article.content
    assert (media / image.image.name).is_file()
    assert (media / image.src.removeprefix(settings.MEDIA_URL)).exists()


def test_loaded_article_saves_unchanged(db, media):
    load_help(HelpArticle, HelpImage)
    article = HelpArticle.objects.get(slug="hanging")
    images = set(article.images.all())

    serializer = HelpArticleSerializer(
        article, data={"content": article.content}, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()

    saved = HelpArticle.objects.get(slug="hanging")
    assert saved.content == article.content
    assert set(saved.images.all()) == images and len(images) == 2
