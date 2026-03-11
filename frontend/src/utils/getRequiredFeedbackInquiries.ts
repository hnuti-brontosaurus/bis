import { Optional } from 'utility-types'
import { InquiryRead } from 'app/services/bisTypes'

type QuestionnaireSection = Optional<InquiryRead, 'id' | 'order'>[]

const checkInSection: QuestionnaireSection = [
  {
    inquiry: 'Anketa',
    slug: 'check_in_section_heading',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Pokolikáté jsi na akci s Hnutím Brontosaurus? (myslíme tábor nebo víkendovou akci)',
    slug: 'previous_participation_number',
    is_required: true,
    data: {
      type: 'radio',
      options: [
        { option: 'poprvé' },
        { option: 'byl*a jsem už několikrát' },
        { option: 'jezdím pravidelně' },
      ],
      layout: 'horizontal',
      fixed: true,
    },
  },
  {
    inquiry:
      'Věděl*a jsi, že akce je součástí Hnutí Brontosaurus a dostal*a jsi informace o tom, jaké akce Hnutí Brontosaurus pořádá?',
    slug: 'brontosaurus_knowledge',
    is_required: true,
    data: {
      type: 'radio',
      options: [
        { option: 'ano' },
        { option: 'ne' },
        { option: 'jezdím pravidelně' },
      ],
      layout: 'horizontal',
      fixed: true,
    },
  },
  {
    inquiry: 'Jak ses o této akci dozvěděl*a?',
    slug: 'propagation_source',
    is_required: true,
    data: {
      type: 'checkbox',
      options: [
        { option: 'Facebook, Instagram' },
        { option: 'reklama na sociálních sítích' },
        { option: 'web Hnutí Brontosaurus' },
        { option: 'kamarád*ka, známý*á nebo rodič' },
        { option: 'na jiné akci Hnutí Brontosaurus' },
        { option: 'tištěná propagace (plakát, leták apod.)' },
        { option: 'školní program' },
        { option: 'festival (informační stánek)' },
        { option: 'dobrovolnické centrum (MUNI Pomáhá apod.)' },
      ],
      otherOption: true,
      fixed: true,
    },
  },
  {
    inquiry:
      'Proč sis vybral*a právě tuto akci? Prosím vyber tři nejdůležitější důvody a budeme rádi i za krátký komentář.',
    slug: 'participation_reasons',
    is_required: true,
    data: {
      type: 'checkbox',
      options: [
        { option: 'termín' },
        { option: 'místo' },
        { option: 'dobrovolnická pomoc' },
        { option: 'téma' },
        { option: 'kamarádi/účastníci' },
        { option: 'organizátoři' },
        { option: 'pořádající základní článek/klub' },
      ],
      otherOption: true,
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
    inquiry: 'Komunikace před akcí byla jasná a měl*a jsem dostatek informací ',
    slug: 'pre_event_communication',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Na akci jsem se cítil*a bezpečně a měl*a jsem se na koho v případě potřeby obrátit.',
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
    inquiry: 'Akce mi rozšířila obzory v oblasti péče o přírodu nebo památky.',
    slug: 'impact_self_volunteering',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Jaká byla celková atmosféra na akci? Co konkrétně se ti líbilo a co bys potřeboval*a jinak? Tvoje zpětná vazba nám umožní se stále zlepšovat.',
    slug: 'event_atmosphere',
    is_required: true,
    data: { type: 'text', fixed: true },
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
      'Měl*a jsem dostatek informací o účelu a smysluplnosti dobrovolnické činnosti na pomoc přírodě, památkám nebo lidem.',
    slug: 'volunteering_communication',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Jak hodnotíš smysluplnost, náročnost a organizaci dobrovolnické pomoci?',
    slug: 'volunteering_feedback',
    is_required: true,
    data: { type: 'text', fixed: true },
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
      'Chceš se do Hnutí Brontosaurus zapojit víc? Co tě nejvíc láká? Možnosti, jak se zapojit, najdeš v Aktuálních příležitostech.', // TODO link [Aktuálních příležitostech](https://brontosaurus.cz/zapoj-se/)
    slug: 'involvement_means',
    is_required: true,
    data: {
      type: 'checkbox',
      options: [
        {
          option: 'přidat se do organizátorského týmu',
          href: 'https://brontosaurus.cz/zapoj-se/',
        },
        {
          option: 'absolvovat organizátorský kurz',
          href: 'https://organizator.brontosaurus.cz/',
        },
        {
          option: 'zúčastnit se další akce Hnutí Brontosaurus',
          href: 'https://brontosaurus.cz/',
        },
        { option: 'vytvořit vlastní akci' },
        {
          option:
            'zapojit se do dobrovolnického centra v Brně, Praze nebo Olomouci',
        },
        { option: 'stát se vedoucím Brontosauřích dětských oddílů' },
        {
          option: 'stát se členem Hnutí Brontosaurus',
          href: 'https://brontosaurus.cz/zapoj-se/clenstvi/',
        },
        {
          option: 'stát se podporovatelem Hnutí Brontosaurus',
          href: 'https://brontosaurus.cz/podpor-nas/',
        },
        { option: 'nechci se zapojit' },
        { option: 'jsem zapojen*á až až' },
      ],
      fixed: true,
    },
  },
]

export const getRequiredFeedbackInquiries = (
  isVolunteering: boolean,
): QuestionnaireSection =>
  checkInSection.concat(
    eventSection,
    isVolunteering ? volunteeringSection : [],
    involvementSection,
  )
