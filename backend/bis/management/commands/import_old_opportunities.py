from collections import OrderedDict

from dateutil.relativedelta import relativedelta
from dateutil.utils import today
from django.core.management.base import BaseCommand

from bis.models import Location, User
from opportunities.models import Opportunity
from other.models import DashboardItem

data = [
    OrderedDict(
        [
            ("id", 2),
            ("name", "Brontosauří klubové večery - přednášky a workshopy"),
            ("start", "2023-01-23"),
            ("end", "2023-12-22"),
            ("on_web_start", "2023-01-23"),
            ("on_web_end", "2023-12-22"),
            (
                "introduction",
                "<div>Cel&yacute; rok mimo letn&iacute; pr&aacute;zdniny se každ&eacute; &uacute;ter&yacute; večer setk&aacute;vam&eacute; v klubovně brněnsk&eacute;ho &uacute;střed&iacute; u předn&aacute;&scaron;ek nebo diskus&iacute; na různ&aacute; t&eacute;mata bl&iacute;zk&aacute; Brontosaurům - ekologie, environmentalizmus, cestov&aacute;n&iacute;, dobrovolnictv&iacute;, kultura, pam&aacute;tky, udržitelnost, životn&iacute; styl a jin&eacute;. Někdy si tak&eacute; prom&iacute;tneme dokument, nebo si vyzkou&scaron;&iacute;me něco nov&eacute; na praktick&eacute;m workshopu - např&iacute;klad př&iacute;pravu čaje, j&oacute;gu, v&yacute;robu ptač&iacute;ch budek, nebo kreativn&iacute; psan&iacute;. A posledn&eacute; &uacute;ter&yacute; v měs&iacute;ci vždy hrajeme deskovky. Je to opravdu pestr&eacute;! Aktu&aacute;lně hled&aacute;me nov&eacute; n&aacute;pady na t&eacute;mata, předn&aacute;&scaron;ej&iacute;c&iacute; a lektory.&nbsp;</div>\r\n<div>&nbsp;</div>",
            ),
            (
                "description",
                '<div>Zaj&iacute;mav&yacute;ch podnětů a osobnost&iacute; nen&iacute; nikdy dost, takže pokud m&aacute;&scaron; tip na nějak&eacute; t&eacute;ma, kter&eacute; by podle tebe mohlo zarezonovat s brontosauř&iacute; komunitou, sem s n&iacute;m. M&aacute;&scaron; rovnou i tip, kdo by n&aacute;m o t&eacute;matu mohl předn&aacute;&scaron;et? Je&scaron;tě lep&scaron;&iacute;! Už m&aacute;&scaron; za sebou nějak&yacute; skvěl&yacute; workshop či předn&aacute;&scaron;ku, kter&eacute; chce&scaron; v na&scaron;em klubov&eacute;m programu? Nebo chce&scaron; rovnou předn&aacute;&scaron;et či facilitovat nějak&yacute; workshop? M&aacute;&scaron; tip na hru, o kterou bychom měli roz&scaron;&iacute;řit na&scaron;ie z&aacute;soby deskovek? Nev&aacute;hej se n&aacute;m ozvat a napi&scaron; Kubovi na <a href="mailto:dobrovolnictv&iacute;@brontosaurus.cz">dobrovolnictv&iacute;@brontosaurus.cz</a></div>\r\n<div>&nbsp;</div>',
            ),
            ("location_benefits", ""),
            (
                "personal_benefits",
                "<p>D&iacute;ky t&eacute;to př&iacute;ležitosti může&scaron; m&iacute;t skvěl&yacute; pocit ze smyslupln&eacute;ho doporučen&iacute;. Pokud se rozdhodne&scaron; zapojit jako lektor či předn&aacute;&scaron;ej&iacute;c&iacute;, tak bude&scaron; m&iacute;t &scaron;anci předat sv&eacute; znalosti a zku&scaron;enosti z tv&eacute;ho vlastn&iacute;ho t&eacute;ma. Nav&iacute;c si zdokonal&iacute;&scaron; dovednosti ve veřejn&eacute;m prezentov&aacute;n&iacute; či veden&iacute; lid&iacute;.&nbsp;</p>",
            ),
            (
                "requirements",
                "<p>Chuť spolupracovat na smyslupln&yacute;ch setk&aacute;n&iacute;ch v pohodov&eacute;m kolektivu.&nbsp;</p>",
            ),
            ("contact_name", ""),
            ("contact_phone", "+420 770 645 444"),
            ("contact_email", "dobrovolnictvi@brontosaurus.cz"),
            ("image", "/media/opportunity_images/Copy_of_1673290278890.jpg"),
            ("category_id", 2),
            ("location_id", 102),
            ("contact_person_id", ("f202aba2-9523-4b05-a119-da0cf7372a65")),
        ]
    ),
    OrderedDict(
        [
            ("id", 3),
            ("name", "Komunitní dobrovolnické akce v regionech"),
            ("start", "2023-04-19"),
            ("end", "2023-04-23"),
            ("on_web_start", "2023-01-01"),
            ("on_web_end", "2023-04-19"),
            (
                "introduction",
                '<p><span style="font-weight: 400;">Komunitn&iacute; setk&aacute;n&iacute;, dobr&yacute; pocit ze smyslupln&eacute; pr&aacute;ce, osloven&iacute; nov&yacute;ch lid&iacute; a rozvoj dobrovolnick&eacute; činnosti ve tv&eacute;m regionu &hellip; Zn&iacute; to l&aacute;kavě, že? Pak nev&aacute;hej a zapoj se do jedn&eacute; z&nbsp;deseti jednodenn&iacute;ch komunitn&iacute;ch akc&iacute;, kter&eacute; budou prvn&iacute; vla&scaron;tovkou toho, co n&aacute;s ve vět&scaron;&iacute;m měř&iacute;tku ček&aacute; již v&nbsp;př&iacute;&scaron;t&iacute;m roce u př&iacute;ležitosti oslav 50 let od vzniku Brontosaura.</span></p>\r\n<p><span style="font-weight: 400;">Pokud se přid&aacute;&scaron; mezi organiz&aacute;tory, z&iacute;sk&aacute;&scaron; skvělou př&iacute;ležitost oslovit nov&eacute; lidi ze sv&eacute;ho okol&iacute; a může&scaron; svůj čl&aacute;nek obohatit o nov&eacute; tv&aacute;ře nad&scaron;en&eacute; pro dobrovolnictv&iacute;, p&eacute;či o životn&iacute; prostřed&iacute; a spoustu dal&scaron;&iacute;ch společn&yacute;ch t&eacute;mat. Z&aacute;roveň se bude&scaron; moct tě&scaron;it na setk&aacute;n&iacute; lid&iacute; ze sv&eacute;ho regionu a dobrovolnick&aacute; pomoc pak bude kr&aacute;snou tře&scaron;ničkou na dortu.</span></p>\r\n<p><span style="font-weight: 400;">Akce se budou konat v term&iacute;nu od 19. do 23. 4., kter&yacute; jsme vybrali u př&iacute;ležitosti Dne Země 22. 4.</span></p>',
            ),
            (
                "description",
                '<p><strong>Tipy na dobrovolnick&eacute; činnosti na akci</strong></p>\r\n<p><span style="font-weight: 400;">Toto jsou na&scaron;e n&aacute;vrhy. Přij&iacute;t v&scaron;ak může&scaron; s&nbsp;č&iacute;mkoli vlastn&iacute;m a z&aacute;roveň vůbec nen&iacute; nutn&eacute;, abyste se věnovali pouze jedn&eacute; aktivitě. Naopak, pro &uacute;častn&iacute;ky bude zaj&iacute;mav&eacute; vyzkou&scaron;et si v&iacute;ce druhů dobrovolnick&eacute; pr&aacute;ce.</span></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">V&yacute;sadba stromů nebo keřů (při vhodn&yacute;ch klimatick&yacute;ch podm&iacute;nk&aacute;ch a zaji&scaron;těn&eacute; z&aacute;livce)</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">P&eacute;če o vysazen&eacute; stromy &ndash; kontrola &uacute;vazků a kůlů, mulčov&aacute;n&iacute;, z&aacute;livka, ořez&aacute;v&aacute;n&iacute; star&yacute;ch stromů</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Umisťov&aacute;n&iacute; berliček pro dravce k v&yacute;sadb&aacute;m&nbsp;&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">V&yacute;roba a vyvě&scaron;ov&aacute;n&iacute; ptač&iacute;ch budek a ochrana dutinov&yacute;ch stromů</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">V&yacute;roba &uacute;krytů pro dal&scaron;&iacute; živočichy &ndash; hmyz&iacute; hotel, čmel&iacute;n, ježkovn&iacute;k, hadn&iacute;k, broukovi&scaron;tě, z&iacute;dka pro je&scaron;těrky</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Či&scaron;těn&iacute; stud&aacute;nek a pramenů, budov&aacute;n&iacute; tůn&iacute;, obnova č&aacute;st&iacute; potoků</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Z&aacute;brany pro ž&aacute;by &ndash; ochrana tahov&yacute;ch cest obojživeln&iacute;ků&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Či&scaron;těn&iacute; potoků od odpadu</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">V&yacute;roba p&iacute;tek pro pt&aacute;ky</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">V&yacute;sadba mot&yacute;l&iacute;ho z&aacute;honu či komunitn&iacute;ho z&aacute;honu</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Vys&eacute;v&aacute;n&iacute; květnat&yacute;ch luk</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Tvorba př&iacute;rodn&iacute;ch zahrad (např. u veřejn&yacute;ch budov), kompostov&aacute;n&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">&Uacute;prava m&iacute;stn&iacute; zast&aacute;vky tak, aby byla bezpečn&aacute; pro pt&aacute;ky</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">P&eacute;če o př&iacute;rodn&iacute; lokalitu &ndash; kosen&iacute; luk, prořez&aacute;vky n&aacute;letov&yacute;ch dřevin</span></li>\r\n</ul>\r\n<p><span style="font-weight: 400;">Dal&scaron;&iacute; n&aacute;pady a kr&aacute;tk&eacute; n&aacute;vody najde&scaron; na <a href="http://naprirodunekaslu.cz/">http://naprirodunekaslu.cz</a>&nbsp;</span></p>',
            ),
            (
                "location_benefits",
                "<p>P&eacute;če o př&iacute;rodu a zv&yacute;&scaron;en&iacute; povědom&iacute; o dobrovolnick&eacute; činnosti dan&eacute;ho m&iacute;sta, komunity a regionu.</p>",
            ),
            (
                "personal_benefits",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Možnost sezn&aacute;mit &scaron;ir&scaron;&iacute; veřejnost s&nbsp;činnost&iacute; Brontosaura</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Propagace tv&eacute;ho čl&aacute;nku/spolku a z&iacute;sk&aacute;n&iacute; nov&yacute;ch členů</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Pomoc krajině, př&iacute;padně pam&aacute;tk&aacute;m</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Osvěta veřejnosti ohledně životn&iacute;ho prostřed&iacute;, rozvoj diskuse o aktu&aacute;ln&iacute;ch t&eacute;matech, kter&aacute; se s&nbsp;ŽP poj&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Osloven&iacute; m&iacute;stn&iacute;ch a jejich zapojen&iacute; do dobrovolnick&yacute;ch aktivit</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Na př&iacute;pravy nebude&scaron; s&aacute;m/sama, může&scaron; se obr&aacute;tit na koordin&aacute;torku těchto akc&iacute; nebo na zku&scaron;en&eacute; mentory</span></li>\r\n</ul>\r\n<p>&nbsp;</p>\r\n<p><strong>Co můžeme nab&iacute;dnout?</strong></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Podporu koordin&aacute;torky projektu Nikoly Star&eacute; z &uacute;střed&iacute; Hnut&iacute; Brontosaurus.&nbsp;</span></li>\r\n</ul>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Rady, pomoc a sd&iacute;len&iacute; užitečn&yacute;ch zku&scaron;enost&iacute; od mentorů, d&iacute;ky kter&yacute;m na př&iacute;pravu nebude&scaron; s&aacute;m/sama.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Pomoc s&nbsp;propagac&iacute; na webu a soci&aacute;ln&iacute;ch s&iacute;t&iacute;ch</span></li>\r\n</ul>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Mal&yacute; &bdquo;brontost&aacute;nek&ldquo; &ndash; propagačn&iacute; materi&aacute;ly k&nbsp;využit&iacute; na tv&eacute; akci (roll up, placky, let&aacute;čky &hellip;) + dle možnost&iacute; putovn&iacute; v&yacute;stavu o činnosti hnut&iacute; atd.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">N&aacute;vrhy na možn&eacute; dobrovolnick&eacute; činnosti (n&iacute;že) a n&aacute;vody (např. na v&yacute;robu budek)</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Možnost zapůjčen&iacute; ochrann&yacute;ch pomůcek a n&aacute;řad&iacute; ze skladu v&nbsp;Brně</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Pro organiz&aacute;tory trička &bdquo;Organizuji s&nbsp;Brontosaurem&ldquo;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Pomoc s&nbsp;vyd&aacute;n&iacute;m tiskov&eacute; zpr&aacute;vy po akci</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Finančn&iacute; podporu (do 7 tis&iacute;c Kč) formou proplacen&iacute; n&aacute;kladů za materi&aacute;l, dopravu, ochrann&eacute; pomůcky, př&iacute;padně dal&scaron;&iacute; služby spojen&eacute; s&nbsp;realizac&iacute; akce a dobrovolnickou prac&iacute; + možnost si ž&aacute;dat finance z D&aacute;rků př&iacute;rodě</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Drobnou odměnu pro hlavn&iacute;ho organiz&aacute;tora</span></li>\r\n</ul>',
            ),
            (
                "requirements",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Akce bude c&iacute;lit na veřejnost (při pl&aacute;nov&aacute;n&iacute; v&scaron;ak neopomeň c&iacute;lovou skupinu Brontosaura, tedy mlad&eacute; lidi ve věku od 15 do 30 let).</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">&Uacute;častn&iacute;ci se sezn&aacute;m&iacute; s&nbsp;činnost&iacute; Hnut&iacute; Brontosaurus, př&iacute;nosy dobrovolnictv&iacute; a možnost&iacute; zapojen&iacute; do dobrovolnick&yacute;ch aktivit.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Na akci nebude chybět smyslupln&aacute; dobrovolnick&aacute; pr&aacute;ce na pomoc př&iacute;rodě nebo pam&aacute;tk&aacute;m, do kter&eacute; se &uacute;častn&iacute;ci zapoj&iacute; a z&aacute;roveň budou sezn&aacute;meni s&nbsp;př&iacute;nosem dan&eacute; činnosti. Bude&scaron;-li cht&iacute;t, může&scaron; takto vytvořit i milou tradici, kter&aacute; umožn&iacute; dal&scaron;&iacute; setk&aacute;v&aacute;n&iacute; m&iacute;stn&iacute; komunity a společně budete o lokalitu (př&iacute;padně o v&yacute;robky jako např. budky, kter&eacute; při prvn&iacute;m setk&aacute;n&iacute; vytvoř&iacute;te) pečovat.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Je v&iacute;t&aacute;na realizace jednoduch&eacute;ho, drobn&eacute;ho doprovodn&eacute;ho programu. Např&iacute;klad společn&eacute; zah&aacute;jen&iacute; a ukončen&iacute;, představen&iacute; Brontosaura, aktivity pro děti a jin&eacute;. Fantazii se meze nekladou.</span></li>\r\n</ul>',
            ),
            ("contact_name", ""),
            ("contact_phone", ""),
            ("contact_email", "nikyy.stara@gmail.com"),
            ("image", "/media/opportunity_images/setkani-ovocnaru-cerven-2021_54.jpg"),
            ("category_id", 1),
            ("location_id", 1397),
            ("contact_person_id", ("ca04acf8-ae7c-4a99-a155-9aab01527414")),
        ]
    ),
    OrderedDict(
        [
            ("id", 4),
            ("name", "Organizátorský tým pro celostátní soutěž Máme rádi přírodu"),
            ("start", "2023-02-09"),
            ("end", "2023-12-31"),
            ("on_web_start", "2023-02-01"),
            ("on_web_end", "2023-12-31"),
            (
                "introduction",
                '<p dir="ltr">Chce&scaron; se zapojit do organiz&aacute;torsk&eacute;ho t&yacute;mu a l&aacute;k&aacute; tě vět&scaron;&iacute; akce? Co třeba rovnou akce celost&aacute;tn&iacute;ho rozměru?Pojď n&aacute;m pomoci s organizac&iacute; celost&aacute;tn&iacute; soutěže M&Aacute;ME R&Aacute;DI PŘ&Iacute;RODU!</p>',
            ),
            (
                "description",
                '<p dir="ltr">M&aacute;me r&aacute;di př&iacute;rodu&ldquo; je celost&aacute;tn&iacute; soutěž pro děti a ml&aacute;dež do 19 let, kterou poř&aacute;d&aacute; Hnut&iacute; Brontosaurus. Soutěž m&aacute; dlouholetou tradici, je organizov&aacute;na již od roku 1992. Soutěž si klade za &uacute;kol v prvn&iacute; řadě podpořit z&aacute;jem o př&iacute;rodu a p&eacute;či o ni. Je určena pro v&scaron;echny milovn&iacute;ky př&iacute;rody, kteř&iacute; z&aacute;roveň i r&aacute;di něco tvoř&iacute;.</p>\r\n<p dir="ltr">&nbsp;</p>\r\n<p dir="ltr">Nev&aacute;hej a přidej se do organiz&aacute;torsk&eacute;ho t&yacute;mu! Může&scaron; se zapojit do komunikace s &uacute;častn&iacute;ky soutěže, organizace slavnostn&iacute;ho vyhl&aacute;&scaron;en&iacute; v&yacute;sledků, hodnocen&iacute; př&iacute;choz&iacute;ch děl, vym&yacute;&scaron;len&iacute; oceněn&iacute; pro &uacute;častn&iacute;ky soutěže nebo vymy&scaron;len&iacute; t&eacute;matu a konceptu dal&scaron;&iacute;ho ročn&iacute;ku.</p>',
            ),
            ("location_benefits", ""),
            (
                "personal_benefits",
                '<ul>\r\n<li dir="ltr">Načerp&aacute;&scaron; zku&scaron;enosti z organizace akce celost&aacute;tn&iacute;ho rozměru.&nbsp;</li>\r\n<li dir="ltr">Podpoř&iacute;&scaron; z&aacute;jem o př&iacute;rodu a p&eacute;či o ni u dět&iacute; a ml&aacute;deže např&iacute;č celou republikou.</li>\r\n<li dir="ltr">Z&iacute;sk&aacute;&scaron; možnost pro vlastn&iacute; seberealizaci v r&aacute;mci vym&yacute;&scaron;len&iacute; dal&scaron;&iacute;ho ročn&iacute;ku soutěže.</li>\r\n<li dir="ltr">Stane&scaron; se souč&aacute;st&iacute; zku&scaron;en&eacute;ho t&yacute;mu organiz&aacute;torů.</li>\r\n<li dir="ltr">Z&iacute;sk&aacute;&scaron; přehled v dal&scaron;&iacute; činnosti v r&aacute;mci Hnut&iacute; Brontosaurus.&nbsp;</li>\r\n<li dir="ltr">Organizaci soutěže může&scaron; pojmout jako praxi při studiu na v&scaron;.</li>\r\n<li dir="ltr">Pozn&aacute;&scaron; nov&eacute; lidi.&nbsp;</li>\r\n</ul>',
            ),
            (
                "requirements",
                '<p dir="ltr">Chuť pomoci a aktivn&iacute; zapojen&iacute; :)&nbsp;</p>',
            ),
            ("contact_name", ""),
            ("contact_phone", "+420 732 882 032"),
            ("contact_email", "mrp@brontosaurus.cz"),
            ("image", "/media/opportunity_images/DSC_0486_wtQTQeZ.JPG"),
            ("category_id", 2),
            ("location_id", 1397),
            ("contact_person_id", ("001a1495-012e-4ec2-835d-4d4c29532372")),
        ]
    ),
    OrderedDict(
        [
            ("id", 5),
            ("name", "Vedoucí na dětském letním táboře"),
            ("start", "2023-08-21"),
            ("end", "2023-09-01"),
            ("on_web_start", "2023-02-06"),
            ("on_web_end", "2023-08-31"),
            (
                "introduction",
                '<p dir="ltr">Hled&aacute;me 1-2 vedouc&iacute;, kteř&iacute; by pomohly s organizac&iacute; her a zabezpečen&iacute;m dět&iacute; na t&aacute;boře. Je možn&eacute; se přidat na celou dobu nebo jen na č&aacute;sti s putov&aacute;n&iacute;m.&nbsp;</p>',
            ),
            (
                "description",
                '<p dir="ltr">Zorganizuj s n&iacute;mi kombinovan&yacute; př&iacute;městsko - pobytov&yacute; t&aacute;bor. Kde 10-15 dět&iacute; tr&aacute;v&iacute; 1/2 t&aacute;bora jako př&iacute;městskou (odch&aacute;z&iacute; sp&aacute;t domů) a na 2/2 se vydaj&iacute; na putovn&iacute; č&aacute;st s přesp&aacute;n&iacute;m.&nbsp;</p>\r\n<p dir="ltr">Z&aacute;zem&iacute; pro př&iacute;městskou č&aacute;st je v obci Kaly, kde m&aacute;me k dispozici klubovnu a kuchyň se společenskou m&iacute;stnost&iacute;. Pro pobytovou č&aacute;st je ubytov&aacute;n&iacute; zat&iacute;m v jedn&aacute;n&iacute; je pravděpodobn&aacute; i varianta stanov&aacute;n&iacute;. R&aacute;mcov&yacute; program je zaji&scaron;těn na detailech programu jako jsou jednotliv&eacute; hry je v&iacute;tan&eacute; se pod&iacute;let.&nbsp;</p>\r\n<p dir="ltr">Strava vynikaj&iacute;c&iacute;, materi&aacute;ln&iacute; zaji&scaron;těn&iacute; v&yacute;born&eacute;, vesel&eacute; a &scaron;ikovn&eacute; děti vždy k dispozici.&nbsp;</p>',
            ),
            (
                "location_benefits",
                "<p>Přispějeme k p&eacute;či o m&iacute;stn&iacute; př&iacute;rodu.</p>",
            ),
            (
                "personal_benefits",
                '<ul>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">kvalitně str&aacute;ven&yacute; čas se z&aacute;žitky, kter&eacute; si nekoup&iacute;&scaron;</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">pobyt venku v př&iacute;rodě</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">načerp&aacute;&scaron; zku&scaron;enosti v r&aacute;mci pr&aacute;ce s dětmi</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">pozn&aacute;&scaron; nov&eacute; lidi</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">z&iacute;sk&aacute;&scaron; přehled o dal&scaron;&iacute; činnosti v r&aacute;mci Hnut&iacute; Brontosaurus</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">&uacute;čast na t&aacute;boře může&scaron; pojmout jako praxi při studiu</p>\r\n</li>\r\n</ul>',
            ),
            (
                "requirements",
                '<ul>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">zodpovědn&yacute; př&iacute;stup</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">kladn&yacute; vztah k dětem&nbsp;</p>\r\n</li>\r\n<li dir="ltr">\r\n<p dir="ltr" role="presentation">m&iacute;t vždy nějak&eacute; hry po kaps&aacute;ch</p>\r\n</li>\r\n</ul>',
            ),
            ("contact_name", ""),
            ("contact_phone", "+420 733 542 216"),
            ("contact_email", "brdo.lisky@brontosaurus.cz"),
            ("image", "/media/opportunity_images/20220819_185438.JPG"),
            ("category_id", 1),
            ("location_id", 74),
            ("contact_person_id", ("b6ed2582-b586-4c09-b53f-e74a7f752179")),
        ]
    ),
    OrderedDict(
        [
            ("id", 6),
            ("name", "Pomoc s vedením dětského oddílu Praha"),
            ("start", "2023-02-17"),
            ("end", "2023-06-30"),
            ("on_web_start", "2023-02-10"),
            ("on_web_end", "2023-06-30"),
            (
                "introduction",
                '<p><span style="font-weight: 400;">Pražsk&eacute; brďo funguje již 10 let. M&aacute;me stabiln&iacute; skupinky dět&iacute;, kter&eacute; se sch&aacute;z&iacute; na odd&iacute;lov&yacute;ch schůzk&aacute;ch, v&yacute;prav&aacute;ch a v l&eacute;tě na t&aacute;boře. Zapoj se s do jedinečn&eacute; př&iacute;ležitosti podporovat u dět&iacute; l&aacute;sku k př&iacute;rodě pr&aacute;vě teď!</span></p>',
            ),
            (
                "description",
                '<p><span style="font-weight: 400;">Na oddilovych schůzk&aacute;ch bychom uv&iacute;tali nad&scaron;en&eacute;ho vedouc&iacute;ho, schopn&eacute;ho spolupracovat v t&yacute;mu.&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">Tvoje činnost bude spoč&iacute;vat zejm&eacute;na:</span></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">připravit program pro skupinku dět&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">veden&iacute; schůzek, v&yacute;prav a t&aacute;bora</span></li>\r\n</ul>\r\n<p><span style="font-weight: 400;">Odd&iacute;lov&eacute; schůzky prob&iacute;haj&iacute; vždy od 16 do 18 hodin, v &uacute;ter&yacute; v klubovně HB na Letn&eacute;, ve středu na Toulcově dvoře. &nbsp; </span></p>',
            ),
            ("location_benefits", ""),
            (
                "personal_benefits",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Př&iacute;jemně str&aacute;ven&yacute; čas venku v př&iacute;rodě.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Načerp&aacute;&scaron; zku&scaron;enosti v r&aacute;mci pr&aacute;ce s dětmi.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Stane&scaron; se souč&aacute;st&iacute; zku&scaron;en&eacute;ho t&yacute;mu vedouc&iacute;ch z Brďo Praha&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Z&iacute;sk&aacute;&scaron; přehled v dal&scaron;&iacute; činnosti v r&aacute;mci Hnut&iacute; Brontosaurus.&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Veden&iacute; odd&iacute;lu může&scaron; pojmout jako praxi při studiu na v&scaron;.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Pro pracuj&iacute;c&iacute; 5 dn&iacute; placen&eacute; dovolen&eacute; od st&aacute;tu na t&aacute;bor</span></li>\r\n</ul>',
            ),
            (
                "requirements",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">chuť pomoci a aktivn&iacute; zapojen&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">možnost &uacute;častnit se schůzek aspoň jednou za 14 dni</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">pozitivn&iacute; vztah k dětem a k př&iacute;rodě :)</span></li>\r\n</ul>',
            ),
            ("contact_name", "Maky Holubová"),
            ("contact_phone", "+420 739 750 623"),
            ("contact_email", "holumar@gmail.com"),
            ("image", "/media/opportunity_images/vedeni_detskeho_oddilu_PRAHA.jpg"),
            ("category_id", 2),
            ("location_id", 91),
            ("contact_person_id", ("79cef240-8328-41cb-8d97-8043737ed77f")),
        ]
    ),
    OrderedDict(
        [
            ("id", 7),
            ("name", "Zdravotník na letním táboře"),
            ("start", "2023-08-05"),
            ("end", "2023-08-17"),
            ("on_web_start", "2023-02-17"),
            ("on_web_end", "2023-08-01"),
            (
                "introduction",
                '<p><span style="font-weight: 400;">Pražsk&eacute; brďo funguje již 10 let. M&aacute;me stabiln&iacute; skupinky dět&iacute;, kter&eacute; se sch&aacute;z&iacute; na odd&iacute;lov&yacute;ch schůzk&aacute;ch, v&yacute;prav&aacute;ch a v l&eacute;tě na t&aacute;boře. Zapoj se s do jedinečn&eacute; př&iacute;ležitosti &uacute;častnit se s n&aacute;mi letn&iacute;ho t&aacute;bora!</span></p>',
            ),
            (
                "description",
                '<p><span style="font-weight: 400;">Na letn&iacute; t&aacute;bor pojedeme do Kozlova u Ledče nad S&aacute;zavou. Potřebujeme zdravotn&iacute;ka zotavovac&iacute;ch akc&iacute;. Na t&aacute;boře budeme m&iacute;t přibližně 30 děti od prvn&iacute; do osm&eacute; tř&iacute;dy. Sp&aacute;t budeme v podsadovych stanech, vodu br&aacute;t ze stud&aacute;nky, bez elektřiny. Na t&aacute;boře bude k dispozici auto na n&aacute;kupy v Ledči, cca 7 km, kde je i nemocnice. L&eacute;k&aacute;rničku můžeme vybavit dle požadavků.&nbsp;</span></p>\r\n<p>&nbsp;</p>\r\n<p><span style="font-weight: 400;">V př&iacute;padě, že bys s n&aacute;mi jel jako zdravotn&iacute;k, uv&iacute;t&aacute;me zapojen&iacute; do programu, ale nen&iacute; podm&iacute;nkou. Jsme tak&eacute; otevřen&iacute;, když by sis s sebou chtěl vz&iacute;t d&iacute;tě v na&scaron;em věku (po prvn&iacute; tř&iacute;dě - 14), př&iacute;padně psa, ale mus&iacute; se dobře sn&aacute;&scaron;et s jin&yacute;m psem.&nbsp;</span></p>\r\n<p><br /><br /><br /></p>\r\n<p><span style="font-weight: 400;">Tvoje činnost bude spoč&iacute;vat zejm&eacute;na:</span></p>\r\n<p><span style="font-weight: 400;">Běžn&aacute; činnost zdravotn&iacute;ka na t&aacute;boře</span></p>\r\n<p><span style="font-weight: 400;">Sezn&aacute;men&iacute; družin s prvn&iacute; pomoc&iacute;</span></p>\r\n<p><span style="font-weight: 400;">Pomoc s programem a chodem t&aacute;bora</span></p>',
            ),
            ("location_benefits", ""),
            (
                "personal_benefits",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Př&iacute;jemně str&aacute;ven&yacute; čas venku v př&iacute;rodě.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Načerp&aacute;&scaron; zku&scaron;enosti v r&aacute;mci pr&aacute;ce s dětmi.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Stane&scaron; se souč&aacute;st&iacute; zku&scaron;en&eacute;ho t&yacute;mu vedouc&iacute;ch z Brďo Praha&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Z&iacute;sk&aacute;&scaron; přehled v dal&scaron;&iacute; činnosti v r&aacute;mci Hnut&iacute; Brontosaurus.&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">&Uacute;čast na t&aacute;boře může&scaron; pojmout jako praxi při studiu na v&scaron;.</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Pro pracuj&iacute;c&iacute; 5 dn&iacute; placen&eacute; dovolen&eacute; od st&aacute;tu na t&aacute;bor</span></li>\r\n</ul>',
            ),
            (
                "requirements",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">certifik&aacute;t zdravotn&iacute;k zotavovac&iacute;ch akc&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">chuť pomoci a aktivn&iacute; zapojen&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">pozitivn&iacute; vztah k dětem a k př&iacute;rodě :)</span></li>\r\n</ul>',
            ),
            ("contact_name", "Maky Holubová"),
            ("contact_phone", "+420 739 750 623"),
            ("contact_email", "holumar@gmail.com"),
            ("image", "/media/opportunity_images/zdravotnik_leti_tabor_Praha.jpg"),
            ("category_id", 2),
            ("location_id", 974),
            ("contact_person_id", ("79cef240-8328-41cb-8d97-8043737ed77f")),
        ]
    ),
    OrderedDict(
        [
            ("id", 10),
            ("name", "Budkování v Mikulčickém luhu"),
            ("start", "2022-09-09"),
            ("end", "2023-03-15"),
            ("on_web_start", "2022-09-09"),
            ("on_web_end", "2023-02-15"),
            (
                "introduction",
                "<p>Brontosauři na Podluž&iacute; jsou po torn&aacute;du dosti zaměstn&aacute;ni pracemi na obnově zeleně, opravami klubovny apod. a uv&iacute;taj&iacute; pomoc s peč&iacute; o hn&iacute;zdn&iacute; budky pro ptactvo v lužn&iacute;ch les&iacute;ch na Podluž&iacute; a s jejich doplňov&aacute;n&iacute;m.</p>\r\n<p>&nbsp;</p>",
            ),
            (
                "description",
                "<p>Uv&iacute;t&aacute;me tak v&iacute;kendov&eacute; i jednodenn&iacute; akce na či&scaron;těn&iacute;, opravy, evidenci stavaj&iacute;c&iacute;ch budek a na vyvě&scaron;ov&aacute;n&iacute; nov&yacute;ch. Budky v les&iacute;ch, jež jsou poznamen&aacute;ny hospod&aacute;řskou činnost&iacute;, kompenzuj&iacute; ptactvu nedostatek přirozen&yacute;ch hn&iacute;zdn&iacute;ch dutin.</p>\r\n<p>K akc&iacute;m nab&iacute;z&iacute;me, jak z&aacute;zem&iacute; kluboven v bl&iacute;zk&yacute;ch ob&iacute;ch či maringotky v lužn&iacute;m lese, tak n&aacute;řad&iacute; a ve&scaron;ker&eacute; podklady a pomůcky pro dobrovolnickou pomoc. Um&iacute;me nab&iacute;dnout i odborn&yacute; v&yacute;klad v př&iacute;nosu dan&eacute; dobrovolnick&eacute; č&iacute;nnosti či exkuze nebo předn&aacute;&scaron;ky k m&iacute;stn&iacute; př&iacute;rodě a jej&iacute; ochraně a jej&iacute;ch ohrožen&iacute;ch.</p>\r\n<p>Dle zad&aacute;n&iacute; v map&aacute;ch a GPS se po skupink&aacute;ch proch&aacute;z&iacute; lužn&iacute; les a kontroluj&iacute; se, eviduj&iacute; a př&iacute;padně opravuj&iacute; st&aacute;vaj&iacute;c&iacute; budky a jejich obsazenost. Ve vybran&yacute;ch &uacute;sec&iacute;ch se doplňuj&iacute; budky nov&eacute; pro různ&eacute; druhy ptactva.</p>",
            ),
            (
                "location_benefits",
                "<p>Lužn&iacute; lesy na soutoku Moravy a Dyje jsou jednou z př&iacute;rodně nejbohat&scaron;&iacute;ch a nejceněj&scaron;&iacute;ch lokalit ve středn&iacute; Evropě. Druhovou pestrost po&scaron;kozuje v&scaron;ak dlouhodob&aacute; nevhodně veden&aacute; hospod&aacute;řsk&aacute; činnost v les&iacute;ch, odkud miz&iacute; star&eacute; porosty, odum&iacute;raj&iacute;c&iacute; stromy apod. Ve vznikaj&iacute;c&iacute;ch mlad&yacute;ch stejnověk&yacute;ch monokulturn&iacute;ch porostech chyb&iacute; např&iacute;klad star&eacute; doupn&eacute; stromy. Vyvě&scaron;ov&aacute;n&iacute;m budek kompenzujeme pr&aacute;vě nedostatek hn&iacute;zdn&iacute;ch dudit pro mnoh&eacute; druhy ptactva - s&yacute;kory, lejsky, brhl&iacute;ky, sovy aj.</p>",
            ),
            (
                "personal_benefits",
                '<p><span style="font-weight: 400;">Zejm&eacute;na dobr&yacute; pocit, že zpěv ptactva v brněnsk&yacute;ch parc&iacute;ch zn&iacute; i d&iacute;ky tobě! Taky se dozv&iacute;&scaron; o tom, jak a proč se budky vyvě&scaron;uj&iacute;, jac&iacute; pt&aacute;ci v nich hn&iacute;zdn&iacute;, apod. Inspirovat tě budou obdobn&eacute; brontosauř&iacute; projekty po cel&eacute; ČR. Rozvine&scaron; si organizačn&iacute; dovednosti, přiuč&iacute;&scaron; se něco ochraně př&iacute;rody.<br /></span></p>',
            ),
            (
                "requirements",
                '<p><span style="font-weight: 400;">Nic speci&aacute;ln&iacute;ho nen&iacute; třeba umět. Předpokl&aacute;d&aacute;me, že dovednostmi pr&aacute;ci na PC a stoup&aacute;n&iacute; po žebři vl&aacute;dne&scaron;. Hod&iacute; se umět pracovat s GPS navigac&iacute;, ale to když tak vysvětl&iacute;me :)</span></p>',
            ),
            ("contact_name", "Dalimil Toman"),
            ("contact_phone", "+420 605 763 112"),
            ("contact_email", "podluzi@brontosaurus.cz"),
            (
                "image",
                "/media/opportunity_images/%C4%8Di%C5%A1t%C4%9Bn%C3%AD_budky.jpg",
            ),
            ("category_id", 3),
            ("location_id", 2103),
            ("contact_person_id", ("f5eea2be-55ac-4df6-a35d-15f786c061b6")),
        ]
    ),
    OrderedDict(
        [
            ("id", 11),
            ("name", "Koordinátor/koordinátorka péče o budky v Brně"),
            ("start", "2022-09-09"),
            ("end", "2023-03-15"),
            ("on_web_start", "2022-09-09"),
            ("on_web_end", "2023-01-01"),
            (
                "introduction",
                '<p><span style="font-weight: 400;">Brontosauři v Brně dlouhodobě pečuj&iacute; o ptactvo a instalac&iacute; ptač&iacute;ch budek doplňuj&iacute; chyběj&iacute;c&iacute; možnosti hn&iacute;zděn&iacute; pro s&yacute;kory, lejsky i dal&scaron;&iacute; druhy pt&aacute;ků. Zapoj se s n&aacute;mi do koordinace p&eacute;če o ptač&iacute; budky.&nbsp;</span></p>\r\n<p>&nbsp;</p>',
            ),
            (
                "description",
                '<p><span style="font-weight: 400;">Aktu&aacute;lně m&aacute;me vyvě&scaron;eno na 200 budek. Budky každoročně doplňujeme, opravujeme, čist&iacute;me a monitorujeme jejich obsazenost. K tomu poř&aacute;d&aacute;me vět&scaron;inou odpoledn&iacute; dobrovolnick&eacute; akce pro ty, co chtěj&iacute; pomoci.</span></p>\r\n<p><span style="font-weight: 400;">Hled&aacute;me nad&scaron;ence/nad&scaron;enkyni, kter&yacute;/kter&aacute; by p&eacute;či o budky koordinoval/koordinovala. To spoč&iacute;v&aacute; ve:</span></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">spr&aacute;vě jednoduch&eacute; datab&aacute;ze budek</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">př&iacute;pravě podkladů k p&eacute;či o budky v jednotliv&yacute;ch lokalit&aacute;ch (mapa a seznam budek z datab&aacute;ze)</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">př&iacute;pravě nov&yacute;ch budek na vyvě&scaron;en&iacute;, popř. zaji&scaron;těn&iacute; drobn&eacute;ho materi&aacute;lu</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">pomoc se zaji&scaron;těn&iacute;m 3-5 akc&iacute; během roku na monitoring, či&scaron;těn&iacute; a &uacute;držbu budek (mohou je organizovat i dal&scaron;&iacute; dobrovoln&iacute;ci)</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">zad&aacute;n&iacute; obsazenosti budek do datab&aacute;ze</span></li>\r\n</ul>',
            ),
            (
                "location_benefits",
                '<p><span style="font-weight: 400;">Podpoř&iacute;&scaron; p&eacute;či o ptactvo v mnoha lokalit&aacute;ch Brna, biodiverzitu městk&eacute; př&iacute;rody apod.<br /></span></p>',
            ),
            (
                "personal_benefits",
                '<p><span style="font-weight: 400;">Zejm&eacute;na dobr&yacute; pocit, že zpěv ptactva v brněnsk&yacute;ch parc&iacute;ch zn&iacute; i d&iacute;ky tobě! Taky se dozv&iacute;&scaron; o tom, jak a proč se budky vyvě&scaron;uj&iacute;, jac&iacute; pt&aacute;ci v nich hn&iacute;zdn&iacute;, apod. Inspirovat tě budou obdobn&eacute; brontosauř&iacute; projekty po cel&eacute; ČR. Rozvine&scaron; si organizačn&iacute; dovednosti, přiuč&iacute;&scaron; se něco k propagaci akc&iacute;. A zejm&eacute;na pozn&aacute;&scaron; dal&scaron;&iacute; inspirativn&iacute; lidi na Dobrovolnick&eacute;m centru Hnut&iacute; Brontosaurus.</span></p>',
            ),
            (
                "requirements",
                '<p><span style="font-weight: 400;">Uv&iacute;t&aacute;me dovednosti pr&aacute;ce s GPS navigac&iacute; a z&aacute;kladn&iacute; organizačn&iacute; schopnosti. Znalost v&yacute;znamu budek a problematiky ochrany ptactva v&yacute;hodou. <br /></span></p>',
            ),
            ("contact_name", "Tereza Opravilová"),
            ("contact_phone", "+420 736 720 568"),
            ("contact_email", "akce-priroda@brontosaurus.cz"),
            ("image", "/media/app/media/opportunity_images/IMG_6549.jpg"),
            ("category_id", 2),
            ("location_id", 1225),
            ("contact_person_id", ("fff98659-92b3-4e70-9f0d-0aedb1e53391")),
        ]
    ),
    OrderedDict(
        [
            ("id", 12),
            ("name", "Technické zázemí pro organizátorské setkání REFRESH"),
            ("start", "2022-10-01"),
            ("end", "2022-12-04"),
            ("on_web_start", "2022-09-09"),
            ("on_web_end", "2022-10-20"),
            (
                "introduction",
                "<p>Skvěl&yacute; t&yacute;m velk&eacute;ho organiz&aacute;torsk&eacute;ho setk&aacute;n&iacute; Hnut&iacute; Brontosaurus REFRESH do sv&yacute;ch řad r&aacute;d přijme dal&scaron;&iacute; členy a členky, co by chtěli pomoci v z&aacute;zem&iacute; akce, s koordinac&iacute; j&iacute;del, př&iacute;pravou občerstven&iacute; pro &uacute;častn&iacute;ky, př&iacute;pravou materi&aacute;lu apod.</p>",
            ),
            (
                "description",
                "<p>Hled&aacute;me:</p>\r\n<p>Ty, jež by uměli koordinovat př&iacute;pravu coffe breaků, čajovny a dal&scaron;&iacute;ho občerstven&iacute; na akci.</p>\r\n<p>Ty, jež by uměli komunikovat s m&iacute;stn&iacute; kuchyn&iacute; a kuchařkami, napl&aacute;novat a ře&scaron;it j&iacute;deln&iacute;ček apod.</p>\r\n<p>Ty, jež by uměli schrom&aacute;ždit, nakoupit, sehnat a na m&iacute;stě spravovat a chystat materi&aacute;l potřebn&yacute; na jednotliv&eacute; programy.</p>",
            ),
            (
                "location_benefits",
                "<p>&Scaron;tastn&iacute; &uacute;častn&iacute;ci akce :-)</p>",
            ),
            (
                "personal_benefits",
                "<p>Pozn&aacute;n&iacute; z&aacute;kulis&iacute; př&iacute;pravy jedn&eacute; z největ&scaron;&iacute;ch akc&iacute; Hnut&iacute; Brontosaurus pro organiz&aacute;tory. Z&iacute;sk&aacute;n&iacute; organiz&aacute;torsk&yacute;ch zku&scaron;enost&iacute; při př&iacute;pravě. Nov&eacute; kontakty.</p>\r\n<p>Radost z toho, že jsme společně připravili akci, kter&aacute; Brontosaura posune zase d&aacute;l, namotivuje nov&eacute; organiz&aacute;tory a pote&scaron;&iacute; ty st&aacute;vaj&iacute;c&iacute;.</p>",
            ),
            (
                "requirements",
                "<p>Na akci a před n&iacute; uv&iacute;t&aacute;me dobrou n&aacute;ladu, nadhled, organizačn&iacute; dovednosti, flexibilitu v ře&scaron;en&iacute; probl&eacute;mů... :-)</p>\r\n<p>Bude potřeba věnovat čas př&iacute;pravě i před akc&iacute;. Cca min. 2-3 schůzky, t&yacute;movky, př&iacute;prava materi&aacute;lu dle potřeb, jež vyplynou.</p>",
            ),
            ("contact_name", "Rozálie Jandová"),
            ("contact_phone", ""),
            ("contact_email", ""),
            ("image", "/media/app/media/opportunity_images/P1020127.jpg"),
            ("category_id", 1),
            ("location_id", 1225),
            ("contact_person_id", ("fff98659-92b3-4e70-9f0d-0aedb1e53391")),
        ]
    ),
    OrderedDict(
        [
            ("id", 16),
            ("name", "Výsadba stromů v Hruškách"),
            ("start", "2022-12-02"),
            ("end", "2022-12-18"),
            ("on_web_start", "2022-10-10"),
            ("on_web_end", "2022-12-11"),
            (
                "introduction",
                "<p>Vesnice Hru&scaron;ky nedaleko Slavkova je vesnic&iacute; plnou ovoce. Za v&yacute;sadbami stoj&iacute; klub Spadl&iacute; z Hru&scaron;ky v čele s Dominikem Grohmannem. Na několika dobrovolnick&yacute;ch akc&iacute;ch se zde od roku 2018 vys&aacute;zelo na stovku ovocn&yacute;ch stromů, o kter&eacute; se každoročně pečuje a dal&scaron;&iacute; se st&aacute;le s&aacute;z&iacute;.</p>\r\n<p>V současn&eacute; době zde v&scaron;ak chyb&iacute; dobrovoln&iacute;ci a dobrovolnice, kteř&iacute; by o tyto v&yacute;sadby pečovali a na nov&yacute;ch v&yacute;sadb&aacute;ch se pod&iacute;leli. <strong>Hled&aacute;me organiz&aacute;tory či organiz&aacute;torsk&eacute; t&yacute;my</strong>, kteř&iacute; zde na zač&aacute;tku prosince uspoř&aacute;daj&iacute; dobrovolnicko z&aacute;žitkovou akci na v&yacute;sadby stromů!</p>",
            ),
            (
                "description",
                "<p>Uspoř&aacute;dej dobrovolnickou jednodenn&iacute; akci nebo dobrovolnicko z&aacute;žitkovou v&iacute;kendovku v Hru&scaron;k&aacute;ch. N&aacute;pln&iacute; dobrovolnick&eacute; pr&aacute;ce bude dosadba ovocn&yacute;ch stromů do v&yacute;sadeb po okol&iacute; a p&eacute;če o vysazen&eacute; stromy, kter&aacute; bude prob&iacute;hat ve spolupr&aacute;ci s Dominikem či něk&yacute;m z ovocn&aacute;řsk&eacute;ho t&yacute;mu.</p>\r\n<p>Na tobě tak bude <strong>realizace akce</strong> ve smyslu z&aacute;zem&iacute;, propagace, programu, komunikace s &uacute;častn&iacute;ky apod.&nbsp;</p>\r\n<p>Pro kon&aacute;n&iacute; akce lze využ&iacute;t prostory hasičky př&iacute;mo v obci, kter&aacute; je vybaven&aacute; kuchyn&iacute;, koupelnou, span&iacute; je na karimatk&aacute;ch.</p>",
            ),
            (
                "location_benefits",
                "<p>Pomůže&scaron; s p&eacute;č&iacute; o ovocn&eacute; stromy a jejich n&aacute;vratem do krajiny.</p>",
            ),
            (
                "personal_benefits",
                "<p>Pod veden&iacute;m zku&scaron;en&yacute;ch sadařů a sadařek se nauč&iacute;&scaron;, jak spr&aacute;vně s&aacute;zet stromy a pečovat o ně. Kromě samotn&eacute; dobrovolnick&eacute; pr&aacute;ce je možn&eacute; se domluvit na workshopu k ovocn&yacute;m stromům, určov&aacute;n&iacute; odrůd ovoce či rukoděln&yacute;m workshopům.</p>\r\n<p>Jinak z&iacute;sk&aacute;&scaron; dal&scaron;&iacute; cenn&eacute; zku&scaron;enosti z organizace dobrovolnicko z&aacute;žitkov&eacute; akce.</p>",
            ),
            (
                "requirements",
                "<p>Nad&scaron;en&iacute; a odhodl&aacute;n&iacute; do organizace dobrovolnick&eacute; v&iacute;kendovky nebo jednodenn&iacute; akce.</p>",
            ),
            ("contact_name", "Terka"),
            ("contact_phone", "+420 736 720 568"),
            ("contact_email", "akce-priroda@brontosaurus.cz"),
            ("image", "/media/app/media/opportunity_images/IMG_5913.JPG"),
            ("category_id", 3),
            ("location_id", 1225),
            ("contact_person_id", ("fff98659-92b3-4e70-9f0d-0aedb1e53391")),
        ]
    ),
    OrderedDict(
        [
            ("id", 17),
            ("name", "Biokoridor Přerov Hvězdárna"),
            ("start", "2023-03-15"),
            ("end", "2023-09-30"),
            ("on_web_start", "2023-01-01"),
            ("on_web_end", "2023-09-24"),
            (
                "introduction",
                "<p>Vznikaj&iacute;c&iacute; biokoridor Přerov - Hvězd&aacute;rna se nach&aacute;z&iacute; v zemědělsk&eacute; krajině na v&yacute;chodn&iacute;m okraji města. Je opatřen&iacute;m pro podporu biodiverzity a pro adaptaci krajiny na změnu klimatu. Za jeho vznikem stoj&iacute; přerovsk&yacute; <strong>spolek Na&scaron;e společn&aacute; krajina</strong>, kter&yacute; biokoridor navrhnul, vytvořil a pravidelně se o něj star&aacute;. P&eacute;če je na několik m&aacute;lo členů spolku mnoho a dal&scaron;&iacute; zapojen&iacute; dobrovoln&iacute;ků by tak mohlo s p&eacute;č&iacute; o biokoridor ulehčil a pomohli by pustit se do dal&scaron;&iacute;ch projektů jako např&iacute;klad realizace naučn&eacute; stezky přes biokoridor.</p>",
            ),
            (
                "description",
                "<p>Hled&aacute;me jednotliv&eacute; organiz&aacute;tory nebo organiz&aacute;torsk&eacute; t&yacute;my, kteř&iacute; by r&aacute;di ve spolupr&aacute;ci s m&iacute;stn&iacute;m spolkem na tomto m&iacute;stě poř&aacute;dali jednodenn&iacute; nebo v&iacute;kendov&eacute; dobrovolnick&eacute; akce. N&aacute;pln&iacute; dobrovolnick&eacute; pr&aacute;ce by byla dle ročn&iacute;ho obdob&iacute; v&yacute;pomoc s p&eacute;č&iacute; o biokoridor (např&iacute;klad stavba a opravy oplocenek, sečen&iacute; a kosen&iacute; porostu, odstraňov&aacute;n&iacute; nepůvodn&iacute;ch n&aacute;letů, v&yacute;roba a instalace hmyz&iacute;ch domečků a ptač&iacute;ch budek, zal&eacute;v&aacute;n&iacute; a o&scaron;etřov&aacute;n&iacute; v&yacute;sadeb dřevin, s&aacute;zen&iacute; nov&yacute;ch keřů a stromů, &uacute;držba informačn&iacute;ch prvků, a dal&scaron;&iacute;).</p>",
            ),
            (
                "location_benefits",
                '<p>Biokoridor a dal&scaron;&iacute; navazuj&iacute;c&iacute; prvky vytvoř&iacute; až sedm kilometrů dlouh&yacute; p&aacute;s zeleně kolem v&yacute;chodn&iacute;ho okraje Přerova. M&iacute;sto bude sloužit jako uk&aacute;zkov&yacute; postup pro obnovu zemědělsk&eacute; krajiny a jako oblast bohat&eacute;ho v&yacute;skytu poln&iacute;ch druhů rostlin a živočichů. Krajinou bude proch&aacute;zet ekoturistick&aacute; stezka, kterou může veřejnost &scaron;etrně nahl&eacute;dnout do tajů př&iacute;rody kulturn&iacute; stepi. Bude zde možnost pozorovat nespočet vz&aacute;cn&yacute;ch kvetouc&iacute;ch plevelů, denn&iacute;ch i nočn&iacute;ch mot&yacute;lů a poln&iacute;ch pt&aacute;ků. O lokalitě Biokoridor Přerov Hvězd&aacute;rna se může&scaron; v&iacute;c doč&iacute;st v <a href="https://www.mapotic.com/lokality-hnuti-brontosaurus/1478925-biokoridor-prerov-hvezdarna">datab&aacute;zi lokalit</a>.&nbsp;</p>',
            ),
            (
                "personal_benefits",
                "<p>Z&iacute;sk&aacute;&scaron; cenn&eacute; zku&scaron;enosti s poř&aacute;d&aacute;n&iacute;m dobrovolnick&yacute;ch nebo dobrovolnicko z&aacute;žitkov&yacute;ch akc&iacute; a <strong>praktick&eacute; zku&scaron;enosti s p&eacute;č&iacute; o př&iacute;rodn&iacute; lokalitu</strong>, dozv&iacute;&scaron; se mnoho nov&yacute;ch věc&iacute; o <strong>současn&eacute; zemědělsk&eacute; krajině</strong>, možn&yacute;ch ře&scaron;en&iacute; probl&eacute;mů krajiny, nauč&iacute;&scaron; se nov&eacute; typy činnost&iacute; v př&iacute;rodě.&nbsp;</p>\r\n<p>Pro samotn&eacute; poř&aacute;d&aacute;n&iacute; akc&iacute; je na lokalitě v&yacute;hodu spolupr&aacute;ce se spolkem Na&scaron;e společn&aacute; krajina, kter&yacute;<strong> prakticky i odborně za&scaron;t&iacute;t&iacute; dobrovolnickou činnost</strong>, pomůže s hled&aacute;n&iacute;m z&aacute;zem&iacute; ve městě a může nab&iacute;dnout bohat&yacute; doprovodn&yacute; program v podobě exkurz&iacute; po okol&iacute;.&nbsp;</p>",
            ),
            (
                "requirements",
                "<p>Zku&scaron;enost s dobrovolnick&yacute;mi akcemi pro př&iacute;rodu (alespoň v podobě &uacute;časti), komunikačn&iacute; schopnosti a t&yacute;mvov&aacute; spolupr&aacute;ce, v př&iacute;padě organizace v&iacute;kendov&eacute; akce kvalifikace Organiz&aacute;tor v&iacute;kendovek HB alespoň jednoho člena t&yacute;mu.&nbsp;</p>",
            ),
            ("contact_name", "Petr Rejzek"),
            ("contact_phone", ""),
            ("contact_email", "info@koroptvicky.cz"),
            ("image", "/media/opportunity_images/A_lokalita4d.JPG"),
            ("category_id", 3),
            ("location_id", 2162),
            ("contact_person_id", ("00f3b097-aea5-4095-b142-7ffe0009fcb7")),
        ]
    ),
    OrderedDict(
        [
            ("id", 18),
            ("name", "Ekofarma Šardice"),
            ("start", "2023-03-15"),
            ("end", "2023-08-30"),
            ("on_web_start", "2023-02-01"),
            ("on_web_end", "2023-06-30"),
            (
                "introduction",
                "<p>Chce&scaron; se dozvědět něco o tom, jak můžeme v zemědělsk&eacute; krajině zadržovat vodu, podporovat biodiverzitu a navracet život? Chce&scaron; na vlastn&iacute; oči vidět jak to v&scaron;echno může fungovat a chce&scaron; se zapojit do p&eacute;če o takov&aacute; m&iacute;sta?</p>\r\n<p>Zapoj se do pomoci na Ekofarmě v &Scaron;ardic&iacute;ch, vyraž sem s kamar&aacute;dy v men&scaron;&iacute; skupině nebo zde uspoř&aacute;dej akci pro dal&scaron;&iacute; dobrovoln&iacute;ky a dobrovolnice!&nbsp;</p>",
            ),
            (
                "description",
                "<p>Prvotn&iacute;m z&aacute;měrem zemědělce a pedagoga Petra Marady byla ochrana &uacute;zem&iacute; před nepř&iacute;zniv&yacute;m a ničiv&yacute;m dopadem př&iacute;valov&yacute;ch de&scaron;ťů. Kromě obnovy vodn&iacute;ho režimu krajiny jeho opatřen&iacute; ale tak&eacute; podporuj&iacute; biodiverzitu a zaji&scaron;ťuj&iacute; prostupnost krajiny. Jeho aktivity rozv&iacute;j&iacute; fungov&aacute;n&iacute; komunity a jsou tak&eacute; zdrojem odborn&eacute; a informačn&iacute; činnosti. Postupn&yacute;m roz&scaron;iřov&aacute;n&iacute;m obhospodařovan&yacute;ch pozemků vznikla vzorov&aacute; ekofarma, na kter&eacute; m&aacute;&scaron; možnost zapojit se do p&eacute;če o př&iacute;rodu i ty a kromě toho se dozvědět spoustu informac&iacute; a nahl&eacute;dnout do toho, jak zdej&scaron;&iacute; ekosyst&eacute;m funguje.&nbsp;</p>\r\n<p>Do &Scaron;ardic může&scaron; vyrazit pom&aacute;hat a vzděl&aacute;vat se s kamar&aacute;dy v men&scaron;&iacute; skupině nebo zde může&scaron; uspoř&aacute;dat jednodenn&iacute; nebo v&iacute;cedenn&iacute; dobrovolnickou akci. N&aacute;pln&iacute; dobrovolnick&eacute; činnosti na ekofarmě je pomoc s p&eacute;č&iacute; o v&yacute;znamn&eacute; krajinotvorn&eacute; prvky zemědělsk&eacute; krajiny - sečen&iacute; tr&aacute;vobylinn&eacute;ho patra, odstraňov&aacute;n&iacute; oplocenek, odstraňov&aacute;n&iacute; letorostů z kmene ovocn&yacute;ch stromů apod.&nbsp;</p>",
            ),
            (
                "location_benefits",
                "<p>Chceme dos&aacute;hnout uk&aacute;zky spr&aacute;vn&eacute; praxe - dosažen&iacute; vzorov&eacute; - demonstračn&iacute; p&eacute;če o krajinn&eacute; prvky.</p>",
            ),
            (
                "personal_benefits",
                "<p>Dostane&scaron; př&iacute;ležitost dovz&iacute;dat se nov&eacute; věci a zkoumat o adaptac&iacute;ch krajiny na klimatickou změnu. Uvid&iacute;&scaron;, jak tyto prvky v krajině funguj&iacute; a jak&eacute; možnosti jako jednotlivci m&aacute;me.&nbsp;</p>",
            ),
            (
                "requirements",
                "<p>Chuť zaj&iacute;mat se o fungov&aacute;n&iacute; krajiny a ře&scaron;en&iacute; aktu&aacute;ln&iacute;ch environment&aacute;ln&iacute;ch probl&eacute;mů. V př&iacute;padě poř&aacute;d&aacute;n&iacute; akc&iacute; zku&scaron;enost s dobrovolnick&yacute;mi akcemi (alespoň na &uacute;rovni &uacute;častnick&eacute;).</p>",
            ),
            ("contact_name", "Petr Marada"),
            ("contact_phone", ""),
            ("contact_email", "marada@mendelu.cz"),
            ("image", "/media/opportunity_images/210616_02_petr-marada_10_2500px.jpg"),
            ("category_id", 3),
            ("location_id", 2163),
            ("contact_person_id", ("00f3b097-aea5-4095-b142-7ffe0009fcb7")),
        ]
    ),
    OrderedDict(
        [
            ("id", 19),
            ("name", "Kutiny na Tišnovsku"),
            ("start", "2023-06-01"),
            ("end", "2023-08-30"),
            ("on_web_start", "2023-01-01"),
            ("on_web_end", "2023-06-16"),
            (
                "introduction",
                "<p>Přidejte se k ochraně stepn&iacute; př&iacute;rodn&iacute; pam&aacute;tky pln&eacute; jalovců, prořez&aacute;vce březov&eacute;ho lesa a večerům u ohně. Zapoj se do obnovy svažit&eacute; stepn&iacute; vegetace Př&iacute;rodn&iacute; pam&aacute;tky Pl&aacute;ně a světl&yacute;ch lesů na Ti&scaron;novsku. Ček&aacute; na tebe smyslupln&aacute; pr&aacute;ce, span&iacute; na seně a klidn&aacute; př&iacute;roda v &uacute;dol&iacute; kousek za Brnem.&nbsp;&nbsp;</p>",
            ),
            (
                "description",
                "<p>Uspoř&aacute;dej v&iacute;kendovku nebo jednodenn&iacute; akci na ochranu př&iacute;rody cenn&eacute;ho stanovi&scaron;tě mnoha bezobratl&yacute;ch živoč&iacute;chů a rostlin. M&iacute;stn&iacute; znalci tě zasvět&iacute; do zdej&scaron;&iacute; př&iacute;rody a v&yacute;znamu dobrovolnick&eacute; činnosti.</p>\r\n<p>K z&aacute;zem&iacute; akce lze využ&iacute;t star&scaron;&iacute; dům v nedalek&eacute; osadě Kutiny. Přehnan&eacute;ho luxusu se ale neob&aacute;vej, span&iacute; je na seně ve stodole nebo na louce pod &scaron;ir&aacute;kem. Z&aacute;zem&iacute; domu s kadibudkou, studenou vodou z hadice a teplo z kamen.&nbsp;</p>",
            ),
            (
                "location_benefits",
                "<p>Pomůžete s p&eacute;č&iacute; o lokalitu, kter&aacute; m&aacute; potenci&aacute;l st&aacute;t se &uacute;toči&scaron;těm mnoha vz&aacute;cn&yacute;ch brzobratl&yacute;ch živočichů a rostlin. Vedle p&eacute;če o př&iacute;rodn&iacute; pam&aacute;tku je možnost zapojit se do přeměny smrkov&eacute;ho lesa ve světl&yacute; pařezinov&yacute; les, č&iacute;mž opět podpoř&iacute;me m&iacute;stn&iacute; biodiverzitu a stabilitu ekosyst&eacute;mu.&nbsp;</p>",
            ),
            (
                "personal_benefits",
                "<p>Z&iacute;sk&aacute;&scaron; cenn&eacute; zku&scaron;enosti s poř&aacute;d&aacute;n&iacute;m dobrovolnick&yacute;ch nebo dobrovolnicko z&aacute;žitkov&yacute;ch akc&iacute; a&nbsp;<strong>praktick&eacute; zku&scaron;enosti s p&eacute;č&iacute; o př&iacute;rodn&iacute; lokalitu.</strong></p>\r\n<p>Pro samotn&eacute; poř&aacute;d&aacute;n&iacute; akc&iacute; je na lokalitě v&yacute;hodu spolupr&aacute;ce se spr&aacute;vcem lokality a spolkem ČSOP, kter&yacute; se o lokalitu star&aacute; a může prakticky i odborně za&scaron;t&iacute;tit dobrovolnickou činnost.&nbsp;</p>",
            ),
            (
                "requirements",
                "<p>Zku&scaron;enost s dobrovolnick&yacute;mi akcemi pro př&iacute;rodu (alespoň v podobě &uacute;časti), komunikačn&iacute; schopnosti a t&yacute;mvov&aacute; spolupr&aacute;ce, v př&iacute;padě organizace v&iacute;kendov&eacute; akce kvalifikace Organiz&aacute;tor v&iacute;kendovek HB alespoň jednoho člena t&yacute;mu.&nbsp;</p>",
            ),
            ("contact_name", "Tereza Opravilová"),
            ("contact_phone", "+420 736 720 568"),
            ("contact_email", "akce-priroda@brontosaurus.cz"),
            (
                "image",
                "/media/opportunity_images/AF1QipMiyDLYA_z1B8hiqUwpivJUy1Aa4eqJSwpzYYhcw4032-h3024_mEbRnOK.jpg",
            ),
            ("category_id", 3),
            ("location_id", 2164),
            ("contact_person_id", ("3376af7f-452a-4692-88a0-b501caab8481")),
        ]
    ),
    OrderedDict(
        [
            ("id", 20),
            ("name", "Organizátorský tým pro mezinárodní dobrovolnický tábor"),
            ("start", "2023-07-01"),
            ("end", "2023-08-30"),
            ("on_web_start", "2023-01-01"),
            ("on_web_end", "2023-07-30"),
            (
                "introduction",
                '<p><span style="font-weight: 400;">Klasick&eacute; letn&iacute; dobrovolnick&eacute; t&aacute;bory Hnut&iacute; Brontosaurus jsme roz&scaron;&iacute;řili o 3 nov&eacute;, mezin&aacute;rodn&iacute; t&aacute;bory i pro &uacute;častn&iacute;ky ze zahranič&iacute;. Zapoj se do jedinečn&eacute; př&iacute;ležitosti pr&aacute;vě teď!</span></p>',
            ),
            (
                "description",
                '<p><span style="font-weight: 400;">Přes l&eacute;to 2023 pl&aacute;nujeme zorganizovat 3 mezin&aacute;rodn&iacute; letn&iacute; t&aacute;bory a aktu&aacute;lně hled&aacute;me </span><strong>organiz&aacute;torsk&yacute; t&yacute;m</strong><span style="font-weight: 400;"> (3 nad&scaron;en&eacute; lidi) pro jeden z nich.&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">Organiz&aacute;torsk&yacute; t&yacute;m společně s pomoc&iacute; na&scaron;ich zahraničn&iacute;ch ESC dobrovoln&iacute;ků zorganizuje </span><strong>14 denn</strong><span style="font-weight: 400;">&iacute; </span><strong>dobrovolnick&yacute; t&aacute;bo</strong><span style="font-weight: 400;">r pro celkem </span><strong>20 &uacute;častn&iacute;ků</strong><span style="font-weight: 400;"> (13 z Česka a 7 ze zahranič&iacute;). T&aacute;bor zat&iacute;m nem&aacute; přesn&yacute; datum ani lokalitu, nech&aacute;v&aacute;me to pr&aacute;vě na v&aacute;s a va&scaron;e časov&eacute; možnosti, měl by v&scaron;ak b&yacute;t v druh&eacute; polovině července (16.7. - 2.8.) nebo někdy na konci srpna (17.8. - 10.9.).&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">Tvoje činnost bude spoč&iacute;vat zejm&eacute;na:&nbsp;</span></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">&Uacute;čast na t&yacute;movk&aacute;ch</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Aktivn&iacute; př&iacute;prava programu&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Př&iacute;tomnost na t&aacute;boře na cel&yacute;ch 14 dn&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Koordinace pr&aacute;ce, komunikace s &uacute;častn&iacute;ky, realizace programu&hellip;</span></li>\r\n</ul>',
            ),
            (
                "location_benefits",
                '<p><span style="font-weight: 400;">Lokalita je zcela na v&yacute;běru organiz&aacute;torsk&eacute;ho t&yacute;mu. Př&iacute;nos bude velk&yacute;, pracovat budeme nejm&eacute;ně 7 dn&iacute; po dobu 4 - 8 hodin/den. </span></p>',
            ),
            (
                "personal_benefits",
                '<p><span style="font-weight: 400;">Dobrovolnick&yacute; t&aacute;bor Evropsk&eacute;ho sboru solidarity přin&aacute;&scaron;&iacute; množstvo v&yacute;hod pro jednotlivce z organiz&aacute;torsk&eacute;ho t&yacute;mu i pro ZČ kter&yacute; zastupuje&scaron;</span></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Dobr&yacute; pocit z pomoci na lokalitě</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Potk&aacute;&scaron; nov&eacute; lidi z Česka ale i ze zahranič&iacute;&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Zlep&scaron;&iacute;&scaron; svoji angličtinu</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Za sv&eacute; nasazen&iacute; z&iacute;sk&aacute;&scaron; evropsk&yacute; certifik&aacute;t &ldquo;Youth Pass&rdquo;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Dostane&scaron; kapesn&eacute; a stravn&eacute; na každ&yacute; den</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Stane&scaron; se souč&aacute;st&iacute; t&yacute;mu organiz&aacute;torů a organiz&aacute;torek mezin&aacute;rodn&iacute;ch aktivit Hnut&iacute; Brontosaurus</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Podpoř&iacute;me tě men&scaron;&iacute; finančn&iacute; kompenzac&iacute; za čas str&aacute;ven&yacute; na př&iacute;prav&aacute;ch</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Rovnako podpoř&iacute;me tvůj ZČ nov&yacute;m vybaven&iacute;m a materi&aacute;lem</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Nauč&iacute;&scaron; se postupy důležit&eacute; pro organizov&aacute;n&iacute; mezin&aacute;rodn&iacute;ch eventov</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">A mnoho dal&scaron;&iacute;ho :)&nbsp;</span></li>\r\n</ul>',
            ),
            (
                "requirements",
                '<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Alespoň z&aacute;kladn&iacute; znalost angličtiny</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Chuť pomoci a aktivn&iacute;ho zapojen&iacute;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Př&iacute;tomnost na t&aacute;boře na cel&yacute;ch 14 dn&iacute;&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">&Uacute;čast na velk&eacute;m společn&eacute;m pl&aacute;nov&aacute;n&iacute; v&scaron;ech tř&iacute; t&aacute;borů o v&iacute;kendu 10.-12.3.2023&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">Nad&scaron;en&iacute;, spolupr&aacute;ce skrz cel&eacute; Hnut&iacute; Brontosaurus</span></li>\r\n</ul>',
            ),
            ("contact_name", "Veronika Vlačuhová"),
            ("contact_phone", "+420 734 392 735"),
            ("contact_email", "international@brontosaurus.cz"),
            ("image", "/media/opportunity_images/srovnej_si_je3.jpeg"),
            ("category_id", 1),
            ("location_id", 102),
            ("contact_person_id", ("df118bc3-ed5d-4985-9482-df402417a6eb")),
        ]
    ),
    OrderedDict(
        [
            ("id", 21),
            ("name", "Pomoc s organizací výstavy celostátní soutěže Máme rádi přírodu"),
            ("start", "2023-01-17"),
            ("end", "2023-01-28"),
            ("on_web_start", "2023-01-01"),
            ("on_web_end", "2023-01-28"),
            (
                "introduction",
                '<p><span style="font-weight: 400;">Chce&scaron; se zapojit do organiz&aacute;torsk&eacute;ho t&yacute;mu a l&aacute;k&aacute; tě vět&scaron;&iacute; akce? Co třeba rovnou akce celost&aacute;tn&iacute;ho rozměru? Nem&aacute;&scaron; čas se zapojit do dlouhodoběj&scaron;&iacute;ho spolupr&aacute;ce? Pojď n&aacute;m pomoci s organizac&iacute; v&yacute;stavy a slavnostn&iacute;ho před&aacute;v&aacute;n&iacute; cen v r&aacute;mci celost&aacute;tn&iacute; soutěže M&Aacute;ME R&Aacute;DI PŘ&Iacute;RODU!</span></p>',
            ),
            (
                "description",
                '<p><span style="font-weight: 400;">Bl&iacute;ž&iacute; se vyhl&aacute;&scaron;en&iacute; v&yacute;sledků kreativn&iacute; soutěže M&aacute;me r&aacute;di př&iacute;rodu. M&aacute;me r&aacute;di př&iacute;rodu&ldquo; je celost&aacute;tn&iacute; soutěž pro děti a ml&aacute;dež do 19 let, kterou poř&aacute;d&aacute; Hnut&iacute; Brontosaurus. Soutěž m&aacute; dlouholetou tradici, je organizov&aacute;na již od roku 1992. Soutěž si klade za &uacute;kol v prvn&iacute; řadě podpořit z&aacute;jem o př&iacute;rodu a p&eacute;či o ni. Je určena pro v&scaron;echny milovn&iacute;ky př&iacute;rody, kteř&iacute; z&aacute;roveň i r&aacute;di něco tvoř&iacute;. Se sv&yacute;mi v&yacute;tvarn&yacute;mi a liter&aacute;rn&iacute;mi d&iacute;ly, fotografiemi a bezva ekof&oacute;ry se j&iacute; &uacute;častn&iacute; děti a ml&aacute;dež (od M&Scaron; po S&Scaron;) z cel&eacute; ČR. Letos se se&scaron;lo neuvěřiteln&yacute;ch </span><span style="font-weight: 400;">&nbsp;2 150 děl. Teď n&aacute;s ček&aacute; slavnostn&iacute; </span><span style="font-weight: 400;">vyhl&aacute;&scaron;en&iacute; v&yacute;sledků a před&aacute;v&aacute;n&iacute;&nbsp; cen, na kter&eacute; se sjedou &uacute;častn&iacute;ci soutěže z cel&eacute; republiky. </span></p>\r\n<p><span style="font-weight: 400;">Nev&aacute;hej a přidej se do organiz&aacute;torsk&eacute;ho t&yacute;mu! Hled&aacute;me pomocn&iacute;ky, kteř&iacute; pomůžou na m&iacute;stě při slavnostn&iacute;m vyhl&aacute;&scaron;en&iacute; v&yacute;sledků a před&aacute;v&aacute;n&iacute;&nbsp; cen.&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">Možnosti zapojen&iacute;:</span></p>\r\n<ul>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">pomoc s organizov&aacute;n&iacute;m vyhl&aacute;&scaron;en&iacute; v&yacute;sledků&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">pomoc s doprovodn&yacute;m programem - d&iacute;lny pro děti</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">pomoc s před&aacute;v&aacute;n&iacute;m cen&nbsp;</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">komunikace s rodiči, dětmi a učiteli</span></li>\r\n<li style="font-weight: 400;" aria-level="1"><span style="font-weight: 400;">fotograf</span></li>\r\n</ul>',
            ),
            ("location_benefits", ""),
            (
                "personal_benefits",
                '<p><span style="font-weight: 400;">Načerp&aacute;&scaron; zku&scaron;enosti z organizace akce celost&aacute;tn&iacute;ho rozměru.&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">Podpoř&iacute;&scaron; z&aacute;jem o př&iacute;rodu a p&eacute;či o ni u dět&iacute; a ml&aacute;deže např&iacute;č celou republikou.</span></p>\r\n<p><span style="font-weight: 400;">Stane&scaron; se souč&aacute;st&iacute; zku&scaron;en&eacute;ho t&yacute;mu organiz&aacute;torů.</span></p>\r\n<p><span style="font-weight: 400;">Z&iacute;sk&aacute;&scaron; přehled v dal&scaron;&iacute; činnosti v r&aacute;mci Hnut&iacute; Brontosaurus.&nbsp;</span></p>\r\n<p><span style="font-weight: 400;">Organizaci soutěže může&scaron; pojmout jako praxi při studiu na v&scaron;.</span></p>\r\n<p><span style="font-weight: 400;">Pozn&aacute;&scaron; nov&eacute; lidi. </span></p>',
            ),
            (
                "requirements",
                '<p><span style="font-weight: 400;">Chuť pomoci a aktivn&iacute; zapojen&iacute; :) </span></p>',
            ),
            ("contact_name", "Jitka Rajmonová"),
            ("contact_phone", "+420 732 882 032"),
            ("contact_email", "mrp@brontosaurus.cz"),
            ("image", "/media/opportunity_images/DSC_0423_5WndFS8.JPG"),
            ("category_id", 2),
            ("location_id", 102),
            ("contact_person_id", ("001a1495-012e-4ec2-835d-4d4c29532372")),
        ]
    ),
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        Opportunity.objects.all().delete()

        for item in data:
            item["contact_person_id"] = User.objects.all().first().id
            item["location_id"] = Location.objects.all().first().id
            item["image"] = "/app" + item["image"]
            Opportunity.objects.create(**item)
