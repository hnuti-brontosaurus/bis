import { InquiryRead } from 'app/services/bisTypes'

export const getRequiredFeedbackInquiries = (
  start: number,
): {
  heading: string
  inquiries: InquiryRead[]
}[] => [
  {
    heading: 'Anketka',
    inquiries: [
      {
        id: start + 1, // FIXME
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
        },
      },
      {
        id: start + 2, // FIXME
        inquiry:
          'Dozvěděl/a  ses nejdříve o této akci nebo o Hnutí Brontosaurus jako celku?',
        is_required: true,
        data: {
          type: 'radio',
          options: [{ option: 'O akci' }, { option: 'O Hnutí Brontosaurus' }],
        },
      },
      {
        id: start + 3, // FIXME
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
        },
      },
      {
        id: start + 4, // FIXME
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
        },
      },
      {
        id: start + 5, // FIXME
        // TODO remove when comment can be added to previous inquiry
        inquiry:
          'Chceš nám napsat něco více k tomu, proč sis vybral/a tuto akci? Budeme rádi za jakýkoli komentář',
        data: {
          type: 'text',
        },
      },
    ],
  },
  {
    heading: 'O akci',
    inquiries: [
      {
        id: start + 6, // FIXME
        inquiry:
          'Komunikace před akcí byla jasná a měl/a jsem dostatek informací ',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 7, // FIXME
        inquiry:
          'Věděl/a jsem, že akce je součástí neziskové organizace Hnutí Brontosaurus a byly mi poskytnuty informace o tom, jaké akce Hnutí Brontosaurus pořádá.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 8, // FIXME
        inquiry:
          'Na akci jsem se cítil/a bezpečně a měl/a jsem se na koho v případě potřeby obrátit.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 9, // FIXME
        inquiry:
          'Zázemí (ubytování, jídlo…) odpovídalo tomu, co bylo na akci inzerováno.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 10, // FIXME
        inquiry: 'Náplň akce mi přišla pestrá, zajímavá a dobře připravená',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 11, // FIXME
        inquiry:
          'Přístup organizátorů k účastníkům byl milý, nápomocný a upřímný.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
    ],
  },
  {
    // TODO only for volunteering events
    heading: 'Dobrovolnická činnost',
    inquiries: [
      {
        id: start + 12, // FIXME
        inquiry:
          'Měl/a jsem dostatek informací o účelu a smysluplnosti dobrovolnické činnosti.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 13, // FIXME
        inquiry:
          'Já osobně jsem považoval/a dobrovolnickou činnost za smysluplnou a cítil/a jsem, že pomáhám přírodě, památkám nebo lidem.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 14, // FIXME
        inquiry:
          'Dobrovolnická činnost byla přiměřeně náročná s dostatkem času na odpočinek.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 15, // FIXME
        inquiry:
          'Dobrovolnickou činnost jsem si užil/a a bavila mě - pomůže nám, když nám napíšeš, co konkrétně tě na práci nejvíce bavilo a proč ti přišla užitečná.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
    ],
  },
  {
    heading: 'Atmosféra',
    inquiries: [
      {
        id: start + 16, // FIXME
        inquiry:
          'Díky účasti na akci jsem si rozšířil/a obzory nebo získal/a nový pohled na to jak vnímám své okolí a okolní přírodu',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 17, // FIXME
        inquiry:
          'Na akci jsem se seznámil/a s lidmi, s kterými bych rád/a dál udržovala kontakt i po akci',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
      {
        id: start + 18, // FIXME
        inquiry:
          'Jak hodnotíš celkovou atmosféru na akci? Co konkrétně se ti na akci líbilo a co bys rád/a vylepšil/a? Tvoje zpětná vazba nám umožní se stále zlepšovat.',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
    ],
  },
  {
    heading: 'Zapojení',
    inquiries: [
      {
        id: start + 19, // FIXME
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
        },
      },
      {
        id: start + 20, // FIXME,
        inquiry:
          'Poskytuje Hnutí Brontosaurus dostatek příležitostí, jak se zapojit? Jakým způsobem ti HB může pomoci, aby jsi udržel/a vzniklá přátelství a více se zapojil/a do činnosti HB (organizace táborů a další akce)',
        is_required: true,
        data: { type: 'scale', comment: true },
      },
    ],
  },
]
