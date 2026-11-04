"""Reads the free-text notes of the old database: notes take precedence over the fields.

The labels follow old_budky/docs/classify_notes.py, which was checked by hand
against every note of the dump of 2 November 2026.
"""

import re

from nest_boxes.models import NestBox

RULES = {
    "bird_species": r"sýkor|sykor|\bkoňadr|końadr|modřink|vrabec|vrabc|brhlík|krutihlav|špaček|holub|minařík|\bsov[ay]\b|ptáci",
    "bird_unclear": r"^strakapoud$",
    "eggs": r"vejce|vajíč|skořáp",
    "nest": r"(?<!vosí )(?<!sršní )(?<!zde )hnízd|\bmech\b|^peří$|vývršky|slaměné|kůr\.šup|kůra",
    "traces": r"^trus$|kousíček mechu|pobytové znamení",
    "dead_animal": r"mrtv|uhynul|kostr|kostřičk|lebky|tělíčka",
    "breeding_failed": r"neúspěš",
    "breeding_succeeded": r"(?<!ne)úspěš|vyhnízd",
    "occupation_attempt": r"pokus o obsaz|pokusu o obsaz|pokus strakapouda",
    "other_animal": r"\bmyš|myši|plch|plš|\bvos[yíi]|vosí|sršn|sršeň|netopýr|veverk|mravenc|plošt|škvoř|brouk|ponrav|hlodav|nakakané",
    "confirmed_empty": r"nebylo zde hnízdo|prázdn|neobsazen",
    "occupancy_unknown": r"nejasná informace|není záznam o obsaz|obsazenost nezjištěna|zkontrolovat obsazenost|neurčený druh",
    "not_reached": r"nestihl|nedostali|setmění|minuli jsme|zapoměli",
    "could_not_open": r"nelze otevř|nejde otevř|nepodařilo se otev|neotvíratel|nedobytn",
    "not_inspected": r"nekontrolov|nezkontrol|nezkontol|kontrola ze země",
    "not_cleaned": r"nečist|nečišt|nevyčišt|nelze vyčist|nelze čist|nelze čišt|nešla nám sundat",
    "not_found": r"nenal|nedohled|dopátrat|popátrat|zmizela|^není tam|budka chybí|chybí strom|^chybí,|jen lišta|pokácené stromy|není tam",
    "found_again": r"^nasalezena|^nalezena[!.]?$|^nalezena,|nově (nalezena|nalezená|nalezeno|objevena)|^budka objevena",
    "taken_down": r"stažen|sundan|sundán|odstraněn|odnesen|odneseno|z terénu",
    "destroyed": r"zničen|rozpadá|rozpadlá|vyvrácen|dosloužil",
    "tree_gone": r"chybí strom|pokácen|spadl\w* strom|vyvrácen",
    "fell_down": r"spadl|spadeno|spadená|na zemi",
    "retire": r"vyřad|zrušit|nebude se nahrazovat|nebude se umísťovat|využít číslo jinde",
    "replaced": r"vyměněn|nahrazen|výměna za novou|vyměna za novou|pověšena nová|vyvěšena nová|nová 20\d\d|náhrad",
    "hung": r"^vyvěšen|nově vyvěš|nově pověš|^nová$|^nová,|nazpět|vrátili jsme",
    "repaired_done": r"opraven[aoé]?\b|opr\. a|dáno lino|natlučen|přidán ochran|nový otvor|připevnili",
    "moved_done": r"přesunut|přemístěn|převěšen|posunuta|pověšena výš|^snížena|na jiný strom",
    "replace_needed": r"nahradit|vyměnit|dát novou|pověsit novou|výměna nutná|nutná výměna|^výměna 2023|vhodná výměna",
    "repair_needed": r"opravit|spravit|oprava|rozklov|vyklov|vyklob|oklov|oťukan|třísklý|proklov|prask|rozbit|rozbyt|děrav|díra|chybí d|chybí s|chybí p|chyběla|rozklíž|zlomen|poškoz|narušen|zhnil|plesniv|houba|vadn|vypadává|odpadává|povolen|povolit|špatně se ot|horší ot|těžko ot|přidat kování|doplnit ob|doppnit|přivrtat|lépe|naštípnut|štíplý|zarůst|zarostl|oplechovat|zesílit|pvc|lino na|krátký|nejde dovřít|stav vlet|rozšířený|příliš velký otvor|skobu|bez střechy|^dno$|dno není|přední stěna|stříšk|zmenšit",
    "move_needed": r"přesunout|přemístnění|přemístění|přendáme|posunout|^obnovit\?",
    "coordinates": r"zaměř|přeměř|souř|není na mapě|viz mapa|o 20m|přibližná|orientační",
    "number": r"čísl|\bč\.|přečíslov|bývalá|^stará 1|^stara 43|^\d+[ab]?$|neoznač|nepodepsan|na budce|stará budka|staré 225|náhrada č",
    "access": r"vysoko|žebřík|mimo cestu|před vstupem|oplocenc|\bklíč|nad budkou|exponovaná",
    "opening": r"\bhorní\b|vrchní|\bpřední\b|spodní|boční ot|otevírání|otvírání|otv\.|nemá otvírání",
    "box_type": r"rehkovník|špačkovník|sovník|sovinec|sýkorník|typ rehek|veverkovník|holobudk|dřevocement|barel|sloup|přízemní|^krutihlav$|^rehek",
    "antipredator": r"antipredač|oplechovan|ochranný límec",
    "owner_or_name": r"není naše|orchis|budka lvíčat|pionýr|okrašlovac|bronto praha|titio|titijo|otisk přírody|sluníčková|vyvěšena dobrovolníky",
    "installation_date": r"^vyvěšeno \d|přesný datum vyvěšení",
    "performed_by_unit": r"^vlkani$",
    "ok": r"^ok$|^jinak ok$",
}
COMPILED = {
    label: re.compile(pattern, re.IGNORECASE) for label, pattern in RULES.items()
}

BIRD_EVIDENCE = {
    "bird_species",
    "bird_unclear",
    "eggs",
    "nest",
    "dead_animal",
    "breeding_succeeded",
    "breeding_failed",
    "occupation_attempt",
}
UNSEEN_INSIDE = {"could_not_open", "not_inspected", "occupancy_unknown", "traces"}
EVIDENCE = (
    BIRD_EVIDENCE
    | UNSEEN_INSIDE
    | {
        "other_animal",
        "confirmed_empty",
        "not_cleaned",
        "ok",
    }
)
MAINTENANCE = {"replaced", "hung", "repaired_done", "moved_done", "coordinates"}
ENDING = {"destroyed", "retire", "tree_gone"}
INSTALLATION = {"hung", "replaced", "installation_date"}


def normalized(note):
    return " ".join((note or "").split()).lower()


def labels(note):
    key = normalized(note)
    if not key:
        return frozenset()
    found = {label for label, pattern in COMPILED.items() if pattern.search(key)}
    if "breeding_failed" in found:
        found.discard("breeding_succeeded")
    if "not_reached" in found:
        found.discard("not_found")
    if "not_found" in found:
        found.discard("found_again")
    if "traces" in found:
        found.discard("nest")
    if "replaced" in found:
        found -= {"replace_needed", "hung"}
    return frozenset(found)


BIRDS = (
    ("konadra", r"koňadr|końadr"),
    ("modrinka", r"modřink"),
    ("uhelnicek", r"uhelníč"),
    ("parukarka", r"parukář"),
    ("luzni", r"sýkora lužní"),
    ("vrabec", r"vrab"),
    ("brhlik", r"brhlík"),
    ("krutihlav", r"krutihlav"),
    ("spacek", r"špaček|špačk(?!ovník)"),
    ("strakapoud", r"^strakapoud$"),
    ("sova", r"\bsov[ay]\b|puštík"),
    ("jiny_ptak", r"holub|minařík"),
)
ANIMALS = (
    ("srsni", r"sršn|sršeň"),
    ("vosy", r"\bvos[yíi]|vosí"),
    ("mysi", r"\bmyš|myši|nakakané"),
    ("plsi", r"plch|plš"),
    ("netopyri", r"netopýr"),
    ("veverka", r"veverk"),
    ("mravenci", r"mravenc"),
    ("jine", r"plošt|škvoř|brouk|ponrav|hlodav"),
)
GENERIC_TIT = re.compile(r"sýkor|sykor", re.IGNORECASE)


def birds(note):
    key = normalized(note)
    found = {slug for slug, pattern in BIRDS if re.search(pattern, key)}
    tits = {"konadra", "modrinka", "uhelnicek", "parukarka", "luzni"}
    if GENERIC_TIT.search(key) and not found & tits:
        found.add("sykora")
    return found


def animals(note):
    key = normalized(note)
    found = {slug for slug, pattern in ANIMALS if re.search(pattern, key)}
    if "srsni" in found and not re.search(r"\bvos[yíi]", key):
        found.discard("vosy")
    return found


def not_cleaned_reason(note):
    key = normalized(note)
    if re.search(r"sršn|sršeň", key):
        return "hornets"
    if re.search(r"pták|vejc|na vajíčkách|živá|netopýr", key):
        return "bird_inside"
    if re.search(r"vysoko|žebřík", key):
        return "too_high"
    return "other"


UNSUITABLE = re.compile(r"nevhodn")
NOT_REPLACED = re.compile(r"nebude se (umísťovat|nahrazovat)")


def asks_to_move(note_labels, note):
    """An unsuitable spot: the box is to be moved, it has not ended."""
    return "tree_gone" not in note_labels and bool(UNSUITABLE.search(normalized(note)))


def end_reason(note_labels, note):
    """A box that won't be replaced ended for whatever else the note says, if anything."""
    if "tree_gone" in note_labels:
        return "tree_gone"
    if NOT_REPLACED.search(normalized(note)):
        return "worn_out" if "destroyed" in note_labels else None
    if "not_found" in note_labels:
        return "lost"
    return "worn_out"


YEAR = re.compile(r"\b(20\d\d)\b")


def year(note):
    match = YEAR.search(note or "")
    return int(match[1]) if match else None


Opening, Material = NestBox.Opening, NestBox.Material
OPENINGS = (
    (Opening.SIDE, r"boční ot|otevírání z boku|otvírání z boku"),
    (Opening.NONE, r"nemá otvírání"),
    (
        Opening.ROOF,
        r"\b(horní|vrchní)\b(?! (cest|hřeb))|(otvírání|otevírání) (nahoře|shora)",
    ),
    (Opening.FRONT, r"^\W*přední\b(?! (stěn|stran))|přední (otvírání|otvířání)"),
)


def opening(note):
    key = normalized(note)
    found = {value for value, pattern in OPENINGS if re.search(pattern, key)}
    return found.pop() if len(found) == 1 else None


def material(note):
    key = normalized(note)
    if "dřevocement" in key:
        return Material.WOOD_CEMENT
    if re.search(r"plastov|barel", key):
        return Material.PLASTIC
    if "dřevěn" in key:
        return Material.WOOD
    return None


PREVIOUS_NAMES = re.compile(
    r"bývalá (\w+)|staré číslo (\w+)|^stara? (\w+) nově|^stara (\w+)$"
    r"|původně zaznačena jako (\w+)|místo staré (\w+)|^stara? budka č\.? ?(\w+)$"
    r"|^náhrada č\.? ?(\w+)$",
    re.IGNORECASE,
)

# What a box note may say that the box's fields or its checks already hold:
# material, a type the old record names too, opening, a replacement year, a
# previous name, and that it was found or measured once
RECORDED = re.compile(
    r"dřevocement\w*|dřevěn\w*|plastov\w*|barel\w*|sýkorník\w*|\bsov[ay]\b"
    r"|přední|horní|vrchní|otv[íi][rř]\w*|otevírání|nahoře|shora|nemá"
    r"|v[yý]měn\w*|za novou|\b20\d\d\b|\d{1,2}\.\s?\d{1,2}\.\s?\d{4}"
    r"|nově|nalezen\w*|zaměřen\w*|\b(pro|z|a|budka)\b|[\s,.\-/]"
)


def is_recorded(note):
    """Nothing in the note that a volunteer would miss once its values are in the box's fields."""
    key = normalized(note)
    names_opening = re.search(r"přední|horní|vrchní|otv[íi][rř]|otevír", key)
    if names_opening and opening(note) is None:
        return False
    return bool(key) and not RECORDED.sub("", PREVIOUS_NAMES.sub("", key))


def previous_names(note):
    return [
        next(group for group in match.groups() if group)
        for match in PREVIOUS_NAMES.finditer(normalized(note))
    ]
