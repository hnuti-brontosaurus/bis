import { ReactComponent as OneTreeIcon } from 'assets/one-tree.svg'
import { ReactComponent as TentIcon } from 'assets/tent.svg'
import { ReactComponent as ThreeTreesIcon } from 'assets/three-trees.svg'

export const form = {
  group: {
    options: {
      other: {
        icon: OneTreeIcon,
        name: (
          <>
            Jednodenní <br />
            (příp. akce bez adresáře)
          </>
        ),
        help: (
          <>
            Akce trvající 1 den a méně.
            <br />
            Akce bez povinného adresáře jsou speciální akce, kde nelze vyplňovat
            prezenční listinu např. dlouhodobé výstavy, velké akce pro
            veřejnost…
          </>
        ),
      },
      weekend_event: {
        icon: ThreeTreesIcon,
        name: (
          <>
            Víkendovka,
            <br />
            Brďo schůzky
          </>
        ),
        help: 'Víkendovky jsou akce trvající 2-5 dnů',
      },
      camp: {
        icon: TentIcon,
        name: 'Tábor',
        help: 'Tábory jsou akce konající se 6 a více dní',
      },
    },
  },
  propagation: {
    is_shown_on_web: {
      name: 'Zveřejnit na www.brontosaurus.cz',
      help: 'Pokud zaškrtnete ano, akce se zobrazí na webu www.brontosaurus.cz. Volbu ne zaškrtněte pouze jedná-li se o interní akci HB nebo interní akci Brďa.',
    },
    invitation_text_introduction: {
      name: 'Zvací text: Co nás čeká',
      help: 'Základní informace o tvé akci. Popiš téma akce a nastiň, co se tam bude dít a jak budete pomáhat, co se účastník naučí nového. Prvních několik vět se zobrazí v přehledu akcí na webu. První věty jsou k upoutání pozornosti nejdůležitější, proto se na ně zaměř a shrň ve 2-4 větách na co se účastníci mohou těšit.',
    },
    invitation_text_practical_information: {
      name: 'Zvací text: Co, kde a jak',
      help: 'Stručný popis programu akce – jakého typu budou aktivity na akci, kde se bude spát, co se bude jíst a další praktické záležitosti. Nezapomeň zdůraznit, zda bude program aktivní a plný zážitkového programu nebo bude spíše poklidnější nebo zaměřený na vzdělávání. Také napiš zda bude program fyzicky popř. psychicky náročný, aby účastníci věděli co mají čekat.',
    },
    invitation_text_work_description: {
      name: 'Zvací text: Dobrovolnická pomoc',
      help: 'Stručně popiš dobrovolnickou činnost a její smysl pro přírodu, památky nebo lidi (např. „sázíme vrbky, aby měli místní ptáci kde hnízdit“). Zasaď dobrovolnickou pomoc do kontextu místa a jeho příběhu (např. “kosením pomůžeme udržet pestrost nejvzácnější louky unikátní krajiny Bílých Karpat, jež …” ). Napiš, co se při práci účastníci naučí a v čem je to může rozvinout. Přidej i další zajímavosti, které se vážou k dané dobrovolnické činnosti a lokalitě. Uveď kolik prostoru na akci se bude věnovat dobrovolnické činnosti a jak bude náročná.',
    },
    invitation_text_about_us: {
      name: 'Zvací text: Malá ochutnávka',
      help: 'Malá ochutnávka uvádí fotky, které k akci přiložíte. Popište fotky, které přikládáte nebo přibližte jak vypadaly akce na stejném místě v minulosti. U nových akcí můžete více ukázat místo a důvody proč vás oslovilo a představit organizátory.',
    },
  },
  registrationMethod: {
    help: (
      <>
        Způsoby přihlášení na vaši akci na www.brontosaurus.cz, které se zobrazí
        po kliknutí na tlačítko “chci jet”:
        <ul>
          <li>
            Standardní přihláška na brontowebu (doporučujeme!) - Je jednotná pro
            celé HB. Do této přihlášky si můžete přidat vlastní otázky. Vyplněné
            údaje se pak rovnou zobrazí v BIS, což tobě i kanceláři ulehčí
            práci.
          </li>
          <li>
            Jiná elektronická přihláška - Při přihlašování budou zájemci rovnou
            přesměrování na tvoji přihlášku. V tomto případě se ale přihlášení
            lidé v BIS nezobrazí.
          </li>
          <li>
            Registrace není potřeba, stačí přijít - Zobrazí se jako text u tvojí
            akce na webu.
          </li>
          <li>
            Máme bohužel plno, zkuste jinou z našich akcí - Zobrazí se jako text
            u tvojí akce na webu.
          </li>
        </ul>
      </>
    ),
  },
  registration: {
    questionnaire: {
      help: 'Zde můžeš připsat svoje doplňující otevřené otázky pro účastníky, které se zobrazí u standardní přihlášky na webu. Kromě tvých otázek se standardní přihláška ptá na jméno, datum narození, telefon a email účastníka.',
      introduction: {
        help: 'Text který se zobrazí na začátku dotazníku.',
      },
      after_submit_text: {
        help: 'Text který se zobrazí poté, co zájemkyně/zájemce odešle formulář.',
      },
    },
  },
}
