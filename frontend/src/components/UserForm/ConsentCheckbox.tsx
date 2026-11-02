import { FormInputError, InlineSection, Label } from 'components'
import { Controller, useFormContext } from 'react-hook-form'
import type { UserFormShape } from './UserForm'

// The model stores refusals, while the form asks for consent.
export const ConsentCheckbox = ({
  name,
  label,
}: {
  name: 'do_not_call' | 'do_not_solicit' | 'do_not_send_after_event_email'
  label: string
}) => {
  const { control } = useFormContext<UserFormShape>()
  return (
    <InlineSection>
      <Label htmlFor={name}>{label}</Label>
      <FormInputError>
        <Controller
          control={control}
          name={name}
          render={({ field }) => (
            <input
              type="checkbox"
              id={name}
              checked={!field.value}
              onChange={event => field.onChange(!event.target.checked)}
            />
          )}
        />
      </FormInputError>
    </InlineSection>
  )
}
