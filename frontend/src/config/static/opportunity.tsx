import { ReactComponent as HandsIcon } from 'assets/hands.svg'
import { ReactComponent as HousesIcon } from 'assets/houses.svg'
import { ReactComponent as OrganizerIcon } from 'assets/organizer.svg'

export const about = (
  <>
    <p>
      Zde můžeš zadat novou příležitost, která se zobrazí na webu v sekci{' '}
      <a
        href="https://brontosaurus.cz/zapoj-se/"
        target="_blank"
        rel="noopener noreferrer"
      >
        Zapoj se.
      </a>
    </p>
    <p>
      Příležitost je inzerát, který propojí aktivní lidi napříč celým Hnutím
      Brontosaurus. Zadáním příležitosti vytvoříš inzerát, který vám pomůže
      najít třeba chybějícího člena organizátorského týmu nebo fotografa na
      velkou veřejnou akci pořádanou vaším základním článkem.
    </p>
    <p>
      Inspiruj se na{' '}
      <a
        href="https://brontosaurus.cz/zapoj-se/"
        target="_blank"
        rel="noopener noreferrer"
      >
        www.brontosaurus.cz/zapoj-se/
      </a>
    </p>
  </>
)

export const form = {
  category: {
    options: {
      organizing: {
        icon: OrganizerIcon,
        info: 'Příležitosti organizovat či pomáhat s pořádáním našich akcí.',
      },
      collaboration: {
        icon: HandsIcon,
        info: 'Příležitosti ke spolupráci na chodu a rozvoji Hnutí Brontosaurus.',
      },
      location_help: {
        icon: HousesIcon,
        info: 'Příležitosti k pomoci dané lokalitě, která to aktuálně potřebuje.',
      },
    },
  },
  introduction: {
    name: 'Představení příležitosti',
    info: 'Krátce vysvětli význam činnosti a její přínos, aby přilákala zájemce.',
  },
  description: {
    name: 'Popis činnosti',
    info: 'Přibliž konkrétní činnosti a aktivity, které budou součástí příležitosti.',
  },
  location_benefits: {
    name: 'Přínos pro lokalitu',
    info: 'Popiš dopad a přínos činnosti pro dané místo.',
  },
  personal_benefits: {
    name: 'Co mi to přinese?',
    info: 'Uveď konkrétní osobní přínos do života z realizace této příležitosti.',
  },
  requirements: {
    name: 'Co potřebuji ke spolupráci',
    info: 'Napiš dovednosti, zkušenosti či vybavení potřebné k zapojení do příležitosti.',
  },
  contactPerson: {
    help: 'Pokud necháš kontaktní údaje prázdné, použije se Tvé jméno/email/telefon.',
  },
}
