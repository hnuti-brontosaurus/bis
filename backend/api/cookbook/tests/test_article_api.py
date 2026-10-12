import base64

import pytest
from cookbook.models.articles import Article, ArticleImage
from rest_framework.test import APIClient

from .conftest import _png_bytes
from .test_permissions import _client_for

URL = "/api/cookbook/articles/manifest/"


@pytest.fixture
def editor_client(chef_user, chef):
    chef.is_editor = True
    chef.save()
    return _client_for(chef_user)


@pytest.mark.django_db
def test_article_is_created_on_first_read():
    response = APIClient().get(URL)
    assert response.status_code == 200, response.data
    assert response.data == {"slug": "manifest", "content": ""}
    assert Article.objects.filter(slug="manifest").exists()


@pytest.mark.django_db
def test_unknown_article_is_404():
    assert APIClient().get("/api/cookbook/articles/nope/").status_code == 404
    assert not Article.objects.exists()


@pytest.mark.django_db
def test_editor_writes_headings(editor_client, chef_user):
    response = editor_client.patch(
        URL,
        {
            "content": "<h2>Proč</h2><h3> </h3><h4>x</h4><p>Protože.</p>"
            "<blockquote><p>Citát</p></blockquote><hr>"
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    article = Article.objects.get(slug="manifest")
    assert article.content == (
        "<h2>Proč</h2>x<p>Protože.</p><blockquote><p>Citát</p></blockquote><hr>"
    )
    assert article.updated_by == chef_user


@pytest.mark.django_db
def test_chef_cannot_write(api_client, chef):
    response = api_client.patch(URL, {"content": "<p>x</p>"}, format="json")
    assert response.status_code == 403


@pytest.mark.django_db
def test_anonymous_cannot_write():
    response = APIClient().patch(URL, {"content": "<p>x</p>"}, format="json")
    assert response.status_code in (401, 403)


@pytest.mark.django_db
def test_editor_cannot_delete(editor_client):
    assert editor_client.delete(URL).status_code == 405


def _upload(client):
    data = f"data:image/png;filename=a.png;base64,{base64.b64encode(_png_bytes()).decode()}"
    return client.post(
        "/api/cookbook/article_images/",
        {"article": "manifest", "image": data},
        format="json",
    )


@pytest.mark.django_db
def test_article_keeps_only_images_in_its_content(editor_client):
    editor_client.get(URL)
    kept = _upload(editor_client).data["src"]
    removed = _upload(editor_client).data["src"]
    assert removed.startswith("/media/thumbnails/articles/")

    response = editor_client.patch(
        URL,
        {"content": f'<img src="{kept}"><img src="https://elsewhere.com/x.png">'},
        format="json",
    )
    assert response.status_code == 200, response.data
    assert response.data["content"] == f'<img src="{kept}">'
    assert [image.src for image in ArticleImage.objects.all()] == [kept]


@pytest.mark.django_db
def test_chef_cannot_upload_article_image(api_client, chef):
    api_client.get(URL)
    assert _upload(api_client).status_code == 403
