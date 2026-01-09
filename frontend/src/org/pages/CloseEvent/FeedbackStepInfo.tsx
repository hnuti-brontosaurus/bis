import { FC, useState } from 'react'
import { FaAngleDown, FaAngleUp } from 'react-icons/fa'
import { InfoBox } from 'components'
import { feedback } from '../../../config/static/translations'
import { ExternalHeaderLink } from './ExternalHeaderLink'
import styles from './FeedbackStepInfo.module.scss'

interface Props {
  feedbackRequired: boolean
}

export const FeedbackStepInfo: FC<Props> = ({ feedbackRequired }) => {
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
          <header>
            Stručný návod{' '}
            {feedbackRequired ? (
              <>(pro akce s povinnou zpětnou vazbou)</>
            ) : (
              <>(pro akce bez povinné zpětné vazby)</>
            )}
            <ExternalHeaderLink href="https://drive.google.com/file/d/1DjWAPuQCFsQ5JF4W-cxCa4o71ITYUO4v/view">
              podrobný návod
            </ExternalHeaderLink>
            <ExternalHeaderLink href="https://drive.google.com/file/d/1KlSNJW9kYDRoGWAqAPsOH8XOf8hFZin-/view">
              pdf zpětné vazby
            </ExternalHeaderLink>
          </header>
          {feedbackRequired ? (
            <RequiredFeedbackSteps />
          ) : (
            <OptionalFeedbackSteps />
          )}
        </InfoBox>
      )}
    </>
  )
}

const OptionalFeedbackSteps: FC = () => (
  <ol>
    <li>
      <strong>Motivuj účastníky k vyplnění:</strong> Pokud jim pošleš emailem
      jen dotazník bez vysvětlení, návratnost bude mizivá. Pokud jim vysvětlíš,
      jak je zpětná vazba pro tebe a Hnutí Brontosaurus důležitá, bude
      návratnost lepší. Nejlepší bude použít drobnou odměnu, např. odkaz na
      fotky z akce, adresář či jiné drobnosti. (Během tvorby dotazníku budeš mít
      možnost tento odkaz zadat.)
    </li>
    <li>
      <strong>Můžeš přidat vlastní otázky.</strong> Zpětná vazba se skládá z
      otázek zaměřených na cíle společné pro všechny akce Hnutí Brontosaurus.
      Tyto otázky nelze je upravit. Můžeš si k nim ale přidat vlastní otázky,
      které se zaměří na tvou konkrétní akci.
    </li>
    <li>
      <strong>Pošli odkaz.</strong> Odkaz na zpětnou vazbu rozešli účastníkům,
      nezapomeň jim napsat, proč by zpětnou vazbu měli vyplnit :)
    </li>
    <li>
      <strong>Prohlédni si odpovědi</strong> a motivuj se jimi při přípravě
      další akce. Odpovědi uvidí všichni, kdo mají přístup k akci.
    </li>
  </ol>
)

const RequiredFeedbackSteps: FC = () => (
  <ol>
    <li>
      <strong>Pro tuto akci je zpětná vazba povinná</strong> a její odeslání je
      podmínkou pro uzavření akce.
    </li>
    <li>
      <strong>Motivuj účastníky k vyplnění:</strong> Pokud jim pošleš emailem
      jen dotazník bez vysvětlení, návratnost bude mizivá. Pokud jim vysvětlíš,
      jak je zpětná vazba pro tebe a Hnutí Brontosaurus důležitá, bude
      návratnost lepší. Nejlepší bude použít drobnou odměnu, např. odkaz na
      fotky z akce, adresář či jiné drobnosti. (Během tvorby dotazníku budeš mít
      možnost tento odkaz zadat.)
    </li>
    <li>
      <strong>Můžeš přidat vlastní otázky.</strong> Zpětná vazba se skládá z
      otázek zaměřených na cíle společné pro všechny akce Hnutí Brontosaurus.
      Tyto otázky nelze je upravit. Můžeš si k nim ale přidat vlastní otázky,
      které se zaměří na tvou konkrétní akci.
    </li>
    <li>
      Pokud do 20 dnů od ukončení akce zpětnou vazbu neodešleš a akci neuzavřeš,
      odešle se automaticky v&nbsp;základní podobě
    </li>
    <li>
      <strong>Prohlédni si odpovědi</strong> a motivuj se jimi při přípravě
      další akce. Odpovědi uvidí všichni, kdo mají přístup k akci.
    </li>
    <li>
      <strong>Nemusíš se bát.</strong> Zpětná vazba nám pomáhá dívat se na akce
      v&nbsp;širším kontextu a dlouhodobě je společně posouvat dál.
    </li>
  </ol>
)
