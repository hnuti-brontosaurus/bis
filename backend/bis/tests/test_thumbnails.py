import os
from os.path import join

import pytest
from bis.models import User
from common.thumbnails import get_thumbnail_path
from django.conf import settings


def thumbnail_path(file, size_name):
    return join(settings.MEDIA_ROOT, get_thumbnail_path(file.name, size_name))


@pytest.mark.django_db
def test_loading_with_thumbnail_field_deferred():
    user = User.objects.create(email="deferred@example.com", _str="Deferred")

    loaded = User.objects.only("id").get(id=user.id)

    assert loaded.old_photo is None
    assert "photo" in loaded.get_deferred_fields()


@pytest.fixture
def user_with_photo(settings, tmp_path):
    from io import BytesIO

    from django.core.files.uploadedfile import SimpleUploadedFile
    from PIL import Image

    settings.MEDIA_ROOT = str(tmp_path)
    buffer = BytesIO()
    Image.new("RGB", (800, 600), "red").save(buffer, format="PNG")
    user = User.objects.create(email="photo@example.com", _str="Photo")
    user.photo = SimpleUploadedFile("face.png", buffer.getvalue())
    user.save()
    return user


@pytest.mark.django_db
def test_saving_without_changing_the_photo_leaves_thumbnails_alone(user_with_photo):
    os.remove(user_with_photo.photo.path)

    User.objects.get(id=user_with_photo.id).save()

    assert os.path.exists(thumbnail_path(user_with_photo.photo, "small"))


@pytest.mark.django_db
def test_replacing_the_photo_replaces_its_thumbnails(user_with_photo):
    from django.core.files.uploadedfile import SimpleUploadedFile

    old_thumbnail = thumbnail_path(user_with_photo.photo, "small")
    user = User.objects.get(id=user_with_photo.id)
    with open(user.photo.path, "rb") as original:
        user.photo = SimpleUploadedFile("other.png", original.read())
    user.save()

    assert not os.path.exists(old_thumbnail)
    assert os.path.exists(thumbnail_path(user.photo, "small"))
