import { FC, useState } from 'react'
import { FaAngleDown, FaAngleUp } from 'react-icons/fa'
import { InfoBox } from 'components'
import styles from './FeedbackStepInfo.module.scss'

export const FeedbackStepInfo: FC = () => {
  const [showInfo, setShowInfo] = useState(true)
  const toggleShowInfo = () => setShowInfo(!showInfo)

  return (
    <>
      <button type="button" onClick={toggleShowInfo} className={styles.button}>
        {showInfo ? (
          <>
            Skrýt info <FaAngleUp />
          </>
        ) : (
          <>
            Zobraz si více informací a stručný návod <FaAngleDown />
          </>
        )}
      </button>
      {showInfo && (
        <InfoBox className={styles.info}>
          <p>
            Tento formulář ti pomůže získat zpětnou vazbu od účastníků tvé akce.
            Pokud ji budeš používat, pomůže ti při příštích akcích ušetřit čas,
            zaměřit se na to důležité a organizovat stále lepší akce s menší
            námahou.
          </p>
          <header>Stručný návod</header>
          <ol>
            <li>
              <strong>Motivuj účastníky k vyplnění:</strong> Pokud jim pošleš
              emailem jen dotazník bez vysvětlení, návratnost bude mizivá. Pokud
              jim vysvětlíš, jak je zpětná vazba pro tebe a Hnutí Brontosaurus
              důležitá, bude návratnost lepší. Nejlepší bude použít drobnou
              odměnu, např. odkaz na fotky z akce, adresář či jiné drobnosti.
              (Během tvorby dotazníku budeš mít možnost tento odkaz zadat.)
            </li>
            <li>
              <strong>Uprav dotazník</strong> tak, aby co nejlépe vyhovoval tvé
              akci, tvým potřebám a tvým účastníkům.
            </li>
            <li>
              <strong>Pošli odkaz.</strong> Odkaz rozešli účastníkům, nezapomeň
              jim napsat, proč by zpětnou vazbu měli vyplnit :)
            </li>
            <li>
              <strong>Prohlédni si odpovědi</strong> a motivuj se jimi při
              přípravě další akce. Odpovědi uvidí všichni, kdo mají přístup k
              akci.
            </li>
          </ol>
        </InfoBox>
      )}
    </>
  )
}