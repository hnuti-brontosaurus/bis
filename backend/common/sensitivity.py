"""Groq classification of questionnaire questions and feedback inquiries.

The MCP schema hides the answers to a question from accounts that may not see
its sensitivity. A question that is not classified yet (null) hides its answers
from every account, so a failed or skipped classification fails closed; the
nightly `classify_questions` retries those.
"""

import json

import groq
from bis.background import in_background
from django.conf import settings
from django.db import transaction
from django.db.models import TextChoices


class Sensitivity(TextChoices):
    NONE = "none", "Běžné údaje"
    PERSONAL = "personal", "Osobní údaje"
    HEALTH = "health", "Zdravotní údaje"


SYSTEM_PROMPT = """
Klasifikuješ otázky z přihlášek na akce a z formulářů zpětné vazby podle toho, \
jaké údaje o člověku mohou prozradit odpovědi na ně.

Uživatel pošle JSON objekt otázek podle id; každá má text ("question") a \
nastavení ("settings": typ otázky, případně nabízené možnosti).

Vrať POUZE jeden validní JSON objekt, který každému id přiřadí jednu z hodnot, \
např. {"0": "none", "1": "health"}:
- "health" — odpověď může prozradit cokoli o zdraví: nemoci, alergie a \
intolerance, léky, očkování, zranění, fyzická či psychická omezení a obtíže \
(i fobie, úzkosti, deprese), postižení, těhotenství. Patří sem:
  - každá otázka na omezení ve stravě nebo na dietu, i bez uvedeného důvodu \
(omezení bývají zdravotní), a nabídka, kde je bezlepková či bezlaktózová \
dieta nebo alergie,
  - otázka, která se ptá na zdraví spolu s něčím jiným ("fyzická, psychická \
či stravovací omezení"),
  - otevřená otázka, co bychom o tobě nebo o dítěti měli vědět — organizátoři \
se jí ptají hlavně na zdraví.
- "personal" — odpověď sama je údaj, který identifikuje nebo kontaktuje \
konkrétního člověka: jméno, přezdívka, e-mail, telefon, adresa, celé datum \
narození, rodné číslo, číslo dokladu nebo účtu, kontakt na rodiče či blízkou \
osobu, odkaz na profil na sociální síti. Věk ani rok narození člověka \
neidentifikují, ty jsou "none".
- "none" — všechno ostatní. Patří sem i otázky na věk, povahu, zkušenosti, \
názory, zájmy a preference, i když jsou osobní nebo obsahují slovo „kontakt“: \
odkud přijedeš, jak ses o akci dozvěděl, jezdíš na akce Brontosaura, jak moc \
jsi kontaktní osoba (dotyky, objímání), jak ses na akci cítil, umíš plavat, \
hodnocení akce, volba mezi masovou a vegetariánskou stravou, velikost trička, \
nadpisy sekcí.

Když váháš mezi "health" a čímkoli jiným, zvol "health".
"""


BATCH_SIZE = 50


def classify(questions, max_retries):
    """Classify a batch of (text, data) questions in one Groq call."""
    client = groq.Groq(api_key=settings.GROQ_API_KEY, max_retries=max_retries)
    content = json.dumps(
        {
            str(index): {"question": text, "settings": data}
            for index, (text, data) in enumerate(questions)
        },
        ensure_ascii=False,
    )
    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content},
        ],
        response_format={"type": "json_object"},
        reasoning_effort="medium",
    )
    sensitivities = json.loads(completion.choices[0].message.content)
    return [Sensitivity(sensitivities[str(index)]) for index in range(len(questions))]


def classify_unclassified(model, text_field, max_retries=10):
    """Classify every distinct unclassified question once, BATCH_SIZE per Groq
    call, since events copy their questionnaires and most questions repeat.

    A batch takes about half of the 8K tokens per minute the model allows, so
    a backfill waits on 429s; the client sleeps for their retry-after."""
    if not settings.GROQ_API_KEY:
        return
    unclassified = model.objects.filter(sensitivity=None)
    questions = list(unclassified.order_by().values_list(text_field, "data").distinct())
    for start in range(0, len(questions), BATCH_SIZE):
        batch = questions[start : start + BATCH_SIZE]
        for (text, data), sensitivity in zip(batch, classify(batch, max_retries)):
            unclassified.filter(**{text_field: text, "data": data}).update(
                sensitivity=sensitivity
            )


@in_background
def _classify_in_background(model, text_field):
    # shares the queue with outgoing emails, so it must not wait out a rate
    # limit; whatever fails here is left to the nightly run
    classify_unclassified(model, text_field, max_retries=0)


def reset_sensitivity(instance, text_field):
    """pre_save: a changed question takes the sensitivity of an identical
    classified one, or none at all until it is classified."""
    model = type(instance)
    question = (getattr(instance, text_field), instance.data)
    stored = model.objects.filter(pk=instance.pk).values_list(text_field, "data")
    if stored.first() == question:
        return
    instance.sensitivity = (
        model.objects.filter(**{text_field: question[0], "data": question[1]})
        .exclude(sensitivity=None)
        .values_list("sensitivity", flat=True)
        .first()
    )


def classify_after_save(instance, text_field):
    """post_save: classify a question that could not reuse a sensitivity."""
    if instance.sensitivity is None:
        model = type(instance)
        transaction.on_commit(lambda: _classify_in_background(model, text_field))
