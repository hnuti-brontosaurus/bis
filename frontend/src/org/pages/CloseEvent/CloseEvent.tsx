import { api } from 'app/services/bis'
import type { EventPayload, FullEvent } from 'app/services/bisTypes'
import { Breadcrumbs, GuideOwl, Loading } from 'components'
import {
  useShowApiErrorMessage,
  useShowMessage,
} from 'features/systemMessage/useSystemMessage'
import { useTitle } from 'hooks/title'
import { useUpdateInquiries } from 'hooks/useUpdateInquiries'
import { defaultsDeep, cloneDeep, omit } from 'lodash'
import { useState } from 'react'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { sortOrder } from 'utils/helpers'
import { CloseEventForm, CloseEventPayload } from './CloseEventForm'

export const CloseEvent = () => {
  const params = useParams()
  const eventId = Number(params.eventId)
  const navigate = useNavigate()

  const [isSubmitting, setSubmitting] = useState(false)

  const { event } = useOutletContext<{ event: FullEvent }>()
  const { data: inquiries } = api.endpoints.readEventFeedbackInquiries.useQuery(
    { eventId },
  )

  const showMessage = useShowMessage()

  useTitle(event ? `Evidence akce ${event.name}` : 'Evidence akce')

  const [updateEvent, { error: updateEventError }] =
    api.endpoints.updateEvent.useMutation()
  const updateInquiries = useUpdateInquiries()

  useShowApiErrorMessage(updateEventError)

  if (!inquiries) return <Loading>Stahujeme data</Loading>

  if (isSubmitting) {
    return <Loading>Ukládáme změny</Loading>
  }

  const defaultValues = {
    record: defaultsDeep(cloneDeep(event.record), {
      is_event_closed_email_enabled: true,
    }),
    feedback_form: omit(event.feedback_form, ['sent_at']),
    finance: event.finance ?? undefined,
    inquiries: inquiries.results.slice().sort(sortOrder),
  }

  const handleSubmit = async ({
    inquiries,
    ...evidence
  }: CloseEventPayload) => {
    try {
      setSubmitting(true)
      await updateEvent({
        id: eventId,
        event: evidence as Partial<EventPayload>,
      }).unwrap()

      await Promise.all(
        updateInquiries(eventId, inquiries, defaultValues.inquiries),
      )

      const needsClosing = !evidence.is_closed && !event.is_closed
      const message = `Evidence akce byla úspěšně uložena${
        evidence.is_closed
          ? ' a uzavřena'
          : evidence.feedback_form?.sent_at
            ? ' a zpětná vazba byla odeslána'
            : ''
      }.`
      showMessage({
        type: needsClosing ? 'warning' : 'success',
        message:
          message +
          (needsClosing
            ? ' Nezapomeň akci ještě uzavřít! Akci uzavřeš kliknutím na tlačítko "uložit a uzavřít" do 20 dnů od skončení akce.'
            : ''),
        timeout: event.is_closed ? 5000 : 10_000,
      })

      navigate(`/org/akce/${eventId}`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleCancel = () => {
    navigate(`/org/akce/${eventId}`)
  }

  return (
    <>
      <Breadcrumbs eventName={event && event.name} />

      <CloseEventForm
        id={String(eventId)}
        event={event}
        initialData={defaultValues}
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
      <GuideOwl id="po-akce-guide-owl">
        Akce musí být uzavřená (tj. mít kompletně vyplněné povinné údaje po
        akci) do 20 dnů od skončení.
        <br />
        Akci uzavřeš tak, že klikneš na tlačítko "uložit a uzavřít"
      </GuideOwl>
    </>
  )
}
