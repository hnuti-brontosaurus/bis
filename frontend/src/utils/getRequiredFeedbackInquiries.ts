import { Optional } from 'utility-types'
import { Event, InquiryRead } from 'app/services/bisTypes'
import { isEventVolunteering } from './helpers'

type QuestionnaireSection = Optional<InquiryRead, 'id' | 'order'>[]

const checkInSection: QuestionnaireSection = [
  {
    inquiry: 'Anketka',
    slug: 'check_in_section_heading',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Pokolikáté jsi na akci s Hnutí Brontosaurus? (myslíme tábor nebo víkendovou akci)',
    slug: 'previous_participation_number',
    is_required: true,
    data: {
      type: 'radio',
      options: [
        { option: 'poprvé' },
        { option: 'podruhé nebo potřetí' },
        { option: 'už jsem byl/a víckrát' },
      ],
      layout: 'horizontal',
      fixed: true,
    },
  },
  {
    inquiry:
      'Dozvěděl/a ses nejdříve o této akci nebo o Hnutí Brontosaurus jako celku?',
    slug: 'previous_brontosaurus_knowledge',
    is_required: true,
    data: {
      type: 'radio',
      options: [{ option: 'O akci' }, { option: 'O Hnutí Brontosaurus' }],
      layout: 'horizontal',
      fixed: true,
    },
  },
  {
    inquiry: 'Jak ses dozvěděl/a o této akci?',
    slug: 'propagation_source',
    is_required: true,
    data: {
      type: 'radio',
      options: [
        { option: 'web Hnutí Brontosaurus' },
        { option: 'sociální  sítě – FB' },
        { option: 'sociální sítě – IG' },
        { option: 'kamarád, známý nebo rodič' },
        { option: 'tištěná propagace – plakát nebo leták' },
        { option: 'weby s nabídkami akcí (dobrovolnik.cz atd.)' },
        { option: 'dobrovolnická centra (MUNI Pomáhá atd.)' },
        { option: 'akce a festivaly – Ekostan, Dort, aj.' },
        { option: 'Roverský kmen' },
        { option: 'Google' },
        { option: 'nepamatuji si' },
      ],
      fixed: true,
    },
  },
  {
    // TODO this one should have optional comment
    inquiry:
      'Podle čeho sis vybral/a tuto akci? Prosím vyber pro tebe nejdůležitější 3 důvody',
    slug: 'participation_reasons',
    is_required: true,
    data: {
      type: 'checkbox',
      options: [
        { option: 'Termín' },
        { option: 'Místo' },
        { option: 'Práce' },
        { option: 'Téma' },
        { option: 'Kamarádi, účastníci' },
        { option: 'Organizátoři' },
        { option: 'Pořádající základní článek/klub' },
      ],
      fixed: true,
    },
  },
  {
    // TODO remove when comment can be added to previous inquiry
    inquiry:
      'Chceš nám napsat něco více k tomu, proč sis vybral/a tuto akci? Budeme rádi za jakýkoli komentář',
    slug: 'participation_reasons_comment',
    is_required: false,
    data: {
      type: 'text',
      fixed: true,
    },
  },
]

const eventSection: QuestionnaireSection = [
  {
    inquiry: 'O akci',
    slug: 'event_section_heading',
    data: { type: 'header', fixed: true },
  },

  {
    inquiry: 'Komunikace před akcí byla jasná a měl/a jsem dostatek informací ',
    slug: 'pre_event_communication',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Věděl/a jsem, že akce je součástí neziskové organizace Hnutí Brontosaurus a byly mi poskytnuty informace o tom, jaké akce Hnutí Brontosaurus pořádá.',
    slug: 'brontosaurus_communication',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Na akci jsem se cítil/a bezpečně a měl/a jsem se na koho v případě potřeby obrátit.',
    slug: 'event_safety',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Zázemí (ubytování, jídlo…) odpovídalo tomu, co bylo na akci inzerováno.',
    slug: 'facilities_information_veracity',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry: 'Náplň akce mi přišla pestrá, zajímavá a dobře připravená',
    slug: 'event_program',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry: 'Přístup organizátorů k účastníkům byl milý, nápomocný a upřímný.',
    slug: 'organizer_attitude',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

const volunteeringSection: QuestionnaireSection = [
  {
    inquiry: 'Dobrovolnická činnost',
    slug: 'volunteering_section_heading',
    data: { type: 'header', fixed: true },
  },

  {
    inquiry:
      'Měl/a jsem dostatek informací o účelu a smysluplnosti dobrovolnické činnosti.',
    slug: 'volunteering_communication',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Já osobně jsem považoval/a dobrovolnickou činnost za smysluplnou a cítil/a jsem, že pomáhám přírodě, památkám nebo lidem.',
    slug: 'volunteering_meaningfulness',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Dobrovolnická činnost byla přiměřeně náročná s dostatkem času na odpočinek.',
    slug: 'volunteering_difficulty',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Dobrovolnickou činnost jsem si užil/a a bavila mě - pomůže nám, když nám napíšeš, co konkrétně tě na práci nejvíce bavilo a proč ti přišla užitečná.',
    slug: 'volunteering_fun',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

const atmosphereSection: QuestionnaireSection = [
  {
    inquiry: 'Atmosféra',
    slug: 'atmosphere_section_heading',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Díky účasti na akci jsem si rozšířil/a obzory nebo získal/a nový pohled na to jak vnímám své okolí a okolní přírodu',
    slug: 'impact_self',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Na akci jsem se seznámil/a s lidmi, s kterými bych rád/a dál udržovala kontakt i po akci',
    slug: 'impact_people',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Jak hodnotíš celkovou atmosféru na akci? Co konkrétně se ti na akci líbilo a co bys rád/a vylepšil/a? Tvoje zpětná vazba nám umožní se stále zlepšovat.',
    slug: 'event_atmosphere',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

const involvementSection: QuestionnaireSection = [
  {
    inquiry: 'Zapojení',
    slug: 'involvement_section_heading',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Chceš se více zapojit do činnosti Hnutí Brontosaurus? Rádi ti s tím pomůžeme a přivítáme tě mezi sebou :) Co tě nejvíc láká? Možnosti jak se zapojit najdeš i na webu Zapoj se', // TODO link [Zapoj se](https://brontosaurus.cz/zapoj-se/)
    slug: 'involvement_means',
    is_required: true,
    data: {
      type: 'checkbox',
      options: [
        { option: 'přidat se do organizátorského týmu' },
        { option: 'absolvovat organizátorský kurz' },
        { option: 'zúčastnit se další akce Hnutí Brontosaurus' },
        { option: 'vytvořit vlastní akci' },
        {
          option: 'zapojit se do dobrovolnického centra v Brně nebo Praze',
        },
        { option: 'stát se vedoucím dětských Brďo oddílů' },
        { option: 'stát se členem Hnutí Brontosaurus (Staň se členem)' }, // TODO link [Staň se členem](https://brontosaurus.cz/zapoj-se/clenstvi/)
        {
          option:
            'stát se podporovatelem Hnutí Brontosaurus (Adoptuj Brontosaura)', // TODO link [Adoptuj Brontosaura](https://brontosaurus.cz/podpor-nas/)
        },
        { option: 'nechci se zapojit' },
      ],
      fixed: true,
    },
  },
  {
    inquiry:
      'Poskytuje Hnutí Brontosaurus dostatek příležitostí, jak se zapojit? Jakým způsobem ti HB může pomoci, aby jsi udržel/a vzniklá přátelství a více se zapojil/a do činnosti HB (organizace táborů a další akce)',
    slug: 'involvement_feedback',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

export const getRequiredFeedbackInquiries = (
  event: Event,
): QuestionnaireSection =>
  checkInSection.concat(
    eventSection,
    isEventVolunteering(event) ? volunteeringSection : [],
    atmosphereSection,
    involvementSection,
  )
