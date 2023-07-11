// This file was automatically generated with a script.
//
// !!!DO NOT EDIT!!!
//
// You can generate it again with `yarn generate-translations` or `yarn gt` for short.
// The script is defined in `bin/generateTranslations.ts`

export const baseAddress = { _name: 'Adresa', _name_plural: 'Adresa' } as const

export const baseContact = {
  _name: 'Kontakt',
  _name_plural: 'Kontakt',
} as const

export const location = {
  _name: 'Lokalita',
  _name_plural: 'Lokalita',
  name: 'Název lokality',
  patron: 'Kontakt v hnutí',
  contact_person: 'Kontakt na lokalitě',
  for_beginners: 'Vhodné pro začínající organizátory?',
  is_full: 'Je lokalita plně vytížená?',
  is_unexplored: 'Je lokalita nová/nevyužívaná?',
  program: 'Program lokality',
  accessibility_from_prague: 'Dostupnost z Prahy',
  accessibility_from_brno: 'Dostupnost z Brna',
  volunteering_work: 'Práce na lokalitě',
  volunteering_work_done: 'Čeho jsme na lokalitě dosáhli',
  volunteering_work_goals: 'Čeho chceme dosáhnout / péče o lokalitu',
  options_around: 'Možnosti programu a vzdělávání',
  facilities: 'Zázemí',
  address: 'Adresa',
  web: 'Web',
  gps_location: 'GPS lokace',
  is_fully_specified: 'Plnohodnotná lokalita?',
} as const

export const locationPhoto = {
  _name: 'Fotka lokality',
  _name_plural: 'Fotka lokality',
} as const

export const locationContactPerson = {
  _name: 'Kontakt na lokalitě',
  _name_plural: 'Kontakt na lokalitě',
} as const

export const locationPatron = {
  _name: 'Kontakt v hnutí',
  _name_plural: 'Kontakt v hnutí',
} as const

export const user = {
  _name: 'Uživatel',
  _name_plural: 'Uživatel',
  vokativ: 'Vokativ',
  email_exists: 'Je e-mail skutečný?',
  is_active: 'Může se uživatel přihlásit?',
  date_joined: 'Datum vzniku uživatelského profilu',
  close_person: 'Rodič / blízká osoba',
  health_insurance_company: 'Pojišťovna',
  roles: 'Role',
  internal_note: 'Poznámka ústředí',
  subscribed_to_newsletter: 'Odebírá novinky?',
} as const

export const userClosePerson = {
  _name: 'Rodič / blízká osoba',
  _name_plural: 'Rodič / blízká osoba',
} as const

export const userAddress = {
  _name: 'Adresa uživatele',
  _name_plural: 'Adresa uživatele',
} as const

export const eYCACard = {
  _name: 'EYCA karta',
  _name_plural: 'EYCA karta',
  photo: 'Fotka',
  number: 'Číslo kartičky',
  submitted_for_creation: 'Předáno k výrobě',
  sent_to_user: 'Odesláno uživateli',
  valid_till: 'Platnost do',
} as const

export const userContactAddress = {
  _name: 'Kontaktní adresa uživatele',
  _name_plural: 'Kontaktní adresa uživatele',
} as const

export const userEmail = {
  _name: 'E-mail uživatele',
  _name_plural: 'E-mail uživatele',
} as const

export const duplicateUser = {
  _name: 'Duplicita',
  _name_plural: 'Duplicita',
  user: [
    'Primární uživatel',
    'Tento uživatel (by měl) obsahovat aktuání informace',
  ],
  other: [
    'Duplicitní uživatel',
    'Tento uživatel (by měl) být zastaralý, jeho informace budou (po kontrole) připojeny k primárnímu (vybranému) uživateli',
  ],
} as const

export const administrationUnit = {
  _name: 'Organizační jednotka',
  _name_plural: 'Organizační jednotka',
  name: ['Oficiální název', 'Název z rejstříku, např. ZČ HB Zvonek'],
  abbreviation: [
    'Zkrácený název',
    'Běžně užívaný název, např. Zvonek, Orchis...',
  ],
  phone: 'Telefon',
  category: 'Typ jednotky',
  board_members: 'Členové představenstva',
  bank_account_number: 'Číslo účtu',
  chairman: 'Předseda',
  vice_chairman: 'Místopředseda',
  existed_since: 'Datum vzniku',
  existed_till: 'Datum zániku',
  ic: 'IČO',
  is_for_kids: 'Jedná se o BRĎO oddíl?',
  manager: 'Hospodář',
  www: 'Webové stránky',
  custom_statues: 'Vlastní stanovy',
  data_box: 'Datová schránka',
  facebook: 'Facebook',
  instagram: 'Instagram',
  gps_location: 'GPS lokace',
} as const

export const administrationUnitAddress = {
  _name: 'Adresa',
  _name_plural: 'Adresa',
  administration_unit: 'Organizační jednotka',
} as const

export const administrationUnitContactAddress = {
  _name: 'Kontaktní adresa',
  _name_plural: 'Kontaktní adresa',
  administration_unit: 'Organizační jednotka',
} as const

export const generalMeeting = {
  _name: 'Valná hromada',
  _name_plural: 'Valná hromada',
  administration_unit: 'Organizační jednotka',
} as const

export const brontosaurusMovement = {
  _name: 'Přístupy',
  _name_plural: 'Přístupy',
  director: ['Programový ředitel', 'Má veškerá oprávnění'],
  finance_director: ['Finanční ředitel', 'Má veškerá oprávnění'],
  bis_administrators: ['Správci BISu', 'Mají veškeré oprávnění'],
  office_workers: [
    'Pracovníci ústředí',
    'Mohou měnit vše kromě základních oprávnění',
  ],
  audit_committee: [
    'KRK - Kontrolní a revizní komise',
    'Vidí vše, nemohou editovat',
  ],
  executive_committee: ['VV - Výkonný výbor', 'Vidí vše, nemohou editovat'],
  education_members: [
    'EDU - konzultanti a instruktoři',
    'Vidí pouze uživatele a mohou editovat pouze jejich kvalifikaci',
  ],
} as const

export const membership = {
  _name: 'Členství',
  _name_plural: 'Členství',
  administration_unit: 'Organizační jednotka',
  year: 'Členství v roce',
  category: 'Typ',
} as const

export const qualification = {
  _name: 'Kvalifikace',
  _name_plural: 'Kvalifikace',
  category: 'Typ kvalifikace',
  valid_till: 'Platnost do',
  valid_since: 'Platnost od',
  approved_by: 'Schválilo',
} as const

export const event = {
  _name: 'Akce',
  _name_plural: 'Akce',
  group: 'Druh',
  category: 'Typ',
  internal_note: 'Privátní poznámka',
  program: 'Program',
  intended_for: 'Pro koho?',
  location: ['Lokalita', 'Zobrazí se na webu jako místo konání akce'],
  is_canceled: ['Je akce zrušena?', 'Akce se nebude konat / nekonala'],
  is_complete: [
    'Vše vyplněno?',
    'Příznak, zda-li jsou všechny povinné údaje po akci vyplněny',
  ],
  is_closed: [
    'Je akce uzavřena?',
    'Uzavřená akce nelze editovat, je archivována',
  ],
  start: 'Začátek akce',
  start_time: 'Čas začátku akce',
  end: 'Konec akce',
  duration: 'Délka trvání akce',
  online_link: [
    'Webová adresa pro připojení',
    'Vyplňte, pokud se akce koná online',
  ],
  number_of_sub_events: 'Počet akcí v uvedeném období',
  administration_units: 'Organizační jednotky',
  main_organizer: 'Hlavní organizátor',
  other_organizers: 'Další organizátoři',
  is_attendance_list_required: 'Je prezenční listina vyžadována?',
  vip_propagation: 'Je akce propagována v rámci VIP propagace?',
} as const

export const eventFinance = {
  _name: 'Finance akce',
  _name_plural: 'Finance akce',
  category: 'Kategorie dle financí',
  grant_category: 'Typ grantu',
  grant_amount: 'Přidělené dotace',
  total_event_cost: 'Celkové náklady akce',
  budget: 'Rozpočet',
  bank_account_number: ['Číslo bankvního účtu', 'Pro zaslání dotací'],
} as const

export const eventFinanceReceipt = {
  _name: 'Účtenka',
  _name_plural: 'Účtenka',
  finance: 'Finance akce',
  receipt: 'Účtenky',
} as const

export const eventPropagation = {
  _name: 'Propagace akce',
  _name_plural: 'Propagace akce',
  is_shown_on_web: 'Je akce zobrazena na webu?',
  minimum_age: 'Minimální věk',
  maximum_age: 'Maximální věk',
  cost: [
    'Účastnický poplatek',
    'Max. 12 znaků, "Kč" je doplněno automaticky, nechte prázdné pokud je akce bez poplatku',
  ],
  diets: 'Možnosti stravování',
  _contact_url: 'Kontaktní url',
  accommodation: 'Ubytování',
  working_days: [
    'Počet pracovních dní',
    'Pouze pro vícedenní dobrovolnické akce',
  ],
  working_hours: [
    'Odpracovaných hodin (denně)',
    'Pouze pro dobrovolnické akce',
  ],
  organizers: 'Organizátoři (text do propagace)',
  web_url: 'Web akce',
  invitation_text_introduction: [
    'Zvací text: Co nás čeká?',
    'Základní informace o tvé akci. Popiš téma akce a nastiň, co se tam bude dít a jak budete pomáhat, co se účastník naučí nového. Prvních několik vět se zobrazí v přehledu akcí na webu. První věty jsou k upoutání pozornosti nejdůležitější, proto se na ně zaměř a shrň ve 2-4 větách na co se účastníci mohou těšit.',
  ],
  invitation_text_practical_information: [
    'Zvací text: Co, kde a jak',
    'Stručný popis programu akce – jakého typu budou aktivity na akci, kde se bude spát, co se bude jíst a další praktické záležitosti. Nezapomeň zdůraznit, zda bude program aktivní a plný zážitkového programu nebo bude spíše poklidnější nebo zaměřený na vzdělávání. Také napiš zda bude program fyzicky popř. psychicky náročný, aby účastníci věděli co mají čekat.',
  ],
  invitation_text_work_description: [
    'Zvací text: Dobrovolnická pomoc',
    'Stručně popiš dobrovolnickou činnost a její smysl pro přírodu, památky nebo lidi (např. „sázíme vrbky, aby měli místní ptáci kde hnízdit“). Zasaď dobrovolnickou pomoc do kontextu místa a jeho příběhu (např. “kosením pomůžeme udržet pestrost nejvzácnější louky unikátní krajiny Bílých Karpat, jež …” ). Napiš, co se při práci účastníci naučí a v čem je to může rozvinout. Přidej i další zajímavosti, které se vážou k dané dobrovolnické činnosti a lokalitě. Uveď kolik prostoru na akci se bude věnovat dobrovolnické činnosti a jak bude náročná.',
  ],
  invitation_text_about_us: [
    'Zvací text: Malá ochutnávka',
    'Malá ochutnávka uvádí fotky, které k akci přiložíte. Popište fotky, které přikládáte nebo přibližte jak vypadaly akce na stejném místě v minulosti. U nových akcí můžete více ukázat místo a důvody proč vás oslovilo a představit organizátory.',
  ],
  contact_name: [
    'Jméno kontaktní osoby',
    'Nechte prázdné pokud chcete použít jméno kontaktní osoby',
  ],
  contact_phone: [
    'Kontaktní telefon',
    'Nechte prázdné pokud chcete použít telefon kontaktní osoby',
  ],
  contact_email: [
    'Kontaktní e-mail',
    'Nechte prázdné pokud chcete použít e-mail kontaktní osoby',
  ],
} as const

export const vIPEventPropagation = {
  _name: 'VIP propagace akce',
  _name_plural: 'VIP propagace akce',
  event_propagation: 'Propagace',
  goals_of_event: [
    'Cíle akce a přínos pro prvoúčastníky',
    'Jaké je hlavní téma vaší akce? Jaké jsou hlavní cíle akce? Co nejvýstižněji popište, co akce přináší účastníkům, co zajímavého si zkusí, co se dozví, naučí, v čem se rozvinou...',
  ],
  program: [
    'Programové pojetí akce pro prvoúčastníky',
    'V základu uveďte, jak bude vaše akce programově a dramaturgicky koncipována (motivační příběh, zaměření programu – hry, diskuse, řemesla,...). Uveďte, jak náplň a program akce reflektují potřeby vaší cílové skupiny prvoúčastníků.',
  ],
  rover_propagation: [
    'Propagovat akci v Roverském kmeni?',
    'Placená propagace vaší vícedenní akce v časopisu Roverský kmen za poplatek 100 Kč.',
  ],
  short_invitation_text: [
    'Krátký zvací text do propagace',
    'Ve 2-4 větách nalákejte na vaši akci a zdůrazněte osobní přínos pro účastníky (max. 200 znaků).',
  ],
} as const

export const eventRegistration = {
  _name: 'Přihlášení',
  _name_plural: 'Přihlášení',
  is_registration_required: 'Musí se účastníci na akci přihlásit?',
  is_event_full: 'Je akce plná?',
  questionnaire: 'Dotazník',
  alternative_registration_link: 'Alternativní adresa pro přihlášení',
} as const

export const eventRecord = {
  _name: 'Záznam z akce',
  _name_plural: 'Záznam z akce',
  total_hours_worked: 'Odpracováno člověkohodin',
  comment_on_work_done: 'Okomentování vykonané práce',
  attendance_list_pages: 'Prezenční listina',
  participants: 'Účastníci',
  note: 'Poznámka k akci',
  number_of_participants: [
    'Počet účastníků',
    'Vyplň pouze pokud nejsou vyplnění konkrétní účastníci',
  ],
  number_of_participants_under_26: [
    'Počet účastníků pod 26 let',
    'Vyplň pouze pokud nejsou vyplnění konkrétní účastníci',
  ],
} as const

export const eventContact = {
  _name: 'Zjednodušená prezenční listina z jednodenní akce',
  _name_plural: 'Zjednodušená prezenční listina z jednodenní akce',
  record: 'Záznam z akce',
} as const

export const eventPropagationImage = {
  _name: 'Obrázek k propagaci',
  _name_plural: 'Obrázek k propagaci',
  propagation: 'Propagace akce',
} as const

export const eventPhoto = {
  _name: 'Fotka z akce',
  _name_plural: 'Fotka z akce',
  record: 'Záznam z akce',
} as const

export const eventAttendanceListPage = {
  _name: 'Prezenční listina',
  _name_plural: 'Prezenční listina',
  record: 'Záznam z akce',
  page: 'Strana',
} as const

export const eventApplication = {
  _name: 'Přihláška na akci',
  _name_plural: 'Přihláška na akci',
  event_registration: 'Přihlášení na akci',
  state: 'Stav',
} as const

export const eventApplicationClosePerson = {
  _name: 'Rodič / blízká osoba',
  _name_plural: 'Rodič / blízká osoba',
} as const

export const eventApplicationAddress = {
  _name: 'Adresa',
  _name_plural: 'Adresa',
} as const

export const questionnaire = {
  _name: 'Dotazník',
  _name_plural: 'Dotazník',
  event_registration: 'Přihlášení na akci',
  introduction: 'Úvodní text dotazníku',
  after_submit_text: 'Text po zodpovězení dotazníku',
} as const

export const question = {
  _name: 'Otázka dotazníku',
  _name_plural: 'Otázka dotazníku',
  question: 'Otázka',
  data: 'Data',
  is_required: 'Povinná otázka?',
  questionnaire: 'Dotazník',
} as const

export const answer = {
  _name: 'Odpověď na otázku',
  _name_plural: 'Odpověď na otázku',
  question: 'Otázka',
  application: 'Přihláška na akci',
  answer: 'Odpověď',
  data: 'Data',
} as const

export const grantCategory = {
  _name: 'Typ grantu',
  _name_plural: 'Typ grantu',
} as const

export const eventIntendedForCategory = {
  _name: 'Kategorie zaměření propagace',
  _name_plural: 'Kategorie zaměření propagace',
} as const

export const dietCategory = {
  _name: 'Typ stravy',
  _name_plural: 'Typ stravy',
} as const

export const qualificationCategory = {
  _name: 'Typ kvalifikace',
  _name_plural: 'Typ kvalifikace',
  parents: 'Nadřazené kvalifikace',
  can_approve: 'Schvaluje kvalifikace',
} as const

export const administrationUnitCategory = {
  _name: 'Typ organizační jednotky',
  _name_plural: 'Typ organizační jednotky',
} as const

export const membershipCategory = {
  _name: 'Členství',
  _name_plural: 'Členství',
} as const

export const eventGroupCategory = {
  _name: 'Druh akce',
  _name_plural: 'Druh akce',
} as const

export const eventCategory = {
  _name: 'Typ akce',
  _name_plural: 'Typ akce',
} as const

export const eventProgramCategory = {
  _name: 'Program akce',
  _name_plural: 'Program akce',
} as const

export const donationSourceCategory = {
  _name: 'Zdroj dotace',
  _name_plural: 'Zdroj dotace',
} as const

export const organizerRoleCategory = {
  _name: 'Organizátorská role',
  _name_plural: 'Organizátorská role',
} as const

export const teamRoleCategory = {
  _name: 'Týmová role',
  _name_plural: 'Týmová role',
} as const

export const opportunityCategory = {
  _name: 'Kagegorie příležitosti',
  _name_plural: 'Kagegorie příležitosti',
} as const

export const locationProgramCategory = {
  _name: 'Program lokality',
  _name_plural: 'Program lokality',
} as const

export const locationAccessibilityCategory = {
  _name: 'Dostupnost lokality',
  _name_plural: 'Dostupnost lokality',
} as const

export const roleCategory = {
  _name: 'Typ role',
  _name_plural: 'Typ role',
} as const

export const healthInsuranceCompany = {
  _name: 'Zdravotní pojišťovna',
  _name_plural: 'Zdravotní pojišťovna',
} as const

export const pronounCategory = {
  _name: 'Oslovení',
  _name_plural: 'Oslovení',
} as const

export const donor = {
  _name: 'Dárce',
  _name_plural: 'Dárce',
  subscribed_to_newsletter: 'Odebírá novinky?',
  is_public: ['Chce zveřejnit?', 'na webu a v závěrečné zprávě'],
  date_joined: 'Dárcem od',
  regional_center_support: 'podpora RC',
  basic_section_support: 'podpora ZČ',
  has_recurrent_donation: 'Pravidelný dárce',
  internal_note: 'Interní poznámka',
} as const

export const donation = {
  _name: 'Dar',
  _name_plural: 'Dar',
  donor: 'Dárce',
  donated_at: 'Datum',
  amount: 'Částka',
  donation_source: 'Zdroj dotace',
  info: 'Info',
  _variable_symbol: ['Variabilní symbol platby', 'pro párování na dárce'],
} as const

export const variableSymbol = {
  _name: 'Variabilní symbol',
  _name_plural: 'Variabilní symbol',
  donor: 'Dárce',
  variable_symbol: 'Variabilní symbol',
} as const

export const uploadBankRecords = {
  _name: 'Nahrání bankovních záznamů',
  _name_plural: 'Nahrání bankovních záznamů',
  file: 'Soubor .csv',
} as const

export const region = {
  _name: 'Kraj',
  _name_plural: 'Kraj',
  area: 'Oblast',
} as const

export const zipCode = { _name: 'PSČ', _name_plural: 'PSČ' } as const

export const opportunity = {
  _name: 'Příležitost',
  _name_plural: 'Příležitost',
  category: 'Kategorie',
  start: 'Začátek příležitosti',
  end: 'Konec příležitosti',
  on_web_start: 'Zobrazit na webu od',
  on_web_end: 'Zobrazit na webu do',
  location: 'Místo příležitosti',
  introduction: [
    'Představení příležitosti',
    'Krátce vysvětli význam činnosti a její přínos, aby přilákala zájemce',
  ],
  description: [
    'Popis činnosti',
    'Přibliž konkrétní činnosti a aktivity, které budou součástí příležitosti',
  ],
  location_benefits: [
    'Přínos pro lokalitu',
    'Popiš dopad a přínos činnosti pro dané místě (nezobrazí se u typu spolupráce)',
  ],
  personal_benefits: [
    'Přínos ze spolupráce',
    'Uveď konkrétní osobní přínos do života z realizace této příležitosti',
  ],
  requirements: [
    'Požadavky příležitosti',
    'Napiš dovednosti, zkušenosti či vybavení potřebné k zapojení do příležitosti',
  ],
  contact_person: 'Kontaktní osoba',
  contact_name: [
    'Jméno kontaktní osoby',
    'Nechte prázdné pokud chcete použít jméno kontaktní osoby',
  ],
  contact_phone: [
    'Kontaktní telefon',
    'Nechte prázdné pokud chcete použít telefon kontaktní osoby',
  ],
  contact_email: [
    'Kontaktní e-mail',
    'Nechte prázdné pokud chcete použít e-mail kontaktní osoby',
  ],
} as const

export const offeredHelp = {
  _name: 'Nabízená pomoc',
  _name_plural: 'Nabízená pomoc',
  programs: 'Programy',
  organizer_roles: 'Organizátorské role',
  additional_organizer_role: 'Jiná organizátorské role',
  team_roles: 'Týmové role',
  additional_team_role: 'Jiné týmové role',
  info: 'Popis pomoci',
} as const

export const feedback = {
  _name: 'Zpětná vazba',
  _name_plural: 'Zpětná vazba',
  feedback: 'Zpětná vazba',
  is_resolved: 'Zpracována?',
} as const

export const dashboardItem = {
  _name: 'Termín',
  _name_plural: 'Termín',
  for_roles: 'Pro role',
  repeats_every_year: 'Opakuje se každý rok?',
} as const

export const game = {
  _name: 'Program',
  _name_plural: 'Program',
  is_hidden: [
    'Je program skrytý?',
    'Editor může program skrýt (autorské práva, nekorektní text, atd.)',
  ],
  created_at: 'Vytvořen',
  contributor: ['Přispěvatel', 'Kdo zadal program do sborníku?'],
  is_original: [
    'Autorský program?',
    'Jsi autorem tohoto programu — vytvořil si ho? Pokud ne, vyplň původ programu níže.',
  ],
  origin: [
    'Původ programu',
    'Kdo je autorem programu, odkud byl program převzat?',
  ],
  administration_unit: [
    'Zákldní článek (RC/klub)',
    'Chceš program přiřadit pod určitý článek? Dej mu kredit!',
  ],
  thumbs_up: 'Dali palec nahoru',
  favourites: 'Oblíbili si',
  watchers: 'Sledují',
  stars: ['Počet hvězd', 'Interní hodnocení pro editory'],
  is_verified: [
    'Je program ověřen?',
    'Editor může program ověřit, záruka brontosauří kvality',
  ],
  tags: [
    'Tagy',
    'Pokud ti nějaký tag chybí, napiš mi na sbornik@brontosaurus.cz, díky!',
  ],
  physical_category: 'Fyzická náročnost',
  physical_note: ['Poznámky', 'Specifické poznámky k fyzické náročnosti'],
  mental_category: 'Psychická náročnost',
  mental_note: ['Poznámky', 'Specifické poznámky k psychické náročnosti'],
  location_category: [
    'Místa uvedení',
    'Typová místa, na kterých lze / dává smysl program uvést',
  ],
  location_note: ['Poznámky', 'Specifické poznámky k místu uvedení'],
  participant_number_category: 'Vhodný počet účastníků',
  participant_number_note: [
    'Poznámky',
    'Specifické poznámky k počtu účastníků',
  ],
  participant_age_category: 'Vhodný věk účastníků',
  participant_age_note: ['Poznámky', 'Specifické poznámky k věku účastníků'],
  game_length_category: 'Délka programu',
  game_length_note: ['Poznámky', 'Specifické poznámky k délce programu'],
  preparation_length_category: 'Délka přípravy',
  preparation_length_note: [
    'Poznámky',
    'Specifické poznámky k délce / náročnosti přípravy programu',
  ],
  material_requirement_category: 'Množství materiálu',
  material_requirement_note: [
    'Poznámky',
    'Specifické poznámky k množství materiálu',
  ],
  organizers_number_category: 'Počet orgů pro uvedení',
  organizers_number_note: [
    'Poznámky',
    'Specifické poznámky k počtu orgů pro uvedení programu',
  ],
  short_description: ['Krátké představení', 'Maximálně 250 znaků'],
  goal: 'Cíle programu',
  description: ['Pravidla', 'Popis a pravidla programu'],
  motivation: [
    'Motivace',
    'Tipy na vtáhnutí účastníků do hry (scénkou, hudbou, aktivitkou)',
  ],
  material: [
    'Soupis materiálu',
    'Co je potřeba k uvedení hry, soubory pro tisk lze přiložit níže',
  ],
  notes: [
    'Metodické poznámky',
    'Tipy a triky pro uvedení, otázky na reflexi, atd.',
  ],
} as const

export const baseFile = {
  _name: 'Soubor',
  _name_plural: 'Soubor',
  file: 'Soubor',
} as const

export const gameFile = { _name: 'Soubor', _name_plural: 'Soubor' } as const

export const comment = {
  _name: 'Komentář',
  _name_plural: 'Komentář',
  author: 'Autor',
  is_hidden: 'Je skrytý?',
} as const

export const commentFile = { _name: 'Soubor', _name_plural: 'Soubor' } as const

export const playedAt = {
  _name: 'Uvedení programu',
  _name_plural: 'Uvedení programu',
} as const

export const playedAtFile = {
  _name: 'Soubor',
  _name_plural: 'Soubor',
  played_at: 'Uvedení programu',
} as const

export const gameList = {
  _name: 'Seznam programů',
  _name_plural: 'Seznam programů',
  games: 'Programy',
  owner: 'Autor seznamu',
} as const

export const tag = { _name: 'Tag', _name_plural: 'Tag' } as const

export const baseCategory = {
  _name: 'Kategorie',
  _name_plural: 'Kategorie',
} as const

export const physicalCategory = {
  _name: 'Kategorie fyzické náročnosti',
  _name_plural: 'Kategorie fyzické náročnosti',
} as const

export const mentalCategory = {
  _name: 'Kategorie psychické náročnosti',
  _name_plural: 'Kategorie psychické náročnosti',
} as const

export const locationCategory = {
  _name: 'Kategorie místa uvedení',
  _name_plural: 'Kategorie místa uvedení',
} as const

export const participantNumberCategory = {
  _name: 'Kategorie početu účastníků',
  _name_plural: 'Kategorie početu účastníků',
} as const

export const participantAgeCategory = {
  _name: 'Kategorie věku účastníků',
  _name_plural: 'Kategorie věku účastníků',
} as const

export const gameLengthCategory = {
  _name: 'Kategorie délky programu',
  _name_plural: 'Kategorie délky programu',
} as const

export const preparationLengthCategory = {
  _name: 'Kategorie délky přípravy',
  _name_plural: 'Kategorie délky přípravy',
} as const

export const materialRequirementCategory = {
  _name: 'Kategorie množství materiálu',
  _name_plural: 'Kategorie množství materiálu',
} as const

export const organizersNumberCategory = {
  _name: 'Kategorie početu orgů pro uvedení',
  _name_plural: 'Kategorie početu orgů pro uvedení',
} as const

export const generic = {
  user: 'Uživatel',
  email: 'E-mail',
  city: 'Město',
  street: 'Ulice',
  zip_code: 'PSČ',
  region: 'Kraj',
  location: 'Lokalita',
  name: 'Název',
  slug: 'Zkratka',
  description: 'Popis',
  photo: 'Fotka',
  first_name: 'Křestní jméno',
  last_name: 'Příjmení',
  nickname: 'Přezdívka',
  birth_name: 'Rodné příjmení',
  phone: 'Tel. číslo',
  birthday: 'Datum narození',
  order: 'Pořadí',
  pronoun: 'Oslovení',
  event: 'Akce',
  image: 'Obrázek',
  health_issues: 'Alergie a zdravotní omezení',
  application: 'Přihláška',
  created_at: 'Vytvořeno',
  date: 'Datum',
  place: 'Místo',
  note: 'Poznámka',
  game: 'Program',
  file: 'Soubor',
  comment: 'Komentář',
  emoji: 'Smajlík',
} as const

export const admin = {
  header: 'BIS - Brontosauří informační systém',
  subheader: 'Administrátorský přístup pro organizační jednotky a ústředí',
} as const

export const login = {
  too_many_retries: 'Příliš mnoho pokusů, zkuste to znovu za hodinu',
  user_does_not_exist: 'Uživatel s tímto emailem neexistuje',
  code_form_header: 'Na e-mail {email} byl zaslán kód pro přihlášení',
  code_invalid: 'Kód není validní (chybný či expirovaný)',
} as const

export const event_categories = {
  internal: 'Interní',
  internal__general_meeting: 'Valná hromada',
  internal__volunteer_meeting: 'Schůzka dobrovolníků, týmovka',
  internal__section_meeting: 'Oddílová, družinová schůzka',
  public: 'Veřejná',
  public__volunteering: 'Dobrovolnická',
  public__only_experiential: 'Čistě zážitková',
  public__educational: 'Vzdělávací',
  public__educational__lecture: 'Přednáška',
  public__educational__course: 'Kurz, školení, exkurze',
  public__educational__ohb: 'OHB',
  public__educational__educational: 'Výukový program',
  public__educational__educational_with_stay: 'Pobytový výukový program',
  public__club: 'Klub',
  public__club__lecture: 'Přednáška',
  public__club__meeting: 'Setkání',
  public__other: 'Ostatní',
  public__other__for_public: 'Akce pro veřejnost',
  public__other__exhibition: 'Výstava',
  public__other__eco_tent: 'Ekostan',
} as const
