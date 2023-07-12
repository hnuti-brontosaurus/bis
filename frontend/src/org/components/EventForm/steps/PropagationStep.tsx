import { api } from 'app/services/bis'
import { ReactComponent as Cheese } from 'assets/cheese.svg'
import { ReactComponent as Leaf } from 'assets/leaf.svg'
import { ReactComponent as Piglet } from 'assets/mama-i-laura.svg'
import classNames from 'classnames'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FullSizeElement,
  InlineSection,
  Label,
  Loading,
  NumberInput,
} from 'components'
import { ReactElement, useEffect } from 'react'
import { Controller, FormProvider } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import { MethodsShapes } from '..'

const foodIcons: { [name: string]: ReactElement } = {
  's masem': <Piglet />,
  vegetariánská: <Cheese />,
  veganská: <Leaf />,
}

/**
 * Validate ages
 * if both ages are provided, then max age must be above or equal min age
 * and we allow empty values
 * we don't care about anything else (taken care of by NumberInput component)
 */
const areAgesValid = (
  min: string | number | null | undefined,
  max: string | number | null | undefined,
) => {
  if (typeof min === 'number' && typeof max === 'number') {
    return min <= max
    // we want to allow empty values
  } else return true
}

export const PropagationStep = ({
  methods,
  isVolunteering,
  isWeekendEvent,
  isCamp,
  isInternalSectionMeeting,
}: {
  methods: MethodsShapes['propagation']
  isVolunteering: boolean
  isWeekendEvent: boolean
  isCamp: boolean
  isInternalSectionMeeting: boolean
}) => {
  const { control, register, getValues, watch, trigger } = methods
  const { data: diets } = api.endpoints.readDiets.useQuery()

  // revalidate ages when they change
  useEffect(() => {
    const subscription = watch((data, { name }) => {
      if (name === 'propagation.minimum_age') trigger('propagation.maximum_age')
    })

    return subscription.unsubscribe
  }, [trigger, watch])

  if (!diets) return <Loading>Připravujeme formulář</Loading>

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={12}>
          <FormSection
            onWeb
            required
            header="Účastnický poplatek"
            help="Napište výši vašeho účastnického poplatku. Označení Kč se přidá automaticky. Pokud máte více cen (studentskou nebo naopak mecenášskou), výše dalších poplatků napište za lomítko. Můžete uvést i rozmezí cen. Např. 150/200/250 nebo 150-250)"
          >
            <InlineSection>
              <Label htmlFor="propagation.cost">částka</Label>
              <FormInputError>
                <input
                  type="text"
                  id="propagation.cost"
                  maxLength={12}
                  size={12}
                  {...register('propagation.cost', { required })}
                  placeholder="100, 150/200, 150-250"
                />
              </FormInputError>{' '}
              Kč
            </InlineSection>
          </FormSection>
          <FormSection header="Věk" onWeb>
            <InlineSection>
              <Label htmlFor="propagation.minimum_age">Od</Label>
              <FormInputError>
                <Controller
                  control={control}
                  name="propagation.minimum_age"
                  render={({ field }) => (
                    <NumberInput
                      {...field}
                      min={0}
                      name="propagation.minimum_age"
                    ></NumberInput>
                  )}
                />
              </FormInputError>
              <Label htmlFor="propagation.maximum_age">Do</Label>
              <FormInputError>
                <Controller
                  control={control}
                  name="propagation.maximum_age"
                  rules={{
                    validate: maxAge =>
                      areAgesValid(
                        getValues('propagation.minimum_age'),
                        maxAge,
                      ) || 'Maximální věk musí být vyšší než minimální věk',
                  }}
                  render={({ field }) => (
                    <NumberInput
                      {...field}
                      min={0}
                      name="propagation.maximum_age"
                    ></NumberInput>
                  )}
                />
              </FormInputError>
            </InlineSection>
          </FormSection>
          {(isWeekendEvent || isCamp) &&
            !(isWeekendEvent && isInternalSectionMeeting) && ( // only camp and weekend, and not weekend+internal-section-meeting
              <FormSection required header="Ubytování" onWeb>
                <FullSizeElement>
                  <FormInputError>
                    <textarea
                      {...register('propagation.accommodation', {
                        required,
                      })}
                    />
                  </FormInputError>
                </FullSizeElement>
              </FormSection>
            )}
          {(isWeekendEvent || isCamp) &&
            !(isWeekendEvent && isInternalSectionMeeting) && ( // only camp and weekend, and not weekend+internal-section-meeting
              <FormSection
                header="Strava"
                required
                onWeb
                help="Můžete vybrat více druhů stravy."
              >
                <FormInputError>
                  <Controller
                    name="propagation.diets"
                    control={control}
                    rules={{ required }}
                    render={({ field }) => (
                      <InlineSection>
                        {[...diets.results]
                          .reverse() // fast hack to show meaty diet last
                          .map(({ id, name }) => (
                            <label
                              key={id}
                              className={classNames(
                                'labelCheckboxTag',
                                'checkboxLabel',
                              )}
                            >
                              <input
                                ref={field.ref}
                                key={id}
                                type="checkbox"
                                name={field.name}
                                value={id}
                                checked={
                                  field.value && field.value.includes(id)
                                }
                                onChange={e => {
                                  // check when unchecked and vise-versa
                                  const targetId = Number(e.target.value)
                                  const set = new Set(field.value)
                                  if (set.has(targetId)) {
                                    set.delete(targetId)
                                  } else {
                                    set.add(targetId)
                                  }
                                  field.onChange(Array.from(set))
                                }}
                              />{' '}
                              <div>{name}</div>
                              {foodIcons[name]}
                            </label>
                          ))}
                      </InlineSection>
                    )}
                  />
                </FormInputError>
              </FormSection>
            )}
          {/* TODO povinné pouze u dobrovolnických */}
          <FormSection header="Práce" onWeb>
            <InlineSection>
              <Label required={isVolunteering}>Denní pracovní doba</Label>
              <FormInputError>
                <input
                  type="text"
                  {...register('propagation.working_hours', {
                    required: isVolunteering && required,
                  })}
                />
              </FormInputError>
            </InlineSection>
            {isCamp && (
              <InlineSection>
                <Label required={isVolunteering}>
                  Počet pracovních dní na akci
                </Label>
                <FormInputError>
                  <Controller
                    control={control}
                    name="propagation.working_days"
                    rules={{
                      required: isVolunteering && required,
                    }}
                    render={({ field }) => (
                      <NumberInput
                        {...field}
                        min={0}
                        name="propagation.working_days"
                      ></NumberInput>
                    )}
                  />
                </FormInputError>
              </InlineSection>
            )}
          </FormSection>
          <FormSection
            header="Web o akci"
            help="Možnost přidat odkaz na webovou stránku vaší akce."
            onWeb
          >
            <FormInputError>
              <input
                type="url"
                id="propagation.web_url"
                {...register('propagation.web_url', {})}
              />
            </FormInputError>
          </FormSection>
          <FormSection
            header="Poznámka"
            help="Možnost přidat interní poznámku. Poznámku uvidí pouze lidé, kteří si mohou tuto akci zobrazit přímo v BISu"
          >
            <FullSizeElement>
              <FormInputError>
                <textarea {...register('internal_note', {})} />
              </FormInputError>
            </FullSizeElement>
          </FormSection>
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
