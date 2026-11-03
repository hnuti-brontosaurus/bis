import { FormInputError, InlineSection, Label } from 'components'
import { subscriptionStatus } from 'config/subscriptionStatus'
import { FC } from 'react'
import { Controller } from 'react-hook-form'

interface CommunicationSubformProps {
  isHardBounce: boolean
}

export const CommunicationSubform: FC<CommunicationSubformProps> = ({
  isHardBounce,
}) => (
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
            name="subscription_status"
            render={({ field: { value, onChange, ...field } }) => (
              <input
                type="checkbox"
                id="subscription_status"
                {...field}
                checked={value === subscriptionStatus.subscribed}
                onChange={event =>
                  onChange(
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
    <InlineSection>
      <Label htmlFor="do_not_call">Můžeme ti zavolat?</Label>
      <FormInputError>
        <Controller
          name="do_not_call"
          render={({ field: { value, onChange, ...field } }) => (
            <input
              type="checkbox"
              id="do_not_call"
              {...field}
              checked={!value}
              onChange={event => onChange(!event.target.checked)}
            />
          )}
        />
      </FormInputError>
    </InlineSection>
    <InlineSection>
      <Label htmlFor="do_not_solicit">
        Můžeme tě požádat o finanční podporu?
      </Label>
      <FormInputError>
        <Controller
          name="do_not_solicit"
          render={({ field: { value, onChange, ...field } }) => (
            <input
              type="checkbox"
              id="do_not_solicit"
              {...field}
              checked={!value}
              onChange={event => onChange(!event.target.checked)}
            />
          )}
        />
      </FormInputError>
    </InlineSection>
    <InlineSection>
      <Label htmlFor="do_not_send_after_event_email">
        Můžeme ti po akci poslat info e-mail (max. 1 za půl roku)?
      </Label>
      <FormInputError>
        <Controller
          name="do_not_send_after_event_email"
          render={({ field: { value, onChange, ...field } }) => (
            <input
              type="checkbox"
              id="do_not_send_after_event_email"
              {...field}
              checked={!value}
              onChange={event => onChange(!event.target.checked)}
            />
          )}
        />
      </FormInputError>
    </InlineSection>
  </>
)
