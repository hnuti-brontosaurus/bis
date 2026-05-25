import re

from django.core.exceptions import ValidationError

REPAIRS = [
    # "a@b.cz, c@d.cz" → keep first address only (comma-separated lists)
    (re.compile(r"^([^,]+),.+$"), r"\1"),
    # strip all whitespace anywhere in the address
    (re.compile(r"\s+"), ""),
    # "foo.@bar.cz" → "foo@bar.cz" (stray dots before @)
    (re.compile(r"\.+@"), "@"),
    # "foo@bar..cz" → "foo@bar.cz" (collapse repeated dots in the domain)
    (re.compile(r"@([^@]*?)\.{2,}"), r"@\1."),
    # typo: ".comj" → ".com"
    (re.compile(r"\.comj$", re.IGNORECASE), ".com"),
    # typo: ".comm" → ".com"
    (re.compile(r"\.comm$", re.IGNORECASE), ".com"),
    # typo: ".ocm" → ".com"
    (re.compile(r"\.ocm$", re.IGNORECASE), ".com"),
    # typo: "@sznam.cz" → "@seznam.cz"
    (re.compile(r"@sznam\.cz$", re.IGNORECASE), "@seznam.cz"),
]

# Things Django's EmailValidator accepts but we don't.
NULLIFY = re.compile(
    r"^.*@(?:"
    # historic junk domain from an old data import
    r"gk\.zy"
    # reserved/test TLDs from RFC 2606 + common bogus ones Ecomail rejects
    r"|(?:[^@]*\.)?(?:asd|test|example|invalid|local|localhost)"
    # single-letter TLDs (no real TLD is 1 char; Ecomail rejects them)
    r"|[^@]*\.[a-z]"
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
