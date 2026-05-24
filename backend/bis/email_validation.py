import re

from django.core.exceptions import ValidationError

REPAIRS = [
    (re.compile(r"^([^,]+),.+$"), r"\1"),
    (re.compile(r"\s+"), ""),
    (re.compile(r"\.+@"), "@"),
    (re.compile(r"@([^@]*?)\.{2,}"), r"@\1."),
    (re.compile(r"\.comj$", re.IGNORECASE), ".com"),
    (re.compile(r"\.comm$", re.IGNORECASE), ".com"),
    (re.compile(r"\.ocm$", re.IGNORECASE), ".com"),
    (re.compile(r"@sznam\.cz$", re.IGNORECASE), "@seznam.cz"),
]

# Things Django's EmailValidator accepts but we don't:
# - reserved/test TLDs from RFC 2606 + common bogus ones that Ecomail rejects
# - the historic gk.zy junk domain
# (Missing-@, 1-letter TLDs, whitespace, comma lists are already caught upstream.)
NULLIFY = re.compile(
    r"^.*@(?:"
    r"gk\.zy"
    r"|(?:[^@]*\.)?(?:asd|test|example|invalid|local|localhost)"
    r")$",
    re.IGNORECASE,
)


def repair_email(email):
    for pattern, replacement in REPAIRS:
        email = pattern.sub(replacement, email)
    if NULLIFY.match(email):
        return None
    return email


def validate_email(value):
    if not value:
        return
    local, _, _ = value.partition("@")
    if "+" in local:
        raise ValidationError(f"E-mail s '+' v lokální části není povolen: {value}")
    if repair_email(value) != value:
        raise ValidationError(f"Neplatná e-mailová adresa: {value}")
