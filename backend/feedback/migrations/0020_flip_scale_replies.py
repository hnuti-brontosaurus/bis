from datetime import UTC, datetime
from math import ceil

from django.db import migrations

# The form offered 1-10 until the deploy between the last 1-10 reply
# (2026-03-28) and the first 1-5 one (2026-03-31). Nothing on the inquiry
# records which scale it was answered on, so the reply date has to.
FIVE_POINT_SCALE_SINCE = datetime(2026, 3, 30, tzinfo=UTC)

# The organizers' own questions of Na Hraně 2026 were worded and answered as
# school grades, so they already are 1 = best.
SCHOOL_GRADED_EVENT = 13355

REWORDED_INQUIRIES = {
    482: (
        "Doporučil/a bys Brďo kurz dalším lidem z tvého oddílu, kteří se chystají zaojit do vedení oddílu? (1 - vůbec, 10 - určitě!)",
        "Doporučil/a bys Brďo kurz dalším lidem z tvého oddílu, kteří se chystají zaojit do vedení oddílu? (1 - určitě!, 5 - vůbec)",
    ),
    12454: (
        "Bylo jsem: 1 = neustále nevyspalé s kruhama pod očima / 10 = vyspinkané do růžova",
        "Bylo jsem: 1 = vyspinkané do růžova / 5 = neustále nevyspalé s kruhama pod očima",
    ),
    12455: (
        "Organizátorský tým to: 1 = neměl vůbec pod kontrolou, byla anarchie na táboře a uctíval se bronzový býček / 10 = zvládal a měl všechno připravené",
        "Organizátorský tým to: 1 = zvládal a měl všechno připravené / 5 = neměl vůbec pod kontrolou, byla anarchie na táboře a uctíval se bronzový býček",
    ),
    12456: (
        "Volný čas jsem: 1 = nemělo ani minutu, ani mamince jsem nestihlo dát vědět, že žiju / 10 = mělo spousty, tak moc že jsem se naučilo na housle hrát",
        "Volný čas jsem: 1 = mělo spousty, tak moc že jsem se naučilo na housle hrát / 5 = nemělo ani minutu, ani mamince jsem nestihlo dát vědět, že žiju",
    ),
    12457: (
        "Zázemí bylo: 1 = šílené, všude špína, zima a bordel / 10 = připadalo jsem si jako princezna na zámku",
        "Zázemí bylo: 1 = připadalo jsem si jako princezna na zámku / 5 = šílené, všude špína, zima a bordel",
    ),
    28594: (
        "Jak bys hodnotil*a smysluplnost dobrovolnické práce? (1-práce nedávala smysl, 5-práce byla smysluplná)",
        "Jak bys hodnotil*a smysluplnost dobrovolnické práce? (1-práce byla smysluplná, 5-práce nedávala smysl)",
    ),
    28597: (
        "Jak jsi byl*a spokojený/á s workshopy? (5 - nejlepší)",
        "Jak jsi byl*a spokojený/á s workshopy? (1 - nejlepší)",
    ),
}


def flipped(rating, created_at):
    if created_at < FIVE_POINT_SCALE_SINCE:
        rating = ceil(rating / 2)
    return 6 - rating


def migrate(apps, schema_editor):
    Reply = apps.get_model("feedback", "Reply")
    Inquiry = apps.get_model("feedback", "Inquiry")

    replies = []
    for reply in Reply.objects.filter(
        inquiry__data__type="scale", value__isnull=False
    ).select_related("feedback", "inquiry__feedback_form"):
        # A comment without a rating used to be saved as "null <comment>"
        # rated 0, which the export then averaged in.
        if reply.value == 0:
            reply.reply = reply.reply.removeprefix("null ")
            reply.value = None
            reply.data.pop("rating", None)
            replies.append(reply)
            continue

        inquiry = reply.inquiry
        if not inquiry.slug and inquiry.feedback_form.event_id == SCHOOL_GRADED_EVENT:
            continue

        rating = flipped(reply.value, reply.feedback.created_at)
        reply.reply = f"{rating}{reply.reply.removeprefix(str(reply.value))}"
        reply.value = rating
        if "rating" in reply.data:
            reply.data["rating"] = rating
        replies.append(reply)

    Reply.objects.bulk_update(replies, ["reply", "value", "data"], batch_size=100)

    # Ids are production ones, so the text is matched too.
    for inquiry_id, (old, new) in REWORDED_INQUIRIES.items():
        Inquiry.objects.filter(id=inquiry_id, inquiry=old).update(inquiry=new)


class Migration(migrations.Migration):
    dependencies = [
        ("feedback", "0019_rename_email_content_variables"),
    ]

    operations = [migrations.RunPython(migrate, migrations.RunPython.noop)]
