import os
from io import BytesIO
from os.path import join

import pytest
from bis.models import User
from common.thumbnails import ThumbnailImageField, get_thumbnail_path
from django.apps import apps
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import signals
from PIL import Image


def thumbnail_paths(name):
    return [
        join(settings.MEDIA_ROOT, get_thumbnail_path(name, size_name))
        for size_name in settings.THUMBNAIL_SIZES
    ]


def has_thumbnails(name):
    return all(os.path.exists(path) for path in thumbnail_paths(name))


def has_no_thumbnails(name):
    return not any(os.path.lexists(path) for path in thumbnail_paths(name))


def png_upload(name, size=(2400, 1800)):
    buffer = BytesIO()
    Image.new("RGB", size, "red").save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue())


@pytest.fixture(autouse=True)
def media_root(settings, tmp_path):
    settings.MEDIA_ROOT = str(tmp_path)


user_count = iter(range(1000))


def create_user(**kwargs):
    i = next(user_count)
    return User.objects.create(email=f"user{i}@example.com", _str=f"User {i}", **kwargs)


@pytest.fixture
def user_with_photo():
    user = create_user()
    user.photo = png_upload("face.png")
    user.save()
    return user


@pytest.mark.parametrize(
    "model, field",
    [
        (model, field)
        for model in apps.get_models()
        for field in model._meta.get_fields()
        if isinstance(field, ThumbnailImageField)
    ],
    ids=lambda value: getattr(value, "__name__", getattr(value, "name", "")),
)
def test_every_thumbnail_field_is_wired(model, field):
    assert field.update_thumbnails in signals.post_save._live_receivers(model)[0]
    assert field.remove_thumbnails in signals.post_delete._live_receivers(model)[0]
    assert model().__dict__[f"old_{field.name}"] == ""


@pytest.mark.django_db
def test_creating_with_a_photo_makes_thumbnails():
    user = create_user(photo=png_upload("face.png"))

    assert has_thumbnails(user.photo.name)


@pytest.mark.django_db
def test_thumbnails_are_downscaled_and_small_originals_are_linked():
    user = create_user(photo=png_upload("face.png"))
    small, medium, large = thumbnail_paths(user.photo.name)

    assert max(Image.open(small).size) == settings.THUMBNAIL_SIZES["small"]
    assert max(Image.open(medium).size) == settings.THUMBNAIL_SIZES["medium"]
    assert max(Image.open(large).size) == settings.THUMBNAIL_SIZES["large"]

    tiny = create_user(photo=png_upload("tiny.png", size=(8, 8)))
    assert all(os.path.islink(path) for path in thumbnail_paths(tiny.photo.name))


@pytest.mark.django_db
def test_assigning_a_photo_to_a_saved_row_makes_thumbnails(user_with_photo):
    assert has_thumbnails(user_with_photo.photo.name)


@pytest.mark.django_db
def test_field_file_save_makes_thumbnails():
    user = User.objects.get(id=create_user().id)

    user.photo.save("face.png", png_upload("face.png"))

    assert has_thumbnails(user.photo.name)


@pytest.mark.django_db
def test_replacing_the_photo_replaces_its_thumbnails(user_with_photo):
    old_name = user_with_photo.photo.name
    user = User.objects.get(id=user_with_photo.id)

    user.photo = png_upload("other.png")
    user.save()

    assert has_no_thumbnails(old_name)
    assert has_thumbnails(user.photo.name)


@pytest.mark.django_db
def test_replacing_twice_on_one_instance(user_with_photo):
    first = user_with_photo.photo.name
    user_with_photo.photo = png_upload("second.png")
    user_with_photo.save()
    second = user_with_photo.photo.name
    user_with_photo.photo = png_upload("third.png")
    user_with_photo.save()

    assert has_no_thumbnails(first)
    assert has_no_thumbnails(second)
    assert has_thumbnails(user_with_photo.photo.name)


@pytest.mark.django_db
def test_clearing_the_photo_removes_its_thumbnails(user_with_photo):
    old_name = user_with_photo.photo.name

    user_with_photo.photo = None
    user_with_photo.save()

    assert has_no_thumbnails(old_name)


@pytest.mark.django_db
def test_saving_without_changing_the_photo_leaves_thumbnails_alone(user_with_photo):
    os.remove(user_with_photo.photo.path)

    User.objects.get(id=user_with_photo.id).save()
    user_with_photo.save()

    assert has_thumbnails(user_with_photo.photo.name)


@pytest.mark.django_db
def test_loading_with_thumbnail_field_deferred():
    user = create_user()

    loaded = User.objects.only("id").get(id=user.id)

    assert loaded.old_photo is None
    assert "photo" in loaded.get_deferred_fields()


@pytest.mark.django_db
def test_saving_a_deferred_row_leaves_thumbnails_alone(user_with_photo):
    os.remove(user_with_photo.photo.path)
    small, medium, _ = thumbnail_paths(user_with_photo.photo.name)
    os.remove(medium)
    loaded = User.objects.only("id", "_str").get(id=user_with_photo.id)

    loaded.save(update_fields=["_str"])

    assert "photo" in loaded.get_deferred_fields()
    assert os.path.exists(small) and not os.path.exists(medium)


@pytest.mark.django_db
def test_missing_thumbnails_are_remade_without_touching_present_ones(user_with_photo):
    small, medium, _ = thumbnail_paths(user_with_photo.photo.name)
    os.remove(medium)
    small_mtime = os.path.getmtime(small)

    ThumbnailImageField.make_thumbnails(
        User._meta.get_field("photo"), user_with_photo.photo
    )

    assert os.path.exists(medium)
    assert os.path.getmtime(small) == small_mtime


@pytest.mark.django_db
def test_deleting_the_row_removes_its_thumbnails(user_with_photo):
    name = user_with_photo.photo.name

    user_with_photo.delete()

    assert has_no_thumbnails(name)


@pytest.mark.django_db
def test_resizing_the_original_remakes_its_thumbnails(user_with_photo):
    user_with_photo.photo.resize_original_image("medium")

    assert max(Image.open(user_with_photo.photo.path).size) == 720
    assert has_thumbnails(user_with_photo.photo.name)
