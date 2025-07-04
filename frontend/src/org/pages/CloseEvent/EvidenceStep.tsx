import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  Help,
  ImagesUpload,
  InfoBox,
} from 'components'
import { ExternalButtonLink } from 'components/Button/Button'
import { form as formTexts } from 'config/static/closeEvent'
import { FormProvider, UseFormReturn } from 'react-hook-form'
import { HiExternalLink } from 'react-icons/hi'
import { required } from 'utils/validationMessages'
import { ExportFilesButton } from '../../components'
import { EvidenceStepFormShape } from './CloseEventForm'
import styles from './EvidenceStep.module.scss'
import { OptOutCheckbox } from './OptOutCheckbox'

export const EvidenceStep = ({
  eventId,
  isVolunteering,
  methods,
  firstIndex = 2,
  multipleSubevents,
}: {
  eventId: number
  isVolunteering: boolean
  methods: UseFormReturn<EvidenceStepFormShape, any>
  firstIndex?: number
  multipleSubevents: boolean
}) => {
  const { register } = methods

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={firstIndex}>
          <FormSection header="Evidence práce">
            <FormSubsection
              required={isVolunteering}
              header="Odpracováno člověkohodin"
              help={formTexts.record.total_hours_worked.help}
            >
              {multipleSubevents && (
                <InfoBox>
                  Tato akce je zadaná jako opakovaná. Zadejte celkový počet
                  odpracovaných hodin na všech opakovaných akcích.
                </InfoBox>
              )}
              <FormInputError>
                <input
                  type="number"
                  {...register('record.total_hours_worked', {
                    required: isVolunteering && required,
                  })}
                />
              </FormInputError>
            </FormSubsection>
            <FormSubsection
              required={isVolunteering}
              header="Komentáře k vykonané práci"
              help="Popište vykonanou dobrovolnickou práci."
            >
              <FormInputError>
                <textarea
                  {...register('record.comment_on_work_done', {
                    required: isVolunteering && required,
                  })}
                  className={styles.widerTextArea}
                />
              </FormInputError>
            </FormSubsection>
          </FormSection>
          <FormSection
            header={
              <>
                Evidence akce&emsp;
                <ExportFilesButton eventId={eventId} />
              </>
            }
          >
            <FormSubsection header="Fotky z akce" help={formTexts.photos.help}>
              <ImagesUpload name="photos" image="photo" thumbnail="thumbnail" />
            </FormSubsection>
            <FormSubsection
              header="Sken prezenční listiny"
              help="Povinné pro akce pobírající dotaci. Doporučené pro všechny ostatní."
            >
              <ImagesUpload name="pages" image="page" />
            </FormSubsection>
          </FormSection>
          <FormSection header="Finance">
            <FormSubsection
              header="Sken dokladů"
              help="Povinné pro vybrané akce. Pokud jste mezi vybranými akcemi, bude vás ústředí HB informovat."
            >
              <ImagesUpload name="receipts" image="receipt" />
            </FormSubsection>
            <FormSubsection
              header="Číslo účtu k proplacení dokladů"
              help="Povinné pro vybrané akce. Pokud jste mezi vybranými akcemi, bude vás ústředí HB informovat."
            >
              {/* TODO: find or ask which field is this */}
              <input type="text" {...register('finance.bank_account_number')} />
            </FormSubsection>
          </FormSection>
          <FormSection header="Závěrečná zpráva">
            <InfoBox>
              Vyplněná závěrečná zpráva o akci nám pomáhá zlepšovat podporu vám
              i dalším organizátorům. Vám zase slouží k uchování doplňkových
              informací a usnadní plánování příští akce!
            </InfoBox>
            <div>
              <Help>
                Přihlašte se univerzálním heslem “vyplnto” nebo heslem vaší
                organizační jednotky.
              </Help>{' '}
              <ExternalButtonLink
                tertiary
                href="https://zpetna-vazba.brontosaurus.cz/login.php"
                target="__blank"
                rel="noopener noreferrer"
                className={styles.outerLinkButton}
              >
                Vyplnit závěrečnou zprávu <HiExternalLink />
              </ExternalButtonLink>
            </div>
          </FormSection>
          <FormSection header="Follow up e-mail pro účastníky">
            <InfoBox>
              Kontakt s účastníky po akci dokresluje celkový dojem z akce a je
              základem toho, aby se účastníci rádi vraceli na další akce HB.
              Stáhni si šablonu pro follow up e-mail, který je nejlepší poslat
              všem účastníkům týden až dva po akci. Účastníkům tak ukážeš, že na
              ně ani po akci nezapomínáš.
            </InfoBox>
            <div>
              <ExternalButtonLink
                tertiary
                href="https://docs.google.com/document/d/17hUEOvU4GH2WEFtd4ZScM_rke9Gv6Vzm/edit"
                target="__blank"
                rel="noopener noreferrer"
                className={styles.outerLinkButton}
              >
                Odkaz na follow up e-mail <HiExternalLink />
              </ExternalButtonLink>
            </div>
          </FormSection>
          <FormSection header="Zpětná vazba Ústředí HB">
            <InfoBox>
              Pokud se na vaší akci vyskytla jakákoliv problémová situace, nebo
              chcete něco sdělit Ústředí HB, vyplňte tento formulář:
            </InfoBox>
            <ExternalButtonLink
              tertiary
              href="https://docs.google.com/forms/d/e/1FAIpQLSf0iDdyvMJp09wD-hk7tSJyFfEMkIER677nNavbKklteij8Qg/viewform"
              target="__blank"
              rel="noopener noreferrer"
              className={styles.outerLinkButton}
            >
              Zpětná vazba na situaci na akci
              <HiExternalLink />
            </ExternalButtonLink>
          </FormSection>
          <FormSection header="E-mail s informacemi o HB">
            <ExternalButtonLink
              tertiary
              href="https://drive.google.com/file/d/1doK_qrD2YW42Qhfd1msRml6YW4he6292/view"
              target="__blank"
              rel="noopener noreferrer"
              className={styles.outerLinkButton}
            >
              E-mail účastníkům po akci
              <HiExternalLink />
            </ExternalButtonLink>
            <FormInputError>
              <label className="checkboxLabel">
                <OptOutCheckbox
                  message="Pokud akci uzavíráte včas, dopočujeme nechat možnost zaškrtnutou. Email po akci obsahuje mnoho důležitých informací, které účastníkům ukazují jak se i přihlásit na další akce a nabízí způsoby, jak s Hnutím Brontosaurus zůstat v kontaktu."
                  title="Opravdu chcete zrušit odeslání mailu?"
                  {...register('record.is_event_closed_email_enabled')}
                ></OptOutCheckbox>
                zaslat účastníkům e-mail s informacemi o HB
              </label>
            </FormInputError>
          </FormSection>
          {/* Údaje , které je třeba zadat po akci:
Počet účastníků celkem *
Z toho počet účastníků do 26 let * 
Bylo by super, pokud by se počet účastníků do 26 let vyplňoval automaticky. 

EVIDENCE AKCE
 Odkaz na fotky z akce - (help?: Nahrajte odkaz na uložiště s fotkami z akce. Fotky z vaší akce velmi pomůžou při propagaci HB a několik se jich posílá poskytovatelům dotací jako důkaz, že akce proběhla. Jako uložiště můžete použít google photos, leteckou poštu, uložto….) 
Nahrát sken prezenční listiny (help?: Povinné pro akce pobírající dotaci. Doporučené pro všechny ostatní.)
Nahrát sken dokladů (help?: Povinné pro vybrané akce. Pokud jste mezi vybranými akcemi, bude vás ústředí HB informovat.)
číslo účtu k proplacení dokladů (help?: Povinné pro vybrané akce. Pokud jste mezi vybranými akcemi, bude vás ústředí HB informovat.)


 
Zpětná vazba od účastníků udělá vaši příští akci ještě lepší! Spokojení účastníci jsou tou nejlepší odměnou pro každého organizátora. Jejich zpětná vazba je velmi cenná a umožní vám reflexi toho, co se povedlo a co můžete do příště ještě vylepšit. Na tomto odkazu zpětnou vazbu pro účastníky lehce připravíte. (help?: Přihlašte se univerzálním heslem “vyplnto” nebo heslem vaší organizační jednotky. )
(https://zpetna-vazba.brontosaurus.cz/login.php)
Vyplněná závěrečná zpráva o akci nám pomáhá zlepšovat podporu vám i dalším organizátorům. Vám zase  slouží k uchování doplňkových informací a usnadní plánování příští akce!
  (help?: Přihlašte se univerzálním heslem “vyplnto” nebo heslem vaší organizační jednotky. )
(https://zpetna-vazba.brontosaurus.cz/login.php).


Do budoucna: Hodnocení servisu ústředí *****
        Možnost poslat follow up email - rozkliknu nabídku - zobrazí se text, který org může upravit - pošle se email všem účastníkům. Text musí být editovatelný kanceláří, aby tam mohli přidávat aktuální pozvánky na akci */}
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
