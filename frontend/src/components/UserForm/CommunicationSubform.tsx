import { FormInputError, InlineSection, Label } from 'components'
import { subscriptionStatus } from 'config/subscriptionStatus'
import { Controller, useFormContext } from 'react-hook-form'
import { ConsentCheckbox } from './ConsentCheckbox'
import type { UserFormShape } from './UserForm'

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
