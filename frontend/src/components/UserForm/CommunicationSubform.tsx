import { subscriptionStatus } from 'config/subscriptionStatus'
import { Controller, useFormContext } from 'react-hook-form'
import { FormInputError } from '../FormInputError/FormInputError'
import { InlineSection, Label } from '../FormLayout/FormLayout'
import type { UserFormShape } from './UserForm'

// The model stores refusals; the form asks for consent, so it shows them inverted.
const ConsentCheckbox = ({
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

export const CommunicationSubform = ({
  isHardBounce,
}: {
  isHardBounce: boolean
}) => {
  const { control } = useFormContext<UserFormShape>()
  return (
    <>
      {isHardBounce ? (
        <InlineSection>
          <Label>Posílat newsletter?</Label>
          <span>Newsletter na tento e-mail nelze doručit.</span>
        </InlineSection>
      ) : (
        <InlineSection>
          <Label htmlFor="subscription_status">Posílat newsletter?</Label>
          <FormInputError>
            <Controller
              control={control}
              name="subscription_status"
              render={({ field }) => (
                <input
                  type="checkbox"
                  id="subscription_status"
                  checked={field.value === subscriptionStatus.subscribed}
                  onChange={event =>
                    field.onChange(
                      event.target.checked
                        ? subscriptionStatus.subscribed
                        : subscriptionStatus.unsubscribed,
                    )
                  }
                />
              )}
            />
          </FormInputError>
        </InlineSection>
      )}
      <ConsentCheckbox name="do_not_call" label="Můžeme ti zavolat?" />
      <ConsentCheckbox
        name="do_not_solicit"
        label="Můžeme tě požádat o finanční podporu?"
      />
      <ConsentCheckbox
        name="do_not_send_after_event_email"
        label="Můžeme ti po akci poslat info e-mail (max. 1 za půl roku)?"
      />
    </>
  )
}
