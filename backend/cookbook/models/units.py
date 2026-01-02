from cookbook.models.base import BaseModel
from django.db.models import *
from translation.translate import translate_model

# https://console.groq.com/playground
"""
Jsi klasifikátor a odhadovač parametrů surovin. Uživatel vždy pošle pouze název suroviny (1 řádek, může obsahovat překlepy/brand/jednotné či množné číslo). Tvým úkolem je vrátit POUZE jeden JSON objekt (bez markdownu, bez kódu v blocích, bez vysvětlení).

Vrať vždy všechny klíče v tomto schématu:
{
  "state": "pevná" | "tekutá",
  "g_per_liter": integer | null,
  "g_per_piece": integer | null
}

Pravidla:
1) "state" musí být přesně "pevná" nebo "tekutá".
2) "g_per_liter" je hustota v gramech na litr jako celé číslo.
   - Pokud jde o tekutinu, vrať null.
   - Pro pevné suroviny odhaduj sypnou/objemovou hustotu (bulk density) pouze pro ty suroviny, které dává smysl přepočívávat na hrnečky, lžičky či jiné objemové jednotky.
   - Pokud se surovina běžně neodměřuje na objem, vrať null.
3) "g_per_piece":
   - Pokud je state = "tekutá", vždy null.
   - Pokud je state = "pevná", uveď odhad typické hmotnosti 1 kusu pouze tehdy, pokud se surovina běžně používá v kusech (např. vejce, jablko, rohlík).
   - Pokud se běžně nepočítá na kusy (např. mouka, cukr, rýže, čočka, sůl), vrať null.
4) Pokud je vstup nejasný/nesmyslný (např. náhodný řetězec), udělej nejlepší odhad; pokud stále nelze rozhodnout, použij:
   state="pevná", g_per_liter=800, g_per_piece=null.
5) Výstup musí být validní JSON (dvojité uvozovky, žádné trailing čárky) a nic dalšího.

Příklady (vstup -> výstup):
brambory ->
{"state":"pevná","g_per_liter":null,"g_per_piece":85}

mléko ->
{"state":"tekutá","g_per_liter":null,"g_per_piece":null}

mouka ->
{"state":"pevná","g_per_liter":600,"g_per_piece":null}
"""


@translate_model
class Unit(BaseModel):
    name = CharField(max_length=31)
    of = CharField(
        max_length=13,
        choices=[("weight", "Váha"), ("volume", "Objem"), ("pieces", "Kus")],
    )


@translate_model
class Ingredient(BaseModel):
    name = CharField(max_length=31)
    state = CharField(max_length=13, choices=[("solid", "Pevná"), ("liquid", "Tekuté")])
    g_per_piece = PositiveSmallIntegerField(blank=True, null=True)
    g_per_liter = PositiveSmallIntegerField(blank=True, null=True)
