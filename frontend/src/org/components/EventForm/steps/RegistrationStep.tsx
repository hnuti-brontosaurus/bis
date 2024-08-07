import { useState } from 'react'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubsection,
  FullSizeElement,
  InfoBox,
  InlineSection,
  Label,
} from 'components'
import { form as formTexts } from 'config/static/event'
import { Controller, FormProvider } from 'react-hook-form'
import { FaAngleUp, FaAngleDown } from 'react-icons/fa'
import { requireBoolean } from 'utils/helpers'
import * as messages from 'utils/validationMessages'
import { MethodsShapes } from '..'
import applicationImage from 'assets/prihlaska.png'
import applicationImageChild from 'assets/prihlaska_dite.png'
import { QuestionsFormSection } from './QuestionsFormSection'
import styles from './RegistrationStep.module.scss'

export const RegistrationStep = ({
  methods,
}: {
  methods: MethodsShapes['registration']
}) => {
  const { control, register, watch } = methods

  const isNotOnWeb = watch('propagation.is_shown_on_web') === false

  const [showInfo, setShowInfo] = useState(false)
  const handleClickShowInfo = () => {
    setShowInfo(!showInfo)
  }

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={10}>
          <FormSection
            required
            header={formTexts.propagation.is_shown_on_web.name}
            help={formTexts.propagation.is_shown_on_web.help}
          >
            <FormInputError>
              <Controller
                name={'propagation.is_shown_on_web'}
                control={control}
                rules={{ ...requireBoolean }}
                render={({ field }) => (
                  <fieldset>
                    <InlineSection>
                      {[
                        { name: 'Ano', value: true },
                        { name: 'Ne', value: false },
                      ].map(({ name, value }) => (
                        <label key={name} className="radioLabel">
                          <input
                            ref={field.ref}
                            type="radio"
                            name={field.name}
                            id={name}
                            value={String(value)}
                            checked={field.value === value}
                            onChange={e =>
                              field.onChange(
                                e.target.value === 'true'
                                  ? true
                                  : e.target.value === 'false'
                                  ? false
                                  : undefined,
                              )
                            }
                          />{' '}
                          {name}
                        </label>
                      ))}
                    </InlineSection>
                  </fieldset>
                )}
              />
            </FormInputError>
          </FormSection>

          {!isNotOnWeb && (
            <>
              <FormSection
                header="Způsob přihlášení"
                required
                onWeb
                help={formTexts.registrationMethod.help}
              >
                <FormInputError name="registrationMethod">
                  <fieldset>
                    {[
                      {
                        name: 'Standardní přihláška na brontowebu',
                        value: 'standard',
                      },
                      { name: 'Jiná elektronická přihláška', value: 'other' },
                      {
                        name: 'Registrace není potřeba, stačí přijít',
                        value: 'none',
                      },
                      {
                        name: 'Máme bohužel plno, zkuste jinou z našich akcí',
                        value: 'full',
                      },
                    ].map(({ name, value }) => (
                      <label key={value} className="radioLabel">
                        <input
                          type="radio"
                          value={value}
                          id={`registration-method-${value}`}
                          {...register('registrationMethod', {
                            required: messages.required,
                          })}
                        />{' '}
                        {name}
                      </label>
                    ))}
                  </fieldset>
                </FormInputError>
              </FormSection>

              {watch('registrationMethod') === 'other' && (
                <InlineSection>
                  <InfoBox>
                    Opravdu nechcete použít Standardní přihlášku?
                    <br />
                    Standardní přihláška vám ulehčí práci, zjednoduší
                    přihlašování účastníkům a poskytuje stejné funkce jako
                    google formulář.
                  </InfoBox>
                  <Label required>Odkaz na přihlášku</Label>{' '}
                  <FormInputError>
                    <input
                      type="url"
                      {...register(
                        'registration.alternative_registration_link',
                        {
                          required: messages.required,
                          validate: {
                            url: value => {
                              try {
                                new URL(value as string)
                                return true
                              } catch (e) {
                                return messages.url
                              }
                            },
                          },
                        },
                      )}
                      placeholder="odkaz na vaši přihlášku"
                    />
                  </FormInputError>
                </InlineSection>
              )}

              {/* {watch('registration.is_registration_required') && ( */}
              {watch('registrationMethod') === 'standard' && (
                <FormSubsection
                  header="Přihláška"
                  help={formTexts.registration.questionnaire.help}
                >
                  <button
                    type="button"
                    onClick={handleClickShowInfo}
                    className={styles.showInfoButton}
                  >
                    {showInfo ? (
                      <>
                        Skrýt info
                        <FaAngleUp />
                      </>
                    ) : (
                      <>
                        Zobraz si více informací a výhod standardní přihlášky
                        <FaAngleDown />
                      </>
                    )}
                  </button>
                  {showInfo ? (
                    <InfoBox>
                      <strong>
                        Standardní přihláška vám ulehčí práci, zjednoduší a
                        sjednotí přihlašování účastníkům a poskytuje stejné
                        funkce jako google formulář.
                      </strong>
                      <br />
                      <br />
                      U Standartní přihlášky na brontowebu se na webu HB vždy
                      automaticky zobrazí standartní přihláška HB s dotazem na
                      jméno, příjmení, datum narození, telefon, e-mail a
                      prostorem pro poznámku. Pokud se přihlašuje dítě, je tam
                      možné vyplnit i kontaktní údaje na rodiče.
                      <br />
                      <br />
                      Pokud si k přihlášce chcete přidat jakýkoliv vlastní
                      vlastní text nebo otázky, můžete si vytvořit vlastní část
                      dotazníku, která se k Standartní přihlášce připojí.
                      <br />
                      <br />
                      Vyplněné Standardní přihlášky vám automaticky budou chodit
                      na kontaktní e-mail uvedený u akce. Zároveň se přihlášky
                      automaticky propíšou do BIS.{' '}
                      <strong>
                        Jedním kliknutím si pak vytvoříš seznam účastníků nebo
                        vygeneruješ prezenční listinu.
                      </strong>
                      <div className={styles.imageWrapper}>
                        <img
                          className={styles.applicationImage}
                          src={applicationImage}
                          alt="přihláška"
                        />
                        <img
                          className={styles.applicationImage}
                          src={applicationImageChild}
                          alt="přihláška dítě"
                        />
                      </div>
                    </InfoBox>
                  ) : null}
                  <FormSubsection
                    header="Úvod k dotazníku"
                    help={
                      formTexts.registration.questionnaire.introduction.help
                    }
                  >
                    <FullSizeElement>
                      <FormInputError>
                        <textarea
                          {...register(
                            'registration.questionnaire.introduction',
                          )}
                        />
                      </FormInputError>
                    </FullSizeElement>
                  </FormSubsection>
                  <FormSubsection
                    header="Text po odeslání"
                    help={
                      formTexts.registration.questionnaire.after_submit_text
                        .help
                    }
                  >
                    <FullSizeElement>
                      <FormInputError>
                        <textarea
                          {...register(
                            'registration.questionnaire.after_submit_text',
                          )}
                        />
                      </FormInputError>
                    </FullSizeElement>
                  </FormSubsection>
                  <QuestionsFormSection methods={methods} />
                </FormSubsection>
              )}
            </>
          )}
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
