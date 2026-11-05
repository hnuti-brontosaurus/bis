from collections import defaultdict
from datetime import timedelta

from administration_units.models import BrontosaurusMovement
from bis.emails import emails, text
from django.conf import settings
from django.utils.formats import date_format
from django.utils.html import format_html, format_html_join
from django.utils.timezone import localtime, now
from nest_boxes.models import Batch
from nest_boxes.permissions import is_manager

WANT_TO_HANG_RECIPIENTS = [emails["movement"][1]]
REMIND_AFTER = timedelta(weeks=1)
BOX_COUNTS = {"1-5": "1–5", "6-20": "6–20", "more": "víc než 20", "unknown": "nevím"}
BOX_SOURCES = {
    "have": "Už je máme",
    "make": "Chceme je vyrobit",
    "advice": "Potřebujeme poradit",
}


def want_to_hang(data):
    """The "Chci vyvěsit budky" form; whoever answers replies to the sender."""
    labels = {
        "name": "Jméno",
        "email": "E-mail",
        "phone": "Telefon",
        "place": "Místo",
        "box_count": "Počet budek",
        "box_source": "Budky",
        "message": "Zpráva",
    }
    values = data | {
        "box_count": BOX_COUNTS.get(data["box_count"], ""),
        "box_source": BOX_SOURCES.get(data["box_source"], ""),
    }
    content = format_html_join(
        "\n", "<b>{}:</b> {}", ((labels[key], values[key]) for key in labels)
    )
    text(
        WANT_TO_HANG_RECIPIENTS,
        "Chci vyvěsit budky",
        f"Někdo chce vyvěsit budky:\n\n{content}",
        reply_to=[data["email"]],
    )


def batch_url(batch):
    return f"{settings.FULL_HOSTNAME}/budky/obchuzka/{batch.pk}/"


def open_batches_reminder():
    """Weekly: the batch's author while still a budkař, else every budkař, hears
    about each batch left open for over a week."""
    batches = Batch.objects.filter(
        closed_at=None, created_at__lt=now() - REMIND_AFTER
    ).select_related("area", "created_by")
    budkari = list(BrontosaurusMovement.get().nest_box_managers.all())
    by_recipient = defaultdict(list)
    for batch in batches:
        author = batch.created_by
        for recipient in [author] if author and is_manager(author) else budkari:
            by_recipient[recipient].append(batch)

    for recipient, batches in by_recipient.items():
        items = format_html_join(
            "",
            '<li><a href="{}">{} – {}</a>, otevřená od {}</li>',
            (
                (
                    batch_url(batch),
                    batch.area.name,
                    batch.name,
                    date_format(localtime(batch.created_at).date()),
                )
                for batch in batches
            ),
        )
        text(
            [recipient.email],
            "Otevřené obchůzky budek",
            "Tyto obchůzky budek jsou otevřené déle než týden. "
            "Pokud už jsou hotové, potvrď je, nebo je zavři.\n"
            + format_html("<ul>{}</ul>", items),
        )
