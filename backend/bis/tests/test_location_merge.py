from io import BytesIO

import pytest
from bis.models import Location, LocationPhoto
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
def test_merge_keeps_one_row_and_the_file_of_a_photo_both_locations_have(
    media, django_capture_on_commit_callbacks
):
    kept = Location.objects.create(name="A")
    merged = Location.objects.create(name="B")
    photo = LocationPhoto(location=kept)
    photo.photo.save("shared.png", png())
    LocationPhoto.objects.create(location=merged, photo=photo.photo.name)
    LocationPhoto.objects.create(location=merged, photo="location_photos/own.png")

    with django_capture_on_commit_callbacks(execute=True):
        Location.merge(Location.objects.all(), to_last=False)

    assert sorted(kept.photos.values_list("photo", flat=True)) == [
        "location_photos/own.png",
        photo.photo.name,
    ]
    assert (media / photo.photo.name).exists()
