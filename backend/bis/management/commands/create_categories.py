import zoneinfo
from datetime import datetime

from bis.cache import invalidate_cache
from bis.models import Location
from categories.models import (
    AdministrationUnitCategory,
    DietCategory,
    DonationSourceCategory,
    DonorEventCategory,
    EventCategory,
    EventGroupCategory,
    EventIntendedForCategory,
    EventProgramCategory,
    EventTag,
    GrantCategory,
    HealthInsuranceCompany,
    LocationAccessibilityCategory,
    LocationProgramCategory,
    MembershipCategory,
    OpportunityCategory,
    OpportunityPriority,
    OrganizerRoleCategory,
    PronounCategory,
    QualificationCategory,
    RoleCategory,
    TeamRoleCategory,
)
from cookbook_categories.models import (
    Allergen,
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.core.management.base import BaseCommand
from donations.models import FundraisingCampaign
from game_book_categories.models import (
    GameLengthCategory,
    LocationCategory,
    MaterialRequirementCategory,
    MentalCategory,
    OrganizersNumberCategory,
    ParticipantAgeCategory,
    ParticipantNumberCategory,
    PhysicalCategory,
    PreparationLengthCategory,
    Tag,
)
from other.models import DonationPointsAggregation
from translation.translate import _

_CATEGORIES_ACTIVATION = datetime(
    2026, 4, 23, 12, 30, tzinfo=zoneinfo.ZoneInfo("Europe/Prague")
)


class Command(BaseCommand):
    help = "Creates categories etc."

    def update_categories(self, model, data, **shared):
        has_order = any(f.name == "order" for f in model._meta.fields)
        for i, (slug, defaults) in enumerate(data.items()):
            merged = {**defaults, **shared}
            if has_order:
                merged.setdefault("order", i)
            model.objects.update_or_create(slug=slug, defaults=merged)

    def create_event_categories(self, data, prefix="", name_prefix=""):
        is_active = (
            datetime.now(zoneinfo.ZoneInfo("Europe/Prague")) < _CATEGORIES_ACTIVATION
        )
        if len(prefix):
            prefix += "__"
        if len(name_prefix):
            name_prefix += " - "

        for key, value in data.items():
            slug = prefix + key
            name = name_prefix + _(f"event_categories.{slug}")
            if isinstance(value, int):
                EventCategory.objects.update_or_create(
                    slug=slug,
                    defaults=dict(name=name, order=value + 100, is_active=is_active),
                )
            else:
                self.create_event_categories(value, slug, name)

    def add_arguments(self, parser):
        parser.add_argument(
            "--group",
            choices=["bis", "game_book", "cookbook"],
            help="Single category group to create. Default: all. "
            "`testing_db cookbook` passes --group cookbook to keep the "
            "cypress seed fast.",
        )

    def handle(self, *args, group=None, **options):
        if group is None or group == "bis":
            self.create_bis_categories()
            invalidate_cache("categories")
        if group is None or group == "game_book":
            self.create_game_book_categories()
        if group is None or group == "cookbook":
            self.create_cookbook_categories()
            invalidate_cache("cookbook_categories")

    def create_bis_categories(self):
        self.update_categories(
            DietCategory,
            {
                "meat": dict(name="s masem"),
                "vege": dict(name="vegetariánská"),
                "vegan": dict(name="veganská"),
            },
        )

        self.update_categories(
            EventIntendedForCategory,
            {
                "for_all": dict(name="pro všechny"),
                "for_young_and_adult": dict(name="pro mládež a dospělé"),
                "for_kids": dict(name="pro děti"),
                "for_parents_with_kids": dict(name="pro rodiče s dětmi"),
                "for_first_time_participant": dict(name="pro prvoúčastníky"),
            },
        )

        self.update_categories(
            QualificationCategory,
            {
                "consultant": dict(name="Konzultant"),
                "instructor": dict(name="Instruktor"),
                "organizer": dict(name="Organizátor (OHB)"),
                "weekend_organizer": dict(name="Organizátor víkendovek (OvHB)"),
                "consultant_for_kids": dict(name="Konzultant Brďo"),
                "kids_leader": dict(name="Vedoucí Brďo"),
                "kids_intern": dict(name="Praktikant Brďo"),
                "main_leader_of_kids_camps": dict(
                    name="Hlavní vedoucí dětských táborů (HVDT)"
                ),
                "main_leader_of_recovery_events": dict(
                    name="Hlavní vedoucí zotavovacích akcí (HVZA)"
                ),
                "organizer_without_education": dict(
                    name="Organizátorský přístup do BISu"
                ),
            },
        )

        qualification_parents = {
            "instructor": ["consultant"],
            "organizer": ["instructor"],
            "weekend_organizer": ["organizer"],
            "kids_leader": ["consultant_for_kids"],
            "kids_intern": ["kids_leader"],
            "organizer_without_education": ["weekend_organizer", "kids_intern"],
        }
        for slug, parent_slugs in qualification_parents.items():
            QualificationCategory.objects.get(slug=slug).parents.set(
                [
                    QualificationCategory.objects.get(slug=parent_slug)
                    for parent_slug in parent_slugs
                ]
            )

        qualification_can_approve = {
            "instructor": ["main_leader_of_kids_camps", "weekend_organizer"],
            "consultant": ["organizer"],
            "consultant_for_kids": [
                "main_leader_of_kids_camps",
                "kids_leader",
                "kids_intern",
            ],
        }
        for slug, can_approve_slugs in qualification_can_approve.items():
            QualificationCategory.objects.get(slug=slug).can_approve.set(
                [
                    QualificationCategory.objects.get(slug=can_approve_slug)
                    for can_approve_slug in can_approve_slugs
                ]
            )

        self.update_categories(
            AdministrationUnitCategory,
            {
                "basic_section": dict(name="Základní článek"),
                "headquarter": dict(name="Ústředí"),
                "regional_center": dict(name="Regionální centrum"),
                "club": dict(name="Klub"),
            },
        )

        self.update_categories(
            MembershipCategory,
            {
                "family": dict(name="první rodinný člen"),
                "family_member": dict(name="další rodinný člen"),
                "kid": dict(name="dětské do 15 let"),
                "student": dict(name="individuální 15-26 let"),
                "adult": dict(name="individuální nad 26 let"),
                "member_elsewhere": dict(name="platil v jiném ZČ"),
            },
        )

        self.update_categories(
            EventGroupCategory,
            {
                "camp": dict(name="Tábor"),
                "weekend_event": dict(name="Víkendovka (Brďo schůzka)"),
                "other": dict(name="Jednodenní (bez adresáře)"),
            },
        )

        self.update_categories(
            EventProgramCategory,
            {
                "monuments": dict(email="pamatky@brontosaurus.cz", name="Akce památky"),
                "nature": dict(
                    email="akce-priroda@brontosaurus.cz", name="Akce příroda"
                ),
                "kids": dict(email="sekce.brdo@brontosaurus.cz", name="BRĎO"),
                "eco_tent": dict(email="ekostan@brontosaurus.cz", name="Ekostan"),
                "holidays_with_brontosaurus": dict(
                    email="psb@brontosaurus.cz",
                    name="PsB (Prázdniny s Brontosaurem = vícedenní letní akce)",
                ),
                "education": dict(
                    email="vzdelavani@brontosaurus.cz", name="Vzdělávání"
                ),
                "international": dict(
                    email="international@brontosaurus.cz", name="Mezinárodní"
                ),
                "none": dict(email="hnuti@brontosaurus.cz", name="Žádný"),
            },
        )

        event_categories = {
            "internal": {
                "general_meeting": 14,
                "volunteer_meeting": 13,
                "section_meeting": 2,
            },
            "public": {
                "volunteering": 0,
                "only_experiential": 1,
                "educational": {
                    "lecture": 5,
                    "course": 6,
                    "ohb": 7,
                    "educational": 8,
                    "educational_with_stay": 9,
                },
                "club": {
                    "lecture": 4,
                    "meeting": 3,
                },
                "other": {
                    "for_public": 10,
                    "exhibition": 12,
                    "eco_tent": 11,
                },
            },
        }

        self.create_event_categories(event_categories)

        event_categories = {
            "volunteering": {
                "name": "dobrovolnická akce",
                "description": "Akce, kde byla dobrovolnická činnost bez ohledu na její rozsah. Zahrnuje i Brďo výpravy a tábory s dobrovolnickou prací. (pravidelné oddílové schůzky mají vlastní typ akce).",
            },
            "section_meeting": {
                "name": "pravidelné oddílové schůzky",
                "description": "pravidelná dětská oddílová činnost BRĎO",
            },
            "internal": {
                "name": "interní akce",
                "description": "plánovačky, valné hromady článků, setkávání organizátorů - setkání bez programu a dobrovolnické činnosti",
            },
            "experiential": {
                "name": "zážitková akce",
                "description": "Akce zcela bez dobrovolnické činnosti. Kluby se zážitkovým programem (např. deskovky, háčkování…). Brďo výpravy a tábory bez dobrovolnické práce (pravidelné oddílové schůzky mají vlastní typ akce)",
            },
            "public_educational": {
                "name": "vzdělávací pro veřejnost",
                "description": "zaměřené na různá témata např. environmentální vzdělávání, péče o přírodu a památky - zahrnuje přednášky, workshopy, promítání, kluby nebo semináře, semináře Akce Příroda např. typu OSF",
            },
            "internal_educational": {
                "name": "vzdělávací pro organizátory HB",
                "description": "malá OHB, BRĎO kurzy, rozvoj organizátorských dovedností, vzdělávání pro ústředí",
            },
            "internal_educational_full": {
                "name": "OHB, Cestičky",
                "description": "",
            },
            "evp": {
                "name": "výukový program (EVP)",
                "description": "pouze Environmentální vzdělávací přednášky EVP",
            },
            "presentation": {
                "name": "prezentační akce",
                "description": "Ekostany, výstavy pro veřejnost",
            },
        }
        is_active = (
            datetime.now(zoneinfo.ZoneInfo("Europe/Prague")) >= _CATEGORIES_ACTIVATION
        )
        self.update_categories(EventCategory, event_categories, is_active=is_active)

        self.update_categories(
            EventTag,
            {
                "retro_event": dict(
                    name="Retro akce",
                    description="Historické úspěné akce, které chceme ve výročním roce zopakovat, připomenout či obnovit. Akce týmů, které již neorganizují, ale rádi by se ve výročí 50 let HB zase sešli a něco spolu udělali. Zkrátka retro akce.",
                    is_active=False,
                ),
                "region_event": dict(
                    name="Akce Brontosarus",
                    description="Dobrovolnické akce, jež mají za cíl udělat kus užitečné práce pro přírodu, krajinu či památky a zároveň dobrovolnicví představit veřejnosti a oslovit lidi k zapojení. Akce mohou také prezentovat činnost Brontosaura v daném regionu. Typicky půjde o půldenní, jednodenní, max. víkendové akce konané v dubnu.",
                ),
            },
        )

        self.update_categories(
            GrantCategory,
            {
                "msmt": dict(name="mšmt"),
                "other": dict(name="z jiných projektů"),
            },
        )

        DonationSourceCategory.objects.update_or_create(
            slug="bank_transfer", defaults=dict(name="bankovním převodem")
        )

        self.update_categories(
            OrganizerRoleCategory,
            {
                "program": dict(name="Tvorba a vedení her"),
                "material": dict(name="Materiálně-technické zajištění"),
                "cook": dict(name="Kuchař/ka"),
                "photo": dict(name="Fotograf/ka"),
                "propagation": dict(name="Propagace akcí"),
                "communication": dict(name="Komunikace s účastníky/lektory/lokalitou"),
                "manager": dict(name="Hospodář/ka"),
                "medic": dict(name="Zdravotník/ce"),
                "singer": dict(name="Hudebník/ce"),
                "generic": dict(name="Všeuměl / podržtaška"),
            },
        )

        self.update_categories(
            TeamRoleCategory,
            {
                "lector": dict(name="Lektor"),
                "lecturer": dict(name="Přednášející"),
                "graphic": dict(name="Grafik"),
                "translator": dict(name="Překladatel"),
                "copywriter": dict(name="Copywriter"),
                "marketing": dict(name="Markeťák"),
                "web": dict(name="Webař"),
                "manager": dict(name="Hospodář"),
            },
        )

        self.update_categories(
            OpportunityCategory,
            {
                "organizing": dict(
                    name="Organizování akcí",
                    description="Příležitosti organizovat či pomáhat s pořádáním našich akcí.",
                ),
                "collaboration": dict(
                    name="Spolupráce",
                    description="Příležitosti ke spolupráci na chodu a rozvoji Hnutí Brontosaurus.",
                ),
                "location_help": dict(
                    name="Pomoc lokalitě",
                    description="Příležitosti k pomoci dané lokalitě, která to aktuálně potřebuje.",
                ),
            },
        )

        self.update_categories(
            OpportunityPriority,
            {
                "highest": dict(name="Nejvyšší"),
                "high": dict(name="Vysoká"),
                "normal": dict(name="Normální"),
                "low": dict(name="Nízká"),
                "lowest": dict(name="Nejnižší"),
            },
        )

        self.update_categories(
            LocationProgramCategory,
            {
                "nature": dict(name="AP - Akce příroda"),
                "monuments": dict(name="APAM - Akce památky"),
            },
        )

        self.update_categories(
            LocationAccessibilityCategory,
            {
                "good": dict(name="Snadná (0-1,5h)"),
                "ok": dict(name="Středně obtížná (1,5-3h)"),
                "bad": dict(name="Obtížná (více než 3h)"),
            },
        )

        self.update_categories(
            RoleCategory,
            {
                "director": dict(name="Ředitel"),
                "admin": dict(name="Admin"),
                "office_worker": dict(name="Ústředí"),
                "auditor": dict(name="KRK"),
                "executive": dict(name="VV"),
                "education_member": dict(name="EDU"),
                "chairman": dict(name="Předseda"),
                "vice_chairman": dict(name="Místopředseda"),
                "manager": dict(name="Hospodář"),
                "board_member": dict(name="Člen představenstva"),
                "main_organizer": dict(name="Hlavní organizátor"),
                "organizer": dict(name="Organizátor"),
                "qualified_organizer": dict(name="Organizátor s kvalifikací"),
                "any": dict(name="Kdokoli"),
                "fundraiser": dict(name="Fundraiser"),
            },
        )

        self.update_categories(
            HealthInsuranceCompany,
            {
                "VZP": dict(name="Všeobecná zdravotní pojišťovna České republiky"),
                "VOZP": dict(name="Vojenská zdravotní pojišťovna České republiky"),
                "CPZP": dict(name="Česká průmyslová zdravotní pojišťovna"),
                "OZP": dict(
                    name="Oborová zdravotní pojišťovna zaměstnanců bank, pojišťoven a stavebnictví"
                ),
                "ZPS": dict(name="Zaměstnanecká pojišťovna Škoda"),
                "ZPMV": dict(
                    name="Zdravotní pojišťovna ministerstva vnitra České republiky"
                ),
                "RBP": dict(name="RBP, zdravotní pojišťovna"),
            },
        )

        self.update_categories(
            PronounCategory,
            {
                "woman": dict(name="Ona/její"),
                "man": dict(name="On/jeho"),
                "other": dict(name="Jiné"),
                "unknown": dict(name="Nechci uvádět"),
            },
        )

        Location.objects.update_or_create(
            name="Online",
            defaults=dict(
                for_beginners=True,
                accessibility_from_prague=LocationAccessibilityCategory.objects.get(
                    slug="good"
                ),
                accessibility_from_brno=LocationAccessibilityCategory.objects.get(
                    slug="good"
                ),
            ),
        )

        self.update_categories(
            DonationPointsAggregation,
            {
                "clubs": dict(
                    name="Kluby",
                    description="počet akcí, které mají program: vzdělávací - přednáška, klub - přednáška, klub - setkání",
                ),
                "other_without_clubs": dict(
                    name="Jednodenní bez klubů",
                    description="počet akcí druhu jednodenní bez klubů",
                ),
                "weekend_events": dict(
                    name="Víkendovky", description="počet akcí druhu víkendovka"
                ),
                "camps": dict(name="Tábory", description="počet akcí druhu tábory"),
                "50_worked_hours": dict(
                    name="Odpracováno 50 člověkohodin",
                    description="bod za každých 50 odpracovaných člověkohodin",
                ),
                "members_0_15": dict(
                    name="Členi 0-15 let", description="počet členů 0-15 let"
                ),
                "members_16_18": dict(
                    name="Členi 16-18 let", description="počet členů 16-18 let"
                ),
                "members_19_26": dict(
                    name="Členi 19-26 let", description="počet členů 19-26 let"
                ),
                "members_27_and_more": dict(
                    name="Členi 27+ let", description="počet členů 27+ let"
                ),
                "supporting_donations": dict(
                    name="Podpora ZČ",
                    description="Celková suma dotací, jejiž procento má být přislíbeno danému ZČ",
                ),
                "supporting_donations_rc": dict(
                    name="Podpora RC",
                    description="Celková suma dotací, jejiž procento má být přislíbeno danému RC",
                ),
            },
        )

        self.update_categories(
            DonorEventCategory,
            {
                "new_recurrent_pledge": dict(
                    description="Nový pravidelný dárce v Darujme"
                ),
                "recurrent_stopped": dict(
                    description="Podruhé za sebou nepřišla platba od pravidelného dárce."
                ),
                "pledge_1y": dict(description="Pravidelný dárce daruje již 1 rok."),
                "pledge_2y": dict(description="Pravidelný dárce daruje již 2 roky."),
                "pledge_3y": dict(description="Pravidelný dárce daruje již 3 roky."),
                "pledge_4y": dict(description="Pravidelný dárce daruje již 4 roky."),
                "pledge_5y": dict(description="Pravidelný dárce daruje již 5 let."),
                "donor_10k_total": dict(
                    description="Součet všech darů od jednoho dárce přesáhl 10 000 Kč."
                ),
                "added_to_campaign": dict(
                    description="Přidán do fundraisingové kampaně"
                ),
                "call_no_answer": dict(description="Volání — nezvedl"),
                "call_postponed": dict(description="Volání — odloženo"),
                "call_reached": dict(description="Volání — odvoláno"),
            },
        )

        FundraisingCampaign.objects.update_or_create(
            slug="automatic_emails",
            defaults=dict(name="Automatické e-maily"),
        )

    def create_game_book_categories(self):
        # good emoji overview at https://www.piliapp.com/emoji/list/
        self.update_categories(
            Tag,
            {
                "icebreaker": dict(
                    emoji="🧊",
                    name="icebreaker",
                    description="Prolomení nervozity, uvolnění účastníků, tvoření skupiny z jednotlivců",
                ),
                "meet": dict(emoji="🤝", name="seznamka", description=""),
                "dynamix": dict(emoji="🌪", name="dynamix", description=""),
                "trust": dict(
                    emoji="🙏",
                    name="důvěrovka",
                    description="Buduje či rozvíjí důvěru mezi účastníky",
                ),
                "simul": dict(
                    emoji="🎮",
                    name="simulační",
                    description="Ať běhačka či deskovka, hra simuluje reálný život",
                ),
                "strategy": dict(emoji="📈", name="strategie", description=""),
                "small": dict(
                    emoji="🐁",
                    name="drobnička",
                    description="Na výplň prostojů, jednoduchá, na uvolnění",
                ),
                "enviro": dict(
                    emoji="🌱",
                    name="enviro",
                    description="Program obsahuje smysluplnou enviro tématiku",
                ),
                "discuss": dict(emoji="🗣", name="diskuzní", description=""),
                "orvo": dict(
                    emoji="🤕",
                    name="orvo",
                    description="Oblečení nemusí zůstat v původním stavu",
                ),
                "larp": dict(emoji="🎭", name="larp", description=""),
                "team-building": dict(emoji="🪜", name="team building", description=""),
                "creative": dict(emoji="🎨", name="kreativní", description=""),
                "vrchol": dict(
                    emoji="🤬",
                    name="vrcholovka",
                    description="Vrchol akce, ať fyzický, psychický či atmosférický",
                ),
                "reflexe": dict(
                    emoji="🔎",
                    name="reflexe",
                    description="Metodika pro vedení reflexe programu",
                ),
                "night": dict(emoji="🌙", name="noční", description=""),
                "atmo": dict(
                    emoji="🎆",
                    name="s atmoškou",
                    description="Programy tvořící atmosféru",
                ),
                "cipher": dict(emoji="📝", name="šifrovačka", description=""),
                "warm-up": dict(
                    emoji="🤸", name="rozcvička", description="Hodí se po ránu"
                ),
                "tutorial": dict(
                    emoji="🔨",
                    name="návod",
                    description="Jak zasadit, vyrobit, zpracovat, vytvořit...",
                ),
            },
        )

        self.update_categories(
            PhysicalCategory,
            {
                "minimal": dict(
                    emoji="🧘",
                    name="Na místě",
                    description="Programy sedící či s minimem pohybu mezi účasníky",
                ),
                "moving": dict(
                    emoji="🚶",
                    name="Chodící",
                    description="Během programu něco nachodím, zahřeji se, ale nezpotím",
                ),
                "running": dict(
                    emoji="🏃",
                    name="Běhací",
                    description="Unavím se, ale nezničím se",
                ),
                "hardcore": dict(
                    emoji="🏋",
                    name="Náročný",
                    description="Po skončení někam odpadnu",
                ),
            },
        )

        self.update_categories(
            MentalCategory,
            {
                "minimal": dict(
                    emoji="😌",
                    name="Nenáročný",
                    description="Odpočinkové programy, u kterých můžu vypnout hlavu",
                ),
                "thinking": dict(
                    emoji="🤔",
                    name="Mozek potřeba",
                    description="Trochu kreativity to chce, ale nic náročného",
                ),
                "logically_demanding": dict(
                    emoji="📈",
                    name="Analyticky náročný",
                    description="Plánování strategie, řešení šifer, komunikace v časovém presu",
                ),
                "emotionally_demanding": dict(
                    emoji="💔",
                    name="Emočně náročný",
                    description="Přemýšlecí otázky, řešení hodnot, pocitů, sdílení",
                ),
                "hardcore": dict(
                    emoji="🤬",
                    name="Psycho",
                    description="Fyzicky i psychicky náročný, narušování komforní zóny, nutnost řešit psychickou bezpečnost",
                ),
            },
        )

        self.update_categories(
            LocationCategory,
            {
                "tearoom": dict(
                    emoji="🫖",
                    name="Čajovna",
                    description="Klidné a komfortní místo s hezkou atmosférou, omezené množství pohybu",
                ),
                "hall": dict(
                    emoji="🏠",
                    name="Větší místnost",
                    description="Sál či místnost dostatkem prostoru, relativní teplo",
                ),
                "in_a_circle": dict(
                    emoji="🔥",
                    name="V kruhu (kolem ohně)",
                    description="Všichi na sebe vidí, tepelný komfort, omezený pohyb",
                ),
                "field": dict(
                    emoji="🌿",
                    name="Louka",
                    description="Louka či park, dost prostoru na sezení či běhání",
                ),
                "forest": dict(
                    emoji="🌲", name="Les", description="Kousek lesa se stromy"
                ),
                "village": dict(
                    emoji="🏘",
                    name="Vesnice",
                    description="Či město, výskyt lidí v okolí",
                ),
                "water": dict(
                    emoji="💧",
                    name="Voda",
                    description="Nutno větší množství vody, na koupání či čvachtání",
                ),
                "at_road": dict(
                    emoji="🛣",
                    name="K cestě",
                    description="Možno hrát během putování či přesunu",
                ),
                "specific": dict(
                    emoji="❓",
                    name="Specifické umístění",
                    description="K programu třeba specifické místo (ať konkrétní či zřídké)",
                ),
            },
        )

        self.update_categories(
            ParticipantNumberCategory,
            {
                "individual": dict(
                    emoji="🚲",
                    name="Pro jednotlivce",
                    description="Každý hraje sám, lib. množství účastníků",
                ),
                "small": dict(
                    emoji="🚗",
                    name="Malá skupinka (4-6)",
                    description="Skupinka 4-6 lidí",
                ),
                "few": dict(
                    emoji="🚐",
                    name="Skupina lidí (10+)",
                    description="Zepár lidí, přes 10",
                ),
                "big": dict(
                    emoji="🚌",
                    name="Větší skupina (20+)",
                    description="Kolem 20 lidí",
                ),
                "a_log": dict(
                    emoji="🚢",
                    name="Hromada lidí",
                    description="Pro velká skupiny lidí",
                ),
            },
        )

        self.update_categories(
            ParticipantAgeCategory,
            {
                "parents_with_kids": dict(
                    emoji="👪", name="Rodiče s dětmi", description=""
                ),
                "preschool": dict(emoji="👶", name="Předškoláci", description=""),
                "elementary": dict(emoji="🧒", name="Školáci", description=""),
                "teen": dict(emoji="🧑", name="Středoškoláci", description=""),
                "university": dict(emoji="🧑‍🎓", name="Vysokoškoláci", description=""),
                "adult": dict(emoji="🧑‍💼", name="Dospělí", description=""),
                "old": dict(emoji="🧓", name="Vyspělí", description=""),
            },
        )

        self.update_categories(
            GameLengthCategory,
            {
                "short": dict(
                    emoji="⚡",
                    name="Rychlý (do 10 minut)",
                    description="Krátké programy, jednuché seznamky, rozcvičky, pro vyplnění prostoje",
                ),
                "an_hour": dict(
                    emoji="🕐",
                    name="Středně dlouhý (do hodiny)",
                    description="Nějakou chvíli účastníky zabaví, dvě tři takové naplní odpoledne",
                ),
                "long": dict(
                    emoji="🕓",
                    name="Dlouhý (pár hodin)",
                    description="Odpolední program, noční hra",
                ),
                "multiple_days": dict(
                    emoji="📅",
                    name="Vícedenní, celotáborový",
                    description="Program rozprostřený přes několik dní, většinou na pozadí jiných programů",
                ),
            },
        )

        self.update_categories(
            PreparationLengthCategory,
            {
                "enough_to_read": dict(
                    emoji="⚡",
                    name="Stačí přečíst pravidla",
                    description="Zkušený org přečte, a program rovnou uvede",
                ),
                "need_to_study": dict(
                    emoji="🧘",
                    name="Třeba chvíle klidu",
                    description="Netriviální, potřeba pořádně přečíst a pochopit",
                ),
                "training": dict(
                    emoji="🖨",
                    name="Potřeba se připravit",
                    description="Příprava zabere pár hodin, chystání materiálů, předání dalším orgům",
                ),
                "multiple_sessions": dict(
                    emoji="📅",
                    name="Náročná příprava",
                    description="Rozsáhle rozpracovaný či naopak nedokončený program, nutno věnovat značné úsilí k uvedení",
                ),
            },
        )

        self.update_categories(
            OrganizersNumberCategory,
            {
                "one": dict(
                    emoji="🧍",
                    name="Zvládnu sám",
                    description="Uvedení programu zvládne jeden org",
                ),
                "few": dict(
                    emoji="🤝",
                    name="Potřebuji pomocnou ruku",
                    description="Na program je potřeba dva či tři orgové",
                ),
                "group": dict(
                    emoji="👪",
                    name="Skupinka orgů",
                    description="Potřeba kolem pěti orgů",
                ),
                "a_lot": dict(
                    emoji="🌍",
                    name="Spousta orgů",
                    description="Velké hry vyžadující B-tým, atp.",
                ),
            },
        )

        self.update_categories(
            MaterialRequirementCategory,
            {
                "none": dict(
                    emoji="🚫",
                    name="Nic není potřeba",
                    description="Stačí účastníci",
                ),
                "simple": dict(
                    emoji="✏",
                    name="Stačí základ",
                    description="Šátky, tužka a papír, provázek",
                ),
                "get_some": dict(
                    emoji="🖨",
                    name="Potřeba nachystat",
                    description="Tisk pár stránek, kostým, potřeba specifický materiál k programu",
                ),
                "complicated": dict(
                    emoji="🚚",
                    name="Kdo se s tím potáhne?",
                    description="Velké množství či velmi specifický materiál",
                ),
            },
        )

    def create_cookbook_categories(self):
        self.update_categories(
            RecipeDifficulty,
            {
                "trivial": dict(name="triviální"),
                "simple": dict(name="jednoduchá"),
                "medium": dict(name="střední"),
                "hard": dict(name="složitá"),
            },
        )

        self.update_categories(
            RecipeRequiredTime,
            {
                "instant": dict(name="instantní"),
                "fast": dict(name="rychlé"),
                "normal": dict(name="normální"),
                "long": dict(name="maraton"),
            },
        )

        tags = {
            "Chody": [
                ("breakfast", "snídaně"),
                ("soup", "polévka"),
                ("main_dish", "hlavní jídlo"),
                ("side", "příloha"),
                ("snack", "svačina"),
                ("to_taste", "na chuť"),
                ("drink", "nápoj"),
            ],
            "Typy": [
                ("spread", "pomazánka"),
                ("pastry", "pečivo"),
                ("burger", "burger"),
                ("salad", "salát"),
                ("porridge", "kaše"),
                ("dip", "dip"),
                ("sandwiches", "sendviče"),
            ],
            "Dezerty": [
                ("cake", "dort"),
                ("bun", "buchta"),
                ("candy", "cukroví"),
            ],
            "Speciální": [
                ("on_hike", "na čundr"),
                ("one_pot", "v jednom hrnci"),
            ],
            "Postižení": [
                ("gluten_free", "bez lepku"),
                ("low_legumes", "málo luštěnin"),
                ("dia", "dia"),
                ("no_soya", "bez sóji"),
            ],
            "Dle složení": [
                ("with_meat", "s masem*"),
                ("dairy", "mléčné*"),
                ("cheese", "sýrové*"),
                ("egg", "vaječné*"),
                ("vegetables", "zeleninové"),
                ("legumes", "luštěninové"),
                ("cereals", "obilninové"),
                ("fruit", "ovocné"),
            ],
            "Kuchyně": [
                ("czech", "česká"),
                ("indi", "indická"),
                ("asian", "asijská"),
            ],
        }
        self.update_categories(
            RecipeTag,
            {
                slug: dict(name=name, group=group)
                for group, items in tags.items()
                for slug, name in items
            },
        )

        units = [
            ("grams", "g", "gram", "gramy", "gramů", "weight"),
            ("kilograms", "kg", "kilogram", "kilogramy", "kilogramů", "weight"),
            ("milliliter", "ml", "mililitr", "mililitry", "mililitrů", "volume"),
            ("liter", "l", "litr", "litry", "litrů", "volume"),
            ("pinch", "", "špetka", "špetky", "špetek", "volume"),
            ("teaspoon", "", "lžička", "lžičky", "lžiček", "volume"),
            ("tablespoon", "", "lžíce", "lžíce", "lžic", "volume"),
            ("handful", "", "hrst", "hrsti", "hrstí", "volume"),
            ("cup", "", "hrnek", "hrnky", "hrnků", "volume"),
            ("serving", "", "porce", "porce", "porcí", "servings"),
            ("piece", "ks", "kus", "kusy", "kusů", "pieces"),
            ("clove", "", "stroužek", "stroužky", "stroužků", "pieces"),
            ("bulb", "", "palička", "paličky", "paliček", "pieces"),
            # ("bread", "", "šumava", "šumavy", "šumav", "weight"),
        ]
        self.update_categories(
            Unit,
            {
                slug: dict(
                    name=name,
                    name2=name2,
                    name5=name5,
                    abbreviation=abbreviation,
                    of=of,
                )
                for slug, abbreviation, name, name2, name5, of in units
            },
        )

        self.update_categories(
            Allergen,
            {
                "gluten": dict(name="lepek"),
                "soya": dict(name="sója"),
                "nuts": dict(name="oříšky"),
            },
        )
