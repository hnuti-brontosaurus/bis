import pytest
from bis.models import User


@pytest.mark.django_db
def test_loading_with_thumbnail_field_deferred():
    user = User.objects.create(email="deferred@example.com", _str="Deferred")

    loaded = User.objects.only("id").get(id=user.id)

    assert loaded.old_photo is None
    assert "photo" in loaded.get_deferred_fields()
