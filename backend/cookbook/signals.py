import json
import logging
import os
import re

import groq
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from cookbook.models import *
from cookbook.models.ingredients import Ingredient

# https://console.groq.com/playground
ingredient_system_prompt = """
Jsi klasifikátor a odhadovač parametrů surovin.

Uživatel vždy pošle pouze název jedné suroviny (1 řádek).
Název může obsahovat:
- překlepy
- brandy
- jednotné nebo množné číslo
- přídavná jména (např. „hladká“, „polotučné“, „olivový“)

Tvým úkolem je vrátit POUZE jeden validní JSON objekt (bez markdownu, bez kódu v blocích, bez vysvětlení, bez textu navíc).

Vždy vrať všechny klíče v tomto schématu:
{
  "state": "solid" | "liquid",
  "g_per_liter": integer | null,
  "g_per_piece": integer | null,
  "g_per_serving": integer | null,
  "reasoning": string
}

Kde "reasoning" je stručné vysvětlení tvého rozhodnutí v češtině, proč jsi zvolil dané hodnoty pro tuto surovinu.

Pravidla:

1) "state"
- Musí být přesně "solid" nebo "liquid".
- Rozhoduj podle běžného kuchyňského použití.

2) "g_per_liter"
- Celé číslo = hustota v gramech na litr.
- Pokud je state = "liquid":
  - vrať hustotu při cca 20 °C.
- Pokud je state = "solid":
  - vrať sypnou / objemovou hustotu (bulk density) pouze u surovin, které se běžně měří na objem (hrnek, lžíce apod.).
- Pokud převod na objem nedává smysl, vrať null.

3) "g_per_piece"
- Pokud je state = "liquid", vždy null.
- Pokud je state = "solid":
  - vrať odhad typické hmotnosti 1 kusu pouze tehdy, pokud se surovina běžně používá v kusech (např. vejce, jablko, banán, rohlík).
- Pokud se běžně nepočítá na kusy, vrať null.

4) "g_per_serving"
- Typické množství suroviny na jednu porci v běžné kuchyni.
- Použij pouze u surovin, kde pojem porce dává smysl (např. příloha, pečivo, těstoviny, rýže), či pro typické možství (olej na pánev, sůl).
- Pokud pojem porce nedává smysl, vrať null.

5) Nejednoznačný nebo nesmyslný vstup
- Pokus se o nejlepší možný odhad.
- Pokud ani tak nelze rozhodnout, použij tento fallback:
  {
    "state": "solid",
    "g_per_liter": null,
    "g_per_piece": null,
    "g_per_serving": null
  }

6) Výstup
- Musí být validní JSON.
- Používej pouze dvojité uvozovky.
- Žádné trailing čárky.
- Žádný další text.

Příklady (vstup -> výstup):

brambory ->
{"state":"solid","g_per_liter":null,"g_per_piece":85,"g_per_serving":250,"reasoning":"Brambory jsou pevná surovina, která se běžně používá v kusech a jako příloha. Průměrná brambora váží kolem 85g a typická porce je asi 250g."}

mléko ->
{"state":"liquid","g_per_liter":1030,"g_per_piece":null,"g_per_serving":null,"reasoning":"Mléko je tekutá surovina s hustotou přibližně 1030g/l. Nepočítá se na kusy a nemá standardní porci."}

mouka ->
{"state":"solid","g_per_liter":600,"g_per_piece":null,"g_per_serving":null,"reasoning":"Mouka je sypká pevná surovina s objemovou hustotou kolem 600g/l. Nepoužívá se v kusech a nemá standardní porci."}"""


@receiver(pre_save, sender=Ingredient, dispatch_uid="ingredient_fill_default")
def ingredient_fill_default(instance: Ingredient, **kwargs):
    instance.name = " ".join(instance.name.split())

    if not instance.name:
        return

    if instance.pk is None:
        instance.name = instance.name.lower().capitalize()

        api_key = settings.GROQ_API_KEY

        if not api_key:
            return

        try:
            client = groq.Groq(api_key=api_key)
            chat_completion = client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": ingredient_system_prompt},
                    {"role": "user", "content": instance.name},
                ],
                top_p=1,
                reasoning_effort="medium",
            )

            # Parse the response
            response_content = chat_completion.choices[0].message.content
            ingredient_data = json.loads(response_content)

            if state := ingredient_data.get("state"):
                assert state in ["solid", "liquid"]
                instance.state = state

            if g_per_liter := ingredient_data.get("g_per_liter"):
                instance.g_per_liter = int(g_per_liter)

            if g_per_piece := ingredient_data.get("g_per_piece"):
                instance.g_per_piece = int(g_per_piece)

            if g_per_serving := ingredient_data.get("g_per_serving"):
                instance.g_per_serving = int(g_per_serving)

            if reasoning := ingredient_data.get("reasoning"):
                instance.reasoning = reasoning

        except Exception as e:
            logging.exception(f"Error running groq: {e}")
