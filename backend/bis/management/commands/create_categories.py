import zoneinfo
from datetime import datetime

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
    RecipeDifficulty,
    RecipeRequiredTime,
    RecipeTag,
    Unit,
)
from django.core.management.base import BaseCommand
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
        if group is None or group == "game_book":
            self.create_game_book_categories()
        if group is None or group == "cookbook":
            self.create_cookbook_categories()

    def create_bis_categories(self):
        DietCategory.objects.update_or_create(
            slug="meat", defaults=dict(name="s masem")
        )
        DietCategory.objects.update_or_create(
            slug="vege", defaults=dict(name="vegetariánská")
        )
        DietCategory.objects.update_or_create(
            slug="vegan", defaults=dict(name="veganská")
        )

        EventIntendedForCategory.objects.update_or_create(
            slug="for_all", defaults=dict(name="pro všechny")
        )
        EventIntendedForCategory.objects.update_or_create(
            slug="for_young_and_adult", defaults=dict(name="pro mládež a dospělé")
        )
        EventIntendedForCategory.objects.update_or_create(
            slug="for_kids", defaults=dict(name="pro děti")
        )
        EventIntendedForCategory.objects.update_or_create(
            slug="for_parents_with_kids", defaults=dict(name="pro rodiče s dětmi")
        )
        EventIntendedForCategory.objects.update_or_create(
            slug="for_first_time_participant", defaults=dict(name="pro prvoúčastníky")
        )

        QualificationCategory.objects.update_or_create(
            slug="consultant", defaults=dict(name="Konzultant")
        )
        QualificationCategory.objects.update_or_create(
            slug="instructor", defaults=dict(name="Instruktor")
        )
        QualificationCategory.objects.update_or_create(
            slug="organizer", defaults=dict(name="Organizátor (OHB)")
        )
        QualificationCategory.objects.update_or_create(
            slug="weekend_organizer",
            defaults=dict(name="Organizátor víkendovek (OvHB)"),
        )
        QualificationCategory.objects.update_or_create(
            slug="consultant_for_kids", defaults=dict(name="Konzultant Brďo")
        )
        QualificationCategory.objects.update_or_create(
            slug="kids_leader", defaults=dict(name="Vedoucí Brďo")
        )
        QualificationCategory.objects.update_or_create(
            slug="kids_intern", defaults=dict(name="Praktikant Brďo")
        )
        QualificationCategory.objects.update_or_create(
            slug="main_leader_of_kids_camps",
            defaults=dict(name="Hlavní vedoucí dětských táborů (HVDT)"),
        )
        QualificationCategory.objects.update_or_create(
            slug="main_leader_of_recovery_events",
            defaults=dict(name="Hlavní vedoucí zotavovacích akcí (HVZA)"),
        )
        QualificationCategory.objects.update_or_create(
            slug="organizer_without_education",
            defaults=dict(name="Organizátorský přístup do BISu"),
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

        AdministrationUnitCategory.objects.update_or_create(
            slug="basic_section", defaults=dict(name="Základní článek")
        )
        AdministrationUnitCategory.objects.update_or_create(
            slug="headquarter", defaults=dict(name="Ústředí")
        )
        AdministrationUnitCategory.objects.update_or_create(
            slug="regional_center", defaults=dict(name="Regionální centrum")
        )
        AdministrationUnitCategory.objects.update_or_create(
            slug="club", defaults=dict(name="Klub")
        )

        MembershipCategory.objects.update_or_create(
            slug="family", defaults=dict(name="první rodinný člen")
        )
        MembershipCategory.objects.update_or_create(
            slug="family_member", defaults=dict(name="další rodinný člen")
        )
        MembershipCategory.objects.update_or_create(
            slug="kid", defaults=dict(name="dětské do 15 let")
        )
        MembershipCategory.objects.update_or_create(
            slug="student", defaults=dict(name="individuální 15-26 let")
        )
        MembershipCategory.objects.update_or_create(
            slug="adult", defaults=dict(name="individuální nad 26 let")
        )
        MembershipCategory.objects.update_or_create(
            slug="member_elsewhere", defaults=dict(name="platil v jiném ZČ")
        )

        EventGroupCategory.objects.update_or_create(
            slug="camp", defaults=dict(name="Tábor")
        )
        EventGroupCategory.objects.update_or_create(
            slug="weekend_event", defaults=dict(name="Víkendovka (Brďo schůzka)")
        )
        EventGroupCategory.objects.update_or_create(
            slug="other", defaults=dict(name="Jednodenní (bez adresáře)")
        )

        EventProgramCategory.objects.update_or_create(
            slug="monuments",
            defaults=dict(email="pamatky@brontosaurus.cz", name="Akce památky"),
        )
        EventProgramCategory.objects.update_or_create(
            slug="nature",
            defaults=dict(email="akce-priroda@brontosaurus.cz", name="Akce příroda"),
        )
        EventProgramCategory.objects.update_or_create(
            slug="kids", defaults=dict(email="sekce.brdo@brontosaurus.cz", name="BRĎO")
        )
        EventProgramCategory.objects.update_or_create(
            slug="eco_tent",
            defaults=dict(email="ekostan@brontosaurus.cz", name="Ekostan"),
        )
        EventProgramCategory.objects.update_or_create(
            slug="holidays_with_brontosaurus",
            defaults=dict(
                email="psb@brontosaurus.cz",
                name="PsB (Prázdniny s Brontosaurem = vícedenní letní akce)",
            ),
        )
        EventProgramCategory.objects.update_or_create(
            slug="education",
            defaults=dict(email="vzdelavani@brontosaurus.cz", name="Vzdělávání"),
        )
        EventProgramCategory.objects.update_or_create(
            slug="international",
            defaults=dict(email="international@brontosaurus.cz", name="Mezinárodní"),
        )
        EventProgramCategory.objects.update_or_create(
            slug="none", defaults=dict(email="hnuti@brontosaurus.cz", name="Žádný")
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
                "description": "akce, kde byla dobrovolnická činnost bez ohledu na její rozsah",
            },
            "section_meeting": {
                "name": "oddílová schůzka",
                "description": "pravidelná dětská oddílová činnost BRĎO",
            },
            "section_event": {
                "name": "oddílová akce",
                "description": "BRĎO výpravy, výlety, dětské tábory",
            },
            "internal": {
                "name": "interní akce",
                "description": "plánovačky, valné hromady článků",
            },
            "experiential": {
                "name": "zážitková akce",
                "description": "akce zcela bez dobrovolnické činnosti",
            },
            "public_educational": {
                "name": "vzdělávací pro veřejnost",
                "description": "včetně vzdělávacích klubů např. klubové přednášky, workshopy, promítání na envirotémata… Vzdělávání Akce příroda např. semináře typu OSF",
            },
            "internal_educational": {
                "name": "vzdělávací pro organizátory HB",
                "description": "OHB, Cestičky, malá OHB, BRĎO kurzy, vzdělávání pro ústředí",
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
        for i, (slug, defaults) in enumerate(event_categories.items()):
            EventCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    **defaults,
                    "order": i,
                    "is_active": is_active,
                },
            )

        EventTag.objects.update_or_create(
            slug="retro_event",
            defaults=dict(
                name="Retro akce",
                description="Historické úspěné akce, které chceme ve výročním roce zopakovat, připomenout či obnovit. Akce týmů, které již neorganizují, ale rádi by se ve výročí 50 let HB zase sešli a něco spolu udělali. Zkrátka retro akce.",
            ),
        )
        EventTag.objects.update_or_create(
            slug="region_event",
            defaults=dict(
                name="Akce Brontosarus",
                description="Dobrovolnické akce, jež mají za cíl udělat kus užitečné práce pro přírodu, krajinu či památky a zároveň dobrovolnicví představit veřejnosti a oslovit lidi k zapojení. Akce mohou také prezentovat činnost Brontosaura v daném regionu. Typicky půjde o půldenní, jednodenní, max. víkendové akce konané v dubnu.",
            ),
        )

        GrantCategory.objects.update_or_create(slug="msmt", defaults=dict(name="mšmt"))
        GrantCategory.objects.update_or_create(
            slug="other", defaults=dict(name="z jiných projektů")
        )

        DonationSourceCategory.objects.update_or_create(
            slug="bank_transfer", defaults=dict(name="bankovním převodem")
        )

        OrganizerRoleCategory.objects.update_or_create(
            slug="program", defaults=dict(name="Tvorba a vedení her")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="material", defaults=dict(name="Materiálně-technické zajištění")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="cook", defaults=dict(name="Kuchař/ka")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="photo", defaults=dict(name="Fotograf/ka")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="propagation", defaults=dict(name="Propagace akcí")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="communication",
            defaults=dict(name="Komunikace s účastníky/lektory/lokalitou"),
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="manager", defaults=dict(name="Hospodář/ka")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="medic", defaults=dict(name="Zdravotník/ce")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="singer", defaults=dict(name="Hudebník/ce")
        )
        OrganizerRoleCategory.objects.update_or_create(
            slug="generic", defaults=dict(name="Všeuměl / podržtaška")
        )

        TeamRoleCategory.objects.update_or_create(
            slug="lector", defaults=dict(name="Lektor")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="lecturer", defaults=dict(name="Přednášející")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="graphic", defaults=dict(name="Grafik")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="translator", defaults=dict(name="Překladatel")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="copywriter", defaults=dict(name="Copywriter")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="marketing", defaults=dict(name="Markeťák")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="web", defaults=dict(name="Webař")
        )
        TeamRoleCategory.objects.update_or_create(
            slug="manager", defaults=dict(name="Hospodář")
        )

        OpportunityCategory.objects.update_or_create(
            slug="organizing",
            defaults=dict(
                name="Organizování akcí",
                description="Příležitosti organizovat či pomáhat s pořádáním našich akcí.",
            ),
        )
        OpportunityCategory.objects.update_or_create(
            slug="collaboration",
            defaults=dict(
                name="Spolupráce",
                description="Příležitosti ke spolupráci na chodu a rozvoji Hnutí Brontosaurus.",
            ),
        )
        OpportunityCategory.objects.update_or_create(
            slug="location_help",
            defaults=dict(
                name="Pomoc lokalitě",
                description="Příležitosti k pomoci dané lokalitě, která to aktuálně potřebuje.",
            ),
        )
        OpportunityPriority.objects.update_or_create(slug="highest", name="Nejvyšší")
        OpportunityPriority.objects.update_or_create(slug="high", name="Vysoká")
        OpportunityPriority.objects.update_or_create(slug="normal", name="Normální")
        OpportunityPriority.objects.update_or_create(slug="low", name="Nízká")
        OpportunityPriority.objects.update_or_create(slug="lowest", name="Nejnižší")

        LocationProgramCategory.objects.update_or_create(
            slug="nature", defaults=dict(name="AP - Akce příroda")
        )
        LocationProgramCategory.objects.update_or_create(
            slug="monuments", defaults=dict(name="APAM - Akce památky")
        )

        LocationAccessibilityCategory.objects.update_or_create(
            slug="good", defaults=dict(name="Snadná (0-1,5h)")
        )
        LocationAccessibilityCategory.objects.update_or_create(
            slug="ok", defaults=dict(name="Středně obtížná (1,5-3h)")
        )
        LocationAccessibilityCategory.objects.update_or_create(
            slug="bad", defaults=dict(name="Obtížná (více než 3h)")
        )

        RoleCategory.objects.update_or_create(
            slug="director", defaults=dict(name="Ředitel")
        )
        RoleCategory.objects.update_or_create(slug="admin", defaults=dict(name="Admin"))
        RoleCategory.objects.update_or_create(
            slug="office_worker", defaults=dict(name="Ústředí")
        )
        RoleCategory.objects.update_or_create(slug="auditor", defaults=dict(name="KRK"))
        RoleCategory.objects.update_or_create(
            slug="executive", defaults=dict(name="VV")
        )
        RoleCategory.objects.update_or_create(
            slug="education_member", defaults=dict(name="EDU")
        )
        RoleCategory.objects.update_or_create(
            slug="chairman", defaults=dict(name="Předseda")
        )
        RoleCategory.objects.update_or_create(
            slug="vice_chairman", defaults=dict(name="Místopředseda")
        )
        RoleCategory.objects.update_or_create(
            slug="manager", defaults=dict(name="Hospodář")
        )
        RoleCategory.objects.update_or_create(
            slug="board_member", defaults=dict(name="Člen představenstva")
        )
        RoleCategory.objects.update_or_create(
            slug="main_organizer", defaults=dict(name="Hlavní organizátor")
        )
        RoleCategory.objects.update_or_create(
            slug="organizer", defaults=dict(name="Organizátor")
        )
        RoleCategory.objects.update_or_create(
            slug="qualified_organizer", defaults=dict(name="Organizátor s kvalifikací")
        )
        RoleCategory.objects.update_or_create(slug="any", defaults=dict(name="Kdokoli"))
        RoleCategory.objects.update_or_create(
            slug="fundraiser", defaults=dict(name="Fundraiser")
        )

        HealthInsuranceCompany.objects.update_or_create(
            slug="VZP",
            defaults=dict(name="Všeobecná zdravotní pojišťovna České republiky"),
        )
        HealthInsuranceCompany.objects.update_or_create(
            slug="VOZP",
            defaults=dict(name="Vojenská zdravotní pojišťovna České republiky"),
        )
        HealthInsuranceCompany.objects.update_or_create(
            slug="CPZP", defaults=dict(name="Česká průmyslová zdravotní pojišťovna")
        )
        HealthInsuranceCompany.objects.update_or_create(
            slug="OZP",
            defaults=dict(
                name="Oborová zdravotní pojišťovna zaměstnanců bank, pojišťoven a stavebnictví"
            ),
        )
        HealthInsuranceCompany.objects.update_or_create(
            slug="ZPS", defaults=dict(name="Zaměstnanecká pojišťovna Škoda")
        )
        HealthInsuranceCompany.objects.update_or_create(
            slug="ZPMV",
            defaults=dict(
                name="Zdravotní pojišťovna ministerstva vnitra České republiky"
            ),
        )
        HealthInsuranceCompany.objects.update_or_create(
            slug="RBP", defaults=dict(name="RBP, zdravotní pojišťovna")
        )

        PronounCategory.objects.update_or_create(
            slug="woman", defaults=dict(name="Ona/její")
        )
        PronounCategory.objects.update_or_create(
            slug="man", defaults=dict(name="On/jeho")
        )
        PronounCategory.objects.update_or_create(
            slug="other", defaults=dict(name="Jiné")
        )
        PronounCategory.objects.update_or_create(
            slug="unknown", defaults=dict(name="Nechci uvádět")
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

        DonationPointsAggregation.objects.update_or_create(
            slug="clubs",
            defaults=dict(
                name="Kluby",
                description="počet akcí, které mají program: vzdělávací - přednáška, klub - přednáška, klub - setkání",
            ),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="other_without_clubs",
            defaults=dict(
                name="Jednodenní bez klubů",
                description="počet akcí druhu jednodenní bez klubů",
            ),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="weekend_events",
            defaults=dict(name="Víkendovky", description="počet akcí druhu víkendovka"),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="camps",
            defaults=dict(name="Tábory", description="počet akcí druhu tábory"),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="50_worked_hours",
            defaults=dict(
                name="Odpracováno 50 člověkohodin",
                description="bod za každých 50 odpracovaných člověkohodin",
            ),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="members_0_15",
            defaults=dict(name="Členi 0-15 let", description="počet členů 0-15 let"),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="members_16_18",
            defaults=dict(name="Členi 16-18 let", description="počet členů 16-18 let"),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="members_19_26",
            defaults=dict(name="Členi 19-26 let", description="počet členů 19-26 let"),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="members_27_and_more",
            defaults=dict(name="Členi 27+ let", description="počet členů 27+ let"),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="supporting_donations",
            defaults=dict(
                name="Podpora ZČ",
                description="Celková suma dotací, jejiž procento má být přislíbeno danému ZČ",
            ),
        )
        DonationPointsAggregation.objects.update_or_create(
            slug="supporting_donations_rc",
            defaults=dict(
                name="Podpora RC",
                description="Celková suma dotací, jejiž procento má být přislíbeno danému RC",
            ),
        )

        donor_event_categories = {
            "new_recurrent_pledge": "Nový pravidelný dárce v Darujme",
            "recurrent_stopped": "Podruhé za sebou nepřišla platba od pravidelného dárce.",
            "pledge_1y": "Pravidelný dárce daruje již 1 rok.",
            "pledge_2y": "Pravidelný dárce daruje již 2 roky.",
            "pledge_3y": "Pravidelný dárce daruje již 3 roky.",
            "pledge_4y": "Pravidelný dárce daruje již 4 roky.",
            "pledge_5y": "Pravidelný dárce daruje již 5 let.",
            "donor_10k_total": "Součet všech darů od jednoho dárce přesáhl 10 000 Kč.",
            "added_to_campaign": "Přidán do fundraisingové kampaně",
            "call_no_answer": "Volání — nezvedl",
            "call_declined": "Volání — odmítl",
            "call_postponed": "Volání — odloženo",
            "call_reached": "Volání — odvoláno",
        }
        for slug, description in donor_event_categories.items():
            DonorEventCategory.objects.update_or_create(
                slug=slug,
                defaults=dict(description=description),
            )

    def create_game_book_categories(self):
        # good emoji overview at https://www.piliapp.com/emoji/list/
        Tag.objects.update_or_create(
            slug="icebreaker",
            defaults=dict(
                emoji="🧊",
                name="icebreaker",
                description="Prolomení nervozity, uvolnění účastníků, tvoření skupiny z jednotlivců",
            ),
        )
        Tag.objects.update_or_create(
            slug="meet", defaults=dict(emoji="🤝", name="seznamka", description="")
        )
        Tag.objects.update_or_create(
            slug="dynamix", defaults=dict(emoji="🌪", name="dynamix", description="")
        )
        Tag.objects.update_or_create(
            slug="trust",
            defaults=dict(
                emoji="🙏",
                name="důvěrovka",
                description="Buduje či rozvíjí důvěru mezi účastníky",
            ),
        )
        Tag.objects.update_or_create(
            slug="simul",
            defaults=dict(
                emoji="🎮",
                name="simulační",
                description="Ať běhačka či deskovka, hra simuluje reálný život",
            ),
        )
        Tag.objects.update_or_create(
            slug="strategy", defaults=dict(emoji="📈", name="strategie", description="")
        )
        Tag.objects.update_or_create(
            slug="small",
            defaults=dict(
                emoji="🐁",
                name="drobnička",
                description="Na výplň prostojů, jednoduchá, na uvolnění",
            ),
        )
        Tag.objects.update_or_create(
            slug="enviro",
            defaults=dict(
                emoji="🌱",
                name="enviro",
                description="Program obsahuje smysluplnou enviro tématiku",
            ),
        )
        Tag.objects.update_or_create(
            slug="discuss", defaults=dict(emoji="🗣", name="diskuzní", description="")
        )
        Tag.objects.update_or_create(
            slug="orvo",
            defaults=dict(
                emoji="🤕",
                name="orvo",
                description="Oblečení nemusí zůstat v původním stavu",
            ),
        )
        Tag.objects.update_or_create(
            slug="larp", defaults=dict(emoji="🎭", name="larp", description="")
        )
        Tag.objects.update_or_create(
            slug="team-building",
            defaults=dict(emoji="🪜", name="team building", description=""),
        )
        Tag.objects.update_or_create(
            slug="creative", defaults=dict(emoji="🎨", name="kreativní", description="")
        )
        Tag.objects.update_or_create(
            slug="vrchol",
            defaults=dict(
                emoji="🤬",
                name="vrcholovka",
                description="Vrchol akce, ať fyzický, psychický či atmosférický",
            ),
        )
        Tag.objects.update_or_create(
            slug="reflexe",
            defaults=dict(
                emoji="🔎",
                name="reflexe",
                description="Metodika pro vedení reflexe programu",
            ),
        )
        Tag.objects.update_or_create(
            slug="night", defaults=dict(emoji="🌙", name="noční", description="")
        )
        Tag.objects.update_or_create(
            slug="atmo",
            defaults=dict(
                emoji="🎆", name="s atmoškou", description="Programy tvořící atmosféru"
            ),
        )
        Tag.objects.update_or_create(
            slug="cipher", defaults=dict(emoji="📝", name="šifrovačka", description="")
        )
        Tag.objects.update_or_create(
            slug="warm-up",
            defaults=dict(emoji="🤸", name="rozcvička", description="Hodí se po ránu"),
        )
        Tag.objects.update_or_create(
            slug="tutorial",
            defaults=dict(
                emoji="🔨",
                name="návod",
                description="Jak zasadit, vyrobit, zpracovat, vytvořit...",
            ),
        )

        PhysicalCategory.objects.update_or_create(
            slug="minimal",
            defaults=dict(
                emoji="🧘",
                name="Na místě",
                description="Programy sedící či s minimem pohybu mezi účasníky",
            ),
        )
        PhysicalCategory.objects.update_or_create(
            slug="moving",
            defaults=dict(
                emoji="🚶",
                name="Chodící",
                description="Během programu něco nachodím, zahřeji se, ale nezpotím",
            ),
        )
        PhysicalCategory.objects.update_or_create(
            slug="running",
            defaults=dict(
                emoji="🏃", name="Běhací", description="Unavím se, ale nezničím se"
            ),
        )
        PhysicalCategory.objects.update_or_create(
            slug="hardcore",
            defaults=dict(
                emoji="🏋", name="Náročný", description="Po skončení někam odpadnu"
            ),
        )

        MentalCategory.objects.update_or_create(
            slug="minimal",
            defaults=dict(
                emoji="😌",
                name="Nenáročný",
                description="Odpočinkové programy, u kterých můžu vypnout hlavu",
            ),
        )
        MentalCategory.objects.update_or_create(
            slug="thinking",
            defaults=dict(
                emoji="🤔",
                name="Mozek potřeba",
                description="Trochu kreativity to chce, ale nic náročného",
            ),
        )
        MentalCategory.objects.update_or_create(
            slug="logically_demanding",
            defaults=dict(
                emoji="📈",
                name="Analyticky náročný",
                description="Plánování strategie, řešení šifer, komunikace v časovém presu",
            ),
        )
        MentalCategory.objects.update_or_create(
            slug="emotionally_demanding",
            defaults=dict(
                emoji="💔",
                name="Emočně náročný",
                description="Přemýšlecí otázky, řešení hodnot, pocitů, sdílení",
            ),
        )
        MentalCategory.objects.update_or_create(
            slug="hardcore",
            defaults=dict(
                emoji="🤬",
                name="Psycho",
                description="Fyzicky i psychicky náročný, narušování komforní zóny, nutnost řešit psychickou bezpečnost",
            ),
        )

        LocationCategory.objects.update_or_create(
            slug="tearoom",
            defaults=dict(
                emoji="🫖",
                name="Čajovna",
                description="Klidné a komfortní místo s hezkou atmosférou, omezené množství pohybu",
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="hall",
            defaults=dict(
                emoji="🏠",
                name="Větší místnost",
                description="Sál či místnost dostatkem prostoru, relativní teplo",
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="in_a_circle",
            defaults=dict(
                emoji="🔥",
                name="V kruhu (kolem ohně)",
                description="Všichi na sebe vidí, tepelný komfort, omezený pohyb",
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="field",
            defaults=dict(
                emoji="🌿",
                name="Louka",
                description="Louka či park, dost prostoru na sezení či běhání",
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="forest",
            defaults=dict(emoji="🌲", name="Les", description="Kousek lesa se stromy"),
        )
        LocationCategory.objects.update_or_create(
            slug="village",
            defaults=dict(
                emoji="🏘", name="Vesnice", description="Či město, výskyt lidí v okolí"
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="water",
            defaults=dict(
                emoji="💧",
                name="Voda",
                description="Nutno větší množství vody, na koupání či čvachtání",
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="at_road",
            defaults=dict(
                emoji="🛣",
                name="K cestě",
                description="Možno hrát během putování či přesunu",
            ),
        )
        LocationCategory.objects.update_or_create(
            slug="specific",
            defaults=dict(
                emoji="❓",
                name="Specifické umístění",
                description="K programu třeba specifické místo (ať konkrétní či zřídké)",
            ),
        )

        ParticipantNumberCategory.objects.update_or_create(
            slug="individual",
            defaults=dict(
                emoji="🚲",
                name="Pro jednotlivce",
                description="Každý hraje sám, lib. množství účastníků",
            ),
        )
        ParticipantNumberCategory.objects.update_or_create(
            slug="small",
            defaults=dict(
                emoji="🚗", name="Malá skupinka (4-6)", description="Skupinka 4-6 lidí"
            ),
        )
        ParticipantNumberCategory.objects.update_or_create(
            slug="few",
            defaults=dict(
                emoji="🚐", name="Skupina lidí (10+)", description="Zepár lidí, přes 10"
            ),
        )
        ParticipantNumberCategory.objects.update_or_create(
            slug="big",
            defaults=dict(
                emoji="🚌", name="Větší skupina (20+)", description="Kolem 20 lidí"
            ),
        )
        ParticipantNumberCategory.objects.update_or_create(
            slug="a_log",
            defaults=dict(
                emoji="🚢", name="Hromada lidí", description="Pro velká skupiny lidí"
            ),
        )

        ParticipantAgeCategory.objects.update_or_create(
            slug="parents_with_kids",
            defaults=dict(emoji="👪", name="Rodiče s dětmi", description=""),
        )
        ParticipantAgeCategory.objects.update_or_create(
            slug="preschool",
            defaults=dict(emoji="👶", name="Předškoláci", description=""),
        )
        ParticipantAgeCategory.objects.update_or_create(
            slug="elementary", defaults=dict(emoji="🧒", name="Školáci", description="")
        )
        ParticipantAgeCategory.objects.update_or_create(
            slug="teen", defaults=dict(emoji="🧑", name="Středoškoláci", description="")
        )
        ParticipantAgeCategory.objects.update_or_create(
            slug="university",
            defaults=dict(emoji="🧑‍🎓", name="Vysokoškoláci", description=""),
        )
        ParticipantAgeCategory.objects.update_or_create(
            slug="adult", defaults=dict(emoji="🧑‍💼", name="Dospělí", description="")
        )
        ParticipantAgeCategory.objects.update_or_create(
            slug="old", defaults=dict(emoji="🧓", name="Vyspělí", description="")
        )

        GameLengthCategory.objects.update_or_create(
            slug="short",
            defaults=dict(
                emoji="⚡",
                name="Rychlý (do 10 minut)",
                description="Krátké programy, jednuché seznamky, rozcvičky, pro vyplnění prostoje",
            ),
        )
        GameLengthCategory.objects.update_or_create(
            slug="an_hour",
            defaults=dict(
                emoji="🕐",
                name="Středně dlouhý (do hodiny)",
                description="Nějakou chvíli účastníky zabaví, dvě tři takové naplní odpoledne",
            ),
        )
        GameLengthCategory.objects.update_or_create(
            slug="long",
            defaults=dict(
                emoji="🕓",
                name="Dlouhý (pár hodin)",
                description="Odpolední program, noční hra",
            ),
        )
        GameLengthCategory.objects.update_or_create(
            slug="multiple_days",
            defaults=dict(
                emoji="📅",
                name="Vícedenní, celotáborový",
                description="Program rozprostřený přes několik dní, většinou na pozadí jiných programů",
            ),
        )

        PreparationLengthCategory.objects.update_or_create(
            slug="enough_to_read",
            defaults=dict(
                emoji="⚡",
                name="Stačí přečíst pravidla",
                description="Zkušený org přečte, a program rovnou uvede",
            ),
        )
        PreparationLengthCategory.objects.update_or_create(
            slug="need_to_study",
            defaults=dict(
                emoji="🧘",
                name="Třeba chvíle klidu",
                description="Netriviální, potřeba pořádně přečíst a pochopit",
            ),
        )
        PreparationLengthCategory.objects.update_or_create(
            slug="training",
            defaults=dict(
                emoji="🖨",
                name="Potřeba se připravit",
                description="Příprava zabere pár hodin, chystání materiálů, předání dalším orgům",
            ),
        )
        PreparationLengthCategory.objects.update_or_create(
            slug="multiple_sessions",
            defaults=dict(
                emoji="📅",
                name="Náročná příprava",
                description="Rozsáhle rozpracovaný či naopak nedokončený program, nutno věnovat značné úsilí k uvedení",
            ),
        )

        OrganizersNumberCategory.objects.update_or_create(
            slug="one",
            defaults=dict(
                emoji="🧍",
                name="Zvládnu sám",
                description="Uvedení programu zvládne jeden org",
            ),
        )
        OrganizersNumberCategory.objects.update_or_create(
            slug="few",
            defaults=dict(
                emoji="🤝",
                name="Potřebuji pomocnou ruku",
                description="Na program je potřeba dva či tři orgové",
            ),
        )
        OrganizersNumberCategory.objects.update_or_create(
            slug="group",
            defaults=dict(
                emoji="👪", name="Skupinka orgů", description="Potřeba kolem pěti orgů"
            ),
        )
        OrganizersNumberCategory.objects.update_or_create(
            slug="a_lot",
            defaults=dict(
                emoji="🌍",
                name="Spousta orgů",
                description="Velké hry vyžadující B-tým, atp.",
            ),
        )

        MaterialRequirementCategory.objects.update_or_create(
            slug="none",
            defaults=dict(
                emoji="🚫", name="Nic není potřeba", description="Stačí účastníci"
            ),
        )
        MaterialRequirementCategory.objects.update_or_create(
            slug="simple",
            defaults=dict(
                emoji="✏",
                name="Stačí základ",
                description="Šátky, tužka a papír, provázek",
            ),
        )
        MaterialRequirementCategory.objects.update_or_create(
            slug="get_some",
            defaults=dict(
                emoji="🖨",
                name="Potřeba nachystat",
                description="Tisk pár stránek, kostým, potřeba specifický materiál k programu",
            ),
        )
        MaterialRequirementCategory.objects.update_or_create(
            slug="complicated",
            defaults=dict(
                emoji="🚚",
                name="Kdo se s tím potáhne?",
                description="Velké množství či velmi specifický materiál",
            ),
        )

    def create_cookbook_categories(self):
        difficulties = [
            ("trivial", "triviální"),
            ("simple", "jednoduchá"),
            ("medium", "střední"),
            ("hard", "složitá"),
        ]
        for i, (slug, name) in enumerate(difficulties):
            RecipeDifficulty.objects.update_or_create(
                slug=slug, defaults=dict(order=i, name=name)
            )

        recipe_times = [
            ("instant", "instantní"),
            ("fast", "rychlé"),
            ("normal", "normální"),
            ("long", "maraton"),
        ]
        for i, (slug, name) in enumerate(recipe_times):
            RecipeRequiredTime.objects.update_or_create(
                slug=slug, defaults=dict(order=i, name=name)
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
        i = 0
        for group, items in tags.items():
            for slug, name in items:
                RecipeTag.objects.update_or_create(
                    slug=slug, defaults=dict(order=i, name=name, group=group)
                )
                i += 1

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
            # ("bread", "", "šumava", "šumavy", "šumav", "weight"),
        ]
        for i, (slug, abbreviation, name, name2, name5, of) in enumerate(units):
            Unit.objects.update_or_create(slug=slug, defaults=dict(order=i, name=name))
