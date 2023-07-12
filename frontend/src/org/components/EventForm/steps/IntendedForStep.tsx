import { api } from 'app/services/bis'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FormSubheader,
  FormSubsection,
  FullSizeElement,
  InfoBox,
  InlineSection,
  Loading,
} from 'components'
import { useEffect, useMemo } from 'react'
import { Controller, FormProvider } from 'react-hook-form'
import { getIdBySlug, requireBoolean } from 'utils/helpers'
import { required, vipPropagationRequired } from 'utils/validationMessages'
import { MethodsShapes } from '..'

export const IntendedForStep = ({
  methods,
  isCamp,
}: {
  methods: MethodsShapes['intendedFor']
  isCamp: boolean
}) => {
  const { data: intendedFor } = api.endpoints.readIntendedFor.useQuery()
  const { watch, register, trigger, control, unregister, setValue, formState } =
    methods

  // unregister stuff
  useEffect(() => {
    const subscription = watch((data, { name }) => {
      if (
        name === 'intended_for' &&
        getIdBySlug(
          intendedFor?.results ?? [],
          'for_first_time_participant',
        ) !== data.intended_for
      ) {
        unregister('vip_propagation')
        setValue('vip_propagation', null)
      }
    })

    return () => subscription.unsubscribe()
  }, [watch, intendedFor?.results, unregister, setValue])

  const vipPropagation = watch('vip_propagation')
  const isVipPropagationRequired = useMemo(() => {
    if (
      vipPropagation?.goals_of_event ||
      vipPropagation?.program ||
      vipPropagation?.short_invitation_text ||
      vipPropagation?.rover_propagation
    )
      return true
    else return false
  }, [
    vipPropagation?.goals_of_event,
    vipPropagation?.program,
    vipPropagation?.rover_propagation,
    vipPropagation?.short_invitation_text,
  ])

  // trigger vip_propagation validation
  useEffect(() => {
    if (formState.isSubmitted)
      // trigger in next tick, to fix revalidating first field
      Promise.resolve().then(() => trigger('vip_propagation'))
  }, [trigger, isVipPropagationRequired, formState.isSubmitted])

  if (!intendedFor) return <Loading>Připravujeme formulář</Loading>

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={8}>
          <FormSection
            required
            header="Pro koho"
            help="vyberte na koho je akce zaměřená"
          >
            <FormInputError>
              <Controller
                name="intended_for"
                control={control}
                rules={{ required }}
                render={({ field }) => (
                  <fieldset>
                    <InlineSection>
                      {intendedFor &&
                        intendedFor.results!.map(({ id, name, slug }) => (
                          <label key={id} className="radioLabel">
                            <input
                              ref={field.ref}
                              key={id}
                              type="radio"
                              name={field.name}
                              id={slug}
                              value={id}
                              checked={id === field.value}
                              onChange={e =>
                                field.onChange(parseInt(e.target.value))
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
          {
            /* not great hardcoded id */
            +watch('intended_for') === 5 && (
              <>
                <FullSizeElement>
                  <InfoBox>
                    <p>
                      Pokud chcete být zařazeni do VIP propagace, vyplňte
                      všechny 3 otázky uvedené níže. VIP propagace je primárně
                      určena pro tábory a víkendovky.
                    </p>
                    <p>
                      Hnutí Brontosaurus pravidelně vytváří nabídku výběrových
                      dobrovolnických akcí, kterými oslovujeme nové účastníky,
                      zejména středoškolskou mládež a začínající vysokoškoláky
                      (15 - 26 let). Cílem akce je oslovit tyto prvoúčastníky a
                      mít jich nejlépe polovinu, (min. třetinu) z celkového
                      počtu účastníků.
                    </p>
                    <p>Zadáním akce pro prvoúčastníky získáte:</p>
                    <ul>
                      <li>
                        Širší propagaci skrze letáky, osobní kontakty apod.
                        Zveřejnění na letáku VIP propagace.
                      </li>
                      <li>
                        Propagaci na středních školách od lektorů
                        středoškolských programů
                      </li>
                      <li>
                        Zveřejnění na Facebooku a Instagramu HB, reklamu na
                        Facebooku
                      </li>
                      <li>Reklamu v Google vyhledávání</li>
                      <li>Služby grafika HB (dle dohodnutého rozsahu)</li>
                      <li>Přidání do webových katalogů akcí</li>
                      <li>Slevu na inzerci v Roverském kmenu (pro tábory)</li>
                      <li>Zpětnou vazbu k webu a Facebooku akce</li>
                      <li>Metodickou pomoc a pomoc s agendou akce</li>
                      <li>Propagace na novém webu HB v sekci Jedu poprvé</li>
                    </ul>
                  </InfoBox>
                </FullSizeElement>

                <FullSizeElement>
                  <FormSubheader required={isVipPropagationRequired}>
                    Cíle akce a přínos pro prvoúčastníky
                  </FormSubheader>
                  <InfoBox>
                    Jaké je hlavní téma vaší akce? Jaké jsou hlavní cíle akce?
                    Co nejvýstižněji popište, co akce přináší účastníkům, co
                    zajímavého si zkusí, co se dozví, naučí, v čem se rozvinou…
                  </InfoBox>
                  <FormInputError>
                    <textarea
                      {...register('vip_propagation.goals_of_event', {
                        required:
                          isVipPropagationRequired && vipPropagationRequired,
                      })}
                    ></textarea>
                  </FormInputError>
                </FullSizeElement>

                <FullSizeElement>
                  <FormSubheader required={isVipPropagationRequired}>
                    Programové pojetí akce pro prvoúčastníky
                  </FormSubheader>
                  <InfoBox>
                    V základu uveďte, jak bude vaše akce programově a
                    dramaturgicky koncipována (motivační příběh, zaměření
                    programu &ndash; hry, diskuse, řemesla,...). Uveďte, jak
                    náplň a program akce reflektují potřeby vaší cílové skupiny
                    prvoúčastníků.
                  </InfoBox>
                  <FormInputError>
                    <textarea
                      {...register('vip_propagation.program', {
                        required:
                          isVipPropagationRequired && vipPropagationRequired,
                      })}
                    ></textarea>
                  </FormInputError>
                </FullSizeElement>

                <FullSizeElement>
                  <FormSubheader required={isVipPropagationRequired}>
                    Krátký zvací text do propagace
                  </FormSubheader>
                  <InfoBox>
                    Ve 2-4 větách nalákejte na vaši akci a zdůrazněte osobní
                    přínos pro účastníky (max. 200 znaků).
                  </InfoBox>
                  <FormInputError>
                    <textarea
                      {...register('vip_propagation.short_invitation_text', {
                        maxLength: 200,
                        required:
                          isVipPropagationRequired && vipPropagationRequired,
                      })}
                    ></textarea>
                  </FormInputError>
                </FullSizeElement>
                {
                  // only "camp" can see this
                  // https://docs.google.com/document/d/1p3nz0-kVJxwN_pRCYYyhy0BObyGox6LDk35RQPADT4g/edit?disco=AAAAc3SBnZQ
                  isCamp && (
                    <FormSubsection
                      header="Propagovat akci v Roverském kmeni"
                      required={isVipPropagationRequired}
                      help="Placená propagace vaší vícedenní akce v časopisu Roverský kmen za poplatek 100 Kč."
                    >
                      <FormInputError>
                        <Controller
                          name="vip_propagation.rover_propagation"
                          control={control}
                          // TODO validation requirements not clear
                          // TODO this field won't get saved if vip propagation is not filled
                          rules={{ ...requireBoolean }}
                          render={({ field }) => (
                            <InlineSection>
                              {[
                                { name: 'ano', value: true },
                                { name: 'ne', value: false },
                              ].map(({ name, value }) => (
                                <div key={name}>
                                  <label
                                    htmlFor={name}
                                    className={'radioLabel'}
                                  >
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
                                </div>
                              ))}
                            </InlineSection>
                          )}
                        />
                      </FormInputError>
                    </FormSubsection>
                  )
                }
              </>
            )
          }
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
