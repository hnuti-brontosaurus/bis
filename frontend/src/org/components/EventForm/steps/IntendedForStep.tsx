import { api } from 'app/services/bis'
import {
  FormInputError,
  FormSection,
  FormSectionGroup,
  InlineSection,
  Loading,
} from 'components'
import { Controller, FormProvider } from 'react-hook-form'
import { required } from 'utils/validationMessages'
import { MethodsShapes } from '..'

export const IntendedForStep = ({
  methods,
}: {
  methods: MethodsShapes['intendedFor']
}) => {
  const { data: intendedFor } =
    api.endpoints.readIntendedFor.useQuery(undefined)
  const { watch, register, trigger, control, unregister, setValue, formState } =
    methods

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
        </FormSectionGroup>
      </form>
    </FormProvider>
  )
}
