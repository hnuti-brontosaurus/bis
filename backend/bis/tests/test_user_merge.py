from io import BytesIO

import pytest
from bis.models import User
from django.core.files.base import ContentFile
from PIL import Image


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


def png():
    buffer = BytesIO()
    Image.new("RGB", (1, 1)).save(buffer, "PNG")
    return ContentFile(buffer.getvalue())


@pytest.mark.django_db
def test_merge_keeps_the_photo_taken_over_from_the_deleted_user(
    media, django_capture_on_commit_callbacks
):
    user = User.objects.create(first_name="Kept")
    other = User.objects.create(first_name="Merged")
    other.photo.save("photo.png", png())

    with django_capture_on_commit_callbacks(execute=True):
        user.merge_with(other)

    user.refresh_from_db()
    assert user.photo
    assert (media / user.photo.name).exists()
    assert not (media / "user_photos" / "photo.png").exists()


@pytest.mark.django_db
def test_merge_keeps_only_the_refusals_of_the_user_merged_into():
    user = User.objects.create(first_name="Kept", do_not_solicit=True)
    other = User.objects.create(first_name="Merged", do_not_call=True)

    user.merge_with(other)

    user.refresh_from_db()
    assert not user.do_not_call
    assert user.do_not_solicit
