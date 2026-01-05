import { api } from 'app/services/bis'
import { AdministrationUnit, EventTag } from 'app/services/bisTypes'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  FullSizeElement,
  InlineSection,
  Label,
  Loading,
  NumberInput,
  Help,
} from 'components'
import { useCurrentUser } from 'hooks/currentUser'
import { useEffect } from 'react'
import { Controller, FormProvider } from 'react-hook-form'
import Select from 'react-select'
import * as validationMessages from 'utils/validationMessages'
import { required } from 'utils/validationMessages'
import { MethodsShapes } from '..'

export const BasicInfoStep = ({
  methods,
}: {
  methods: MethodsShapes['basicInfo']
}) => {
  const { data: currentUser } = useCurrentUser()

  const { register, control, getValues, watch, trigger, formState } = methods
  const { data: categories } = api.endpoints.readEventCategories.useQuery()
  const { data: programs } = api.endpoints.readPrograms.useQuery()
  const { data: administrationUnits } =
    api.endpoints.readAdministrationUnits.useQuery({ pageSize: 2000 })
  const { data: tags } = api.endpoints.readEventTags.useQuery()

  // trigger validation of fields which are dependent on other fields
  useEffect(() => {
    const subscription = watch((_, { name }) => {
      if (formState.isSubmitted) {
        // the validations have to wait one tick
        // so the validation rule has time to update based on the other field
        setTimeout(() => {
          if (name === 'start') trigger('end')
          if (name === 'end') trigger('start')
        }, 0)
      }
    })
    return subscription.unsubscribe
  }, [formState.isSubmitted, trigger, watch])

  if (!(administrationUnits && categories && programs && currentUser))
    return <Loading>Připravujeme formulář</Loading>

  const currentCategory = categories.results.find(
    category => category.id == watch('category'),
  )
  const canChooseCategory =
    typeof currentCategory === 'undefined' || currentCategory.is_active

  return (
    <FormProvider {...methods}>
      <form>
        <FormSectionGroup startIndex={2}>
          <FormSection header="Název" required onWeb>
            <FormInputError>
              <input
                type="text"
                {...register('name', {
                  required,
                })}
              />
            </FormInputError>
          </FormSection>
          <FormSection header="Kdy bude akce?" onWeb>
            <InlineSection>
              <InlineSection>
                <Label htmlFor="start" required>
                  Od
                </Label>
                <FormInputError>
                  <input
                    type="date"
                    id="start"
                    max={watch('end')}
                    {...register('start', {
                      required,
                      max: {
                        value: watch('end'),
                        message: validationMessages.startBeforeEnd,
                      },
                    })}
                  />
                </FormInputError>
                <FormInputError>
                  <input type="time" {...register('start_time')} />
                </FormInputError>
              </InlineSection>
              <InlineSection>
                <Label htmlFor="end" required>
                  Do
                </Label>
                <FormInputError>
                  <input
                    type="date"
                    id="end"
                    min={watch('start')}
                    {...register('end', {
                      required,
                      min: {
                        value: watch('start'),
                        message: validationMessages.endAfterStart,
                      },
                    })}
                  />
                </FormInputError>
              </InlineSection>
            </InlineSection>
          </FormSection>
          <FormSection
            header="Počet akcí v uvedeném období"
            help="Používá se u opakovaných akcí (např. oddílové schůzky). U klasické jednorázové akce zde nechte jedničku."
            required
          >
            <FormInputError>
              <Controller
                control={control}
                name="number_of_sub_events"
                rules={{
                  required,
                }}
                render={({ field }) => (
                  <NumberInput
                    {...field}
                    min={1}
                    name="number_of_sub_events"
                  ></NumberInput>
                )}
              />
            </FormInputError>
          </FormSection>
        </FormSectionGroup>
        <FormSectionGroup startIndex={5}>
          <FormSection header="Typ akce" required>
            <FullSizeElement>
              <FormInputError>
                <select
                  {...register('category', { required })}
                  disabled={!canChooseCategory}
                  defaultValue=""
                >
                  <option disabled value="" />
                  {categories
                    .results!.filter(category =>
                      canChooseCategory
                        ? category.is_active
                        : watch('category') == category.id,
                    )
                    .map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                </select>
              </FormInputError>
            </FullSizeElement>
          </FormSection>
          <FormSection header="Program" required>
            <FullSizeElement>
              <FormInputError>
                <select {...register('program', { required })} defaultValue="">
                  <option disabled value="" />
                  {programs &&
                    programs.results!.map(program => (
                      <option key={program.id} value={program.id}>
                        {program.name}
                      </option>
                    ))}
                </select>
              </FormInputError>
            </FullSizeElement>
            <FullSizeElement>
              <FormInputError>
                <Controller
                  name="tags"
                  control={control}
                  render={({ field }) => (
                    <fieldset>
                      <InlineSection>
                        {tags &&
                          tags.results!.map(
                            ({ id, name, slug, description, is_active }) =>
                              is_active ? (
                                <div key={slug}>
                                  <label key={slug}>
                                    <span className="checkboxLabelWrapper">
                                      <span className="checkboxLabel">
                                        <input
                                          ref={field.ref}
                                          key={slug}
                                          type="checkbox"
                                          name={field.name}
                                          id={slug}
                                          value={id}
                                          checked={
                                            field.value
                                              ?.map(
                                                (val: number | EventTag) => {
                                                  if (typeof val === 'number') {
                                                    return val
                                                  } else if (
                                                    typeof val === 'object'
                                                  ) {
                                                    return val.id
                                                  }
                                                },
                                              )
                                              .includes(id) ?? false
                                          }
                                          onChange={e => {
                                            // check when unchecked and vise-versa
                                            const targetId = Number(
                                              e.target.value,
                                            )
                                            const currentSet: number[] = []
                                            field.value?.forEach(
                                              (item: number | EventTag) => {
                                                if (typeof item === 'number') {
                                                  if (
                                                    !currentSet.includes(item)
                                                  )
                                                    currentSet.push(item)
                                                } else if (
                                                  !currentSet.includes(item.id)
                                                ) {
                                                  // item is EventTag
                                                  currentSet.push(item.id)
                                                }
                                              },
                                            )
                                            const set = new Set(currentSet)
                                            if (set.has(targetId)) {
                                              set.delete(targetId)
                                            } else {
                                              set.add(targetId)
                                            }
                                            field.onChange(Array.from(set))
                                          }}
                                        />{' '}
                                        {name}
                                      </span>
                                    </span>
                                    <span className="checkboxDesription">
                                      <Help>{description}</Help>
                                    </span>
                                  </label>
                                </div>
                              ) : null,
                          )}
                      </InlineSection>
                    </fieldset>
                  )}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSection>
          <FormSection header="Pořádající organizační jednotka" required onWeb>
            <FullSizeElement>
              <FormInputError>
                <Controller
                  name="administration_units"
                  rules={{ required }}
                  control={control}
                  render={({ field: { onChange /*, value, name, ref */ } }) => (
                    <Select
                      isMulti
                      options={
                        administrationUnits
                          ? administrationUnits.results.map(unit => ({
                              label: `${unit.abbreviation}`,
                              value: unit.id,
                            }))
                          : []
                      }
                      onChange={val => onChange(val.map(val => val.value))}
                      defaultValue={(
                        (getValues('administration_units') ?? [])
                          .map(id =>
                            administrationUnits.results.find(
                              unit => id === unit.id,
                            ),
                          )
                          .filter(a => !!a) as AdministrationUnit[]
                      ).map(unit => ({
                        label: `${unit.abbreviation}`,
                        value: unit.id,
                      }))}
                    />
                  )}
                />
              </FormInputError>
            </FullSizeElement>
          </FormSection>
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
