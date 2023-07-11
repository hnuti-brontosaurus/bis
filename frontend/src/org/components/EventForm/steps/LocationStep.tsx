import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  InlineSection,
  SelectLocation,
} from 'components'
import { Controller, FormProvider } from 'react-hook-form'
import { getErrorMessage } from 'utils/helpers'
import { required } from 'utils/validationMessages'
import { MethodsShapes } from '..'

const formId = 'event-form-location-step'

export const LocationStep = ({
  methods,
}: {
  methods: MethodsShapes['location']
}) => {
  const { watch, register, control, formState } = methods

  return (
    <FormProvider {...methods}>
      <form id={formId} />
      <FormSectionGroup startIndex={9}>
        <FormSection header="Místo konání" required onWeb>
          <label className="checkboxLabel">
            <input form={formId} type="checkbox" {...register('online')} /> Akce
            se koná online
          </label>
          {watch('online') ? (
            <InlineSection>
              Odkaz na online setkání{' '}
              <FormInputError>
                <input type="url" form={formId} {...register('online_link')} />
              </FormInputError>
            </InlineSection>
          ) : (
            <Controller
              name="location"
              control={control}
              rules={{ required }}
              render={({ field }) => (
                <SelectLocation
                  {...field}
                  errorMessage={getErrorMessage(formState.errors, 'location')}
                />
              )}
            />
          )}
        </FormSection>
      </FormSectionGroup>
    </FormProvider>
  )
}
