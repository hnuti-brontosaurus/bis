import pytest
from bis.email_validation import validate_email
from django.core.exceptions import ValidationError

VALID = [
    "foo@bar.cz",
    "alice@gmail.com",
    "jirinazarubova@scioskola.cz",
    "lubomir.zavodsky@outlook.sk",
    "ludek.vanicek@centrum.cz",
    "user.name@sub.domain.cz",
    "FOO@BAR.CZ",
]

# Each entry: (input, reason it should be rejected).
INVALID = [
    # Reserved / test TLDs (RFC 2606 + Ecomail-rejected).
    ("123@test.asd", "bogus TLD .asd"),
    ("test@test.test", "reserved TLD .test"),
    ("alice@host.local", "reserved TLD .local"),
    ("alice@example.invalid", "reserved TLD .invalid"),
    ("alice@example.example", "reserved TLD .example"),
    ("alice@localhost", "reserved hostname localhost"),
    ("alice@sub.localhost", "reserved hostname localhost as TLD"),
    # Historic junk domain.
    ("foo@gk.zy", "historic junk domain gk.zy"),
    # Typos that REPAIRS would auto-fix → reject as written.
    ("alice@server.ocm", "typo .ocm"),
    ("alice@server.comj", "typo .comj"),
    ("alice@server.comm", "typo .comm"),
    ("alice@sznam.cz", "typo sznam.cz"),
    # Plus-tagged addresses (subaddressing).
    ("alice+anything@gmail.com", "plus addressing"),
    ("ivanarichterova+hanka@gmail.com", "plus addressing (real example)"),
    ("alena.salajkova+karolina.salajkova@gmail.com", "plus addressing (real example)"),
]


@pytest.mark.parametrize("value", VALID)
def test_valid_email_passes(value):
    validate_email(value)


@pytest.mark.parametrize("value,reason", INVALID)
def test_invalid_email_rejected(value, reason):
    with pytest.raises(ValidationError):
        validate_email(value)


def test_empty_string_passes():
    validate_email("")


def test_none_passes():
    validate_email(None)
