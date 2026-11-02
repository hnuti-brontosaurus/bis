import pytest
from bis.models import User
from ecomail.tags import compute_tags


@pytest.mark.django_db
@pytest.mark.parametrize("refused", [True, False])
def test_refusing_solicitation_is_tagged(refused):
    user = User.objects.create(
        first_name="A", last_name="B", email="a@example.com", do_not_solicit=refused
    )

    assert ("Nežádat o dar" in compute_tags(user)) == refused
