"""Groq-based ingredient enrichment.

Called from the API view after an Ingredient is created. The signal layer
handles only cheap normalization (whitespace, capitalization); anything that
talks to the network lives here.

If GROQ_API_KEY is empty, enrichment is skipped (legitimate dev mode).
Otherwise the call is made and the result written back to the instance.
Errors are NOT swallowed — a misconfigured key or a malformed response
should surface to the API caller, not vanish into a log line.
"""

import json

import groq
from cookbook.models.ingredients import Ingredient
from cookbook_categories.models import Allergen
from django.conf import settings

# https://console.groq.com/playground
INGREDIENT_SYSTEM_PROMPT = """
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
  "allergens": list of strings z {"gluten","soya","nuts"},
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

5) "allergens"
- Seznam slugů alergenů, které surovina typicky obsahuje. Povolené hodnoty: "gluten" (lepek — pšenice, ječmen, žito, špalda, kuskus, bulgur, pšeničná mouka, chleba, těstoviny, pivo, ...), "soya" (sója — sójové boby, sójové mléko, tofu, tempeh, sójová omáčka, ...), "nuts" (oříšky — vlašské, lískové, kešu, mandle, pistácie, para, makadamy, pekanové ořechy; arašídy NE — botanicky luštěnina).
- Pokud surovina žádný z těchto alergenů typicky neobsahuje, vrať [].
- Buď opatrný — vrať alergen jen tehdy, je-li v surovině typicky obsažen v běžně prodávané variantě.

6) Nejednoznačný nebo nesmyslný vstup
- Pokus se o nejlepší možný odhad.
- Pokud ani tak nelze rozhodnout, použij tento fallback:
  {
    "state": "solid",
    "g_per_liter": null,
    "g_per_piece": null,
    "g_per_serving": null,
    "allergens": []
  }

7) Výstup
- Musí být validní JSON.
- Používej pouze dvojité uvozovky.
- Žádné trailing čárky.
- Žádný další text.

Příklady (vstup -> výstup):

brambory ->
{"state":"solid","g_per_liter":null,"g_per_piece":85,"g_per_serving":250,"allergens":[],"reasoning":"Brambory jsou pevná surovina, která se běžně používá v kusech a jako příloha. Průměrná brambora váží kolem 85g a typická porce je asi 250g."}

mléko ->
{"state":"liquid","g_per_liter":1030,"g_per_piece":null,"g_per_serving":null,"allergens":[],"reasoning":"Mléko je tekutá surovina s hustotou přibližně 1030g/l. Nepočítá se na kusy a nemá standardní porci."}

mouka ->
{"state":"solid","g_per_liter":600,"g_per_piece":null,"g_per_serving":null,"allergens":["gluten"],"reasoning":"Hladká pšeničná mouka je sypká pevná surovina s objemovou hustotou kolem 600g/l. Obsahuje lepek."}

vlašské ořechy ->
{"state":"solid","g_per_liter":null,"g_per_piece":5,"g_per_serving":30,"allergens":["nuts"],"reasoning":"Vlašské ořechy se běžně počítají na kusy (~5g) a typická porce je hrst (~30g). Patří mezi ořechy."}

tofu ->
{"state":"solid","g_per_liter":null,"g_per_piece":null,"g_per_serving":150,"allergens":["soya"],"reasoning":"Tofu je sójový výrobek; běžná porce 150g. Obsahuje sóju."}"""


def enrich_ingredient(instance: Ingredient) -> bool:
    """Fill state / g_per_* / reasoning on `instance` via Groq.

    Returns True if the instance was modified and should be saved by the
    caller, False if enrichment was skipped (no API key, empty name).

    Any Groq / JSON / network error is raised — the caller decides how to
    surface it. The freshly-created Ingredient is left as-is in that case.
    """
    if not instance.name:
        return False

    api_key = settings.GROQ_API_KEY
    if not api_key:
        return False

    client = groq.Groq(api_key=api_key)
    chat_completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": INGREDIENT_SYSTEM_PROMPT},
            {"role": "user", "content": instance.name},
        ],
        top_p=1,
        reasoning_effort="medium",
    )

    response_content = chat_completion.choices[0].message.content
    data = json.loads(response_content)

    if state := data.get("state"):
        assert state in ["solid", "liquid"]
        instance.state = state
    if g_per_liter := data.get("g_per_liter"):
        instance.g_per_liter = int(g_per_liter)
    if g_per_piece := data.get("g_per_piece"):
        instance.g_per_piece = int(g_per_piece)
    if g_per_serving := data.get("g_per_serving"):
        instance.g_per_serving = int(g_per_serving)
    if reasoning := data.get("reasoning"):
        instance.reasoning = reasoning

    # Allergens are M2M and require an existing PK; the caller (post-create)
    # already has one. Replace the set even when empty so a reclassification
    # can clear stale flags.
    allergen_slugs = data.get("allergens") or []
    instance.allergens.set(Allergen.objects.filter(slug__in=allergen_slugs))

    return True
