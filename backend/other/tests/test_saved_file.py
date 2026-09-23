from datetime import timedelta

import pytest
from dateutil.utils import today
from other.models import SavedFile


@pytest.fixture
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


@pytest.fixture
def source(tmp_path):
    path = tmp_path / "export.xlsx"
    path.write_bytes(b"data")
    return path


@pytest.mark.django_db
def test_store_records_the_file_under_a_random_directory(media, source):
    first = SavedFile.store(source, "Akce.xlsx")
    second = SavedFile.store(source, "Akce.xlsx")

    first.refresh_from_db()
    assert first.file.name.startswith("saved_files/")
    assert first.file.name.endswith("/Akce.xlsx")
    assert first.file.name != second.file.name
    assert (media / first.file.name).read_bytes() == b"data"


@pytest.mark.django_db
def test_remove_old_deletes_rows_and_files(media, source):
    old = SavedFile.store(source, "old.xlsx")
    fresh = SavedFile.store(source, "fresh.xlsx")
    SavedFile.objects.filter(id=old.id).update(created_at=today() - timedelta(days=15))
    old_directory = (media / old.file.name).parent

    SavedFile.remove_old()

    assert list(SavedFile.objects.all()) == [fresh]
    assert not old_directory.exists()
    assert (media / fresh.file.name).exists()
