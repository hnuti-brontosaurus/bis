import { Optional } from 'utility-types'
import { FullEvent, InquiryRead } from 'app/services/bisTypes'
import { isEventVolunteering } from './helpers'

type QuestionnaireSection = Optional<InquiryRead, 'id' | 'order'>[]

const checkInSection: QuestionnaireSection = [
  {
    inquiry: 'Anketka',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Pokolikáté jsi na akci s Hnutí Brontosaurus? (myslíme tábor nebo víkendovou akci)',
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
      'Dozvěděl/a  ses nejdříve o této akci nebo o Hnutí Brontosaurus jako celku?',
    is_required: true,
    data: {
      type: 'radio',
      options: [{ option: 'O akci' }, { option: 'O Hnutí Brontosaurus' }],
      layout: 'horizontal',
      fixed: true,
    },
  },
  {
    inquiry: 'Jak ses dozvěděl/a o tomto táboře?',
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
    data: { type: 'header', fixed: true },
  },

  {
    inquiry: 'Komunikace před akcí byla jasná a měl/a jsem dostatek informací ',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Věděl/a jsem, že akce je součástí neziskové organizace Hnutí Brontosaurus a byly mi poskytnuty informace o tom, jaké akce Hnutí Brontosaurus pořádá.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Na akci jsem se cítil/a bezpečně a měl/a jsem se na koho v případě potřeby obrátit.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Zázemí (ubytování, jídlo…) odpovídalo tomu, co bylo na akci inzerováno.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry: 'Náplň akce mi přišla pestrá, zajímavá a dobře připravená',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry: 'Přístup organizátorů k účastníkům byl milý, nápomocný a upřímný.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

const volunteeringSection: QuestionnaireSection = [
  {
    inquiry: 'Dobrovolnická činnost',
    data: { type: 'header', fixed: true },
  },

  {
    inquiry:
      'Měl/a jsem dostatek informací o účelu a smysluplnosti dobrovolnické činnosti.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Já osobně jsem považoval/a dobrovolnickou činnost za smysluplnou a cítil/a jsem, že pomáhám přírodě, památkám nebo lidem.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Dobrovolnická činnost byla přiměřeně náročná s dostatkem času na odpočinek.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Dobrovolnickou činnost jsem si užil/a a bavila mě - pomůže nám, když nám napíšeš, co konkrétně tě na práci nejvíce bavilo a proč ti přišla užitečná.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

const atmosphereSection: QuestionnaireSection = [
  {
    inquiry: 'Atmosféra',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Díky účasti na akci jsem si rozšířil/a obzory nebo získal/a nový pohled na to jak vnímám své okolí a okolní přírodu',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Na akci jsem se seznámil/a s lidmi, s kterými bych rád/a dál udržovala kontakt i po akci',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
  {
    inquiry:
      'Jak hodnotíš celkovou atmosféru na akci? Co konkrétně se ti na akci líbilo a co bys rád/a vylepšil/a? Tvoje zpětná vazba nám umožní se stále zlepšovat.',
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

const involvementSection: QuestionnaireSection = [
  {
    inquiry: 'Zapojení',
    data: { type: 'header', fixed: true },
  },
  {
    inquiry:
      'Chceš se více zapojit do činnosti Hnutí Brontosaurus? Rádi ti s tím pomůžeme a přivítáme tě mezi sebou :) Co tě nejvíc láká? Možnosti jak se zapojit najdeš i na webu Zapoj se', // TODO link [Zapoj se](https://brontosaurus.cz/zapoj-se/)
    is_required: true,
    data: {
      type: 'checkbox',
      options: [
        { option: 'přidat se do organizátorského týmu' },
        { option: 'absolvovat organizátorský kurz' },
        { option: 'zůčastnit se další akce Hnutí Brontosaurus' },
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
    is_required: true,
    data: { type: 'scale', comment: true, fixed: true },
  },
]

export const getRequiredFeedbackInquiries = (
  event: FullEvent,
): QuestionnaireSection =>
  checkInSection.concat(
    eventSection,
    isEventVolunteering(event) ? volunteeringSection : [],
    atmosphereSection,
    involvementSection,
  )
