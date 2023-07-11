import { api } from 'app/services/bis'
import { AdministrationUnit } from 'app/services/bisTypes'
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
import { useCurrentUser } from 'hooks/currentUser'
import { useEffect } from 'react'
import { Controller, FormProvider } from 'react-hook-form'
import Select from 'react-select'
import { getEventCannotBeOlderThan } from 'utils/helpers'
import { canUserSaveOldEvent } from 'utils/roles'
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

  const isAllowedToSaveOldEvents = canUserSaveOldEvent(currentUser)

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
                    min={
                      isAllowedToSaveOldEvents
                        ? undefined
                        : getEventCannotBeOlderThan()
                    }
                    {...register('start', {
                      required,
                      max: {
                        value: watch('end'),
                        message: validationMessages.startBeforeEnd,
                      },
                      min: isAllowedToSaveOldEvents
                        ? undefined
                        : {
                            value: getEventCannotBeOlderThan(),
                            message: validationMessages.oldEvent,
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
                <select {...register('category', { required })} defaultValue="">
                  <option disabled value="" />
                  {categories &&
                    categories.results!.map(category => (
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
                              label: `${unit.category.name} ${unit.abbreviation}`,
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
                        label: `${unit.category.name} ${unit.abbreviation}`,
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
