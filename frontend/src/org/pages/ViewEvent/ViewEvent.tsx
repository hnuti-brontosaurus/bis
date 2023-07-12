import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import {
  Actions,
  Breadcrumbs,
  Button,
  ButtonLink,
  DataView,
  ExternalButtonLink,
  Loading,
} from 'components'
import * as combinedTranslations from 'config/static/combinedTranslations'
import { sanitize } from 'dompurify'
import type { FullEvent } from 'hooks/readFullEvent'
// import { useRemoveEvent } from 'hooks/removeEvent'
import { useTitle } from 'hooks/title'
import { useAllowedToCreateEvent } from 'hooks/useAllowedToCreateEvent'
import { useCancelEvent, useRestoreCanceledEvent } from 'hooks/useCancelEvent'
import { mergeWith } from 'lodash'
import { getRegistrationMethodBeforeFull } from 'org/components/EventForm/EventForm'
import { AiOutlineStop } from 'react-icons/ai'
import {
  FaExternalLinkAlt,
  FaPencilAlt,
  FaRedo,
  FaRegCalendarAlt,
  FaRegCheckCircle,
  FaRegCopy,
  FaRegEye,
  // FaTrashAlt,
  FaUsers,
} from 'react-icons/fa'
import { GrLocation } from 'react-icons/gr'
import { useOutletContext, useParams } from 'react-router-dom'
import {
  formatDateRange,
  formatDateTime,
  isEventClosed,
  sortOrder,
  withOverwriteArray,
} from 'utils/helpers'
import styles from './ViewEvent.module.scss'

export const ViewEvent = ({ readonly }: { readonly?: boolean }) => {
  const params = useParams()
  const eventId = Number(params.eventId)
  const { event } = useOutletContext<{ event: FullEvent }>()
  const [canAddEvent] = useAllowedToCreateEvent()

  useTitle(`Akce ${event?.name ?? ''}`)

  const { data: administrationUnits } =
    api.endpoints.readAdministrationUnits.useQuery({ pageSize: 2000 })

  const { data: participants } = api.endpoints.readUsers.useQuery(
    event.record?.participants && event.record.participants.length > 0
      ? { id: event.record.participants }
      : skipToken,
  )

  // possibility to delete event was removed
  // const [removeEvent, { isLoading: isEventRemoving }] = useRemoveEvent()

  const [cancelEvent, { isLoading: isEventCanceling }] = useCancelEvent()
  const [restoreCanceledEvent, { isLoading: isEventRestoring }] =
    useRestoreCanceledEvent()

  // possibility to delete event was removed
  // if (isEventRemoving) return <Loading>Mažeme akci</Loading>

  if (isEventCanceling) return <Loading>Rušíme akci</Loading>

  if (isEventRestoring) return <Loading>Obnovujeme akci</Loading>

  const [mainImage, ...otherImages] = [...event.images].sort(sortOrder)

  const eventAdministrationUnits = event.administration_units.map(
    uid => administrationUnits?.results.find(au => au.id === uid)?.name ?? uid,
  )

  const formattedEvent = mergeWith(
    {},
    event,
    { administration_units: eventAdministrationUnits },
    participants?.results
      ? { record: { participants: participants.results } }
      : {},
    withOverwriteArray,
  )

  return (
    <>
      <Breadcrumbs eventName={event && event.name} />
      <div className={styles.wrapper}>
        <header className={styles.name}>{event.name}</header>
        {event.is_canceled && <div>(Akce je zrušena)</div>}
        <div className={styles.infoBox}>
          <div>
            <FaRegCalendarAlt /> {formatDateRange(event.start, event.end)}
          </div>
          <div>
            <GrLocation /> {event.location?.name}
          </div>
        </div>
        {!readonly && (
          <Actions>
            {!isEventClosed(event) ? (
              <>
                <ButtonLink secondary to={`/org/akce/${eventId}/upravit`}>
                  <FaPencilAlt /> upravit
                </ButtonLink>
                <ButtonLink secondary to={`/org/akce/${eventId}/uzavrit`}>
                  <FaRegCheckCircle /> po akci
                </ButtonLink>
              </>
            ) : null}
            {canAddEvent && (
              <ButtonLink
                secondary
                to={`/org/akce/vytvorit?klonovat=${eventId}`}
              >
                <FaRegCopy /> klonovat
              </ButtonLink>
            )}
            {!isEventClosed(event) ? (
              <>
                {getRegistrationMethodBeforeFull(event) === 'standard' && (
                  <ButtonLink to="prihlasky" secondary>
                    <FaUsers /> přihlášky
                  </ButtonLink>
                )}
                {getRegistrationMethodBeforeFull(event) === 'standard' && (
                  <ButtonLink secondary to={`/akce/${eventId}/prihlasit`}>
                    <FaRegEye /> přihláška
                  </ButtonLink>
                )}
                {getRegistrationMethodBeforeFull(event) === 'other' && (
                  <ExternalButtonLink
                    secondary
                    target="_blank"
                    rel="noopener noreferrer"
                    href={event.registration!.alternative_registration_link}
                  >
                    <FaRegEye /> přihláška <FaExternalLinkAlt />
                  </ExternalButtonLink>
                )}
                {event.is_canceled ? (
                  <Button secondary onClick={() => restoreCanceledEvent(event)}>
                    <FaRedo /> obnovit
                  </Button>
                ) : (
                  <Button danger onClick={() => cancelEvent(event)}>
                    <AiOutlineStop /> zrušit
                  </Button>
                )}
                {/* Possibility to delete event was removed, use Cancel ("zrušit") instead */}
                {/* <Button danger onClick={() => removeEvent(event)}>
                  <FaTrashAlt /> smazat
                </Button> */}
              </>
            ) : null}
          </Actions>
        )}

        <div className={styles.infoBoxDetail}>
          <div className={styles.imageWrapper}>
            {mainImage ? (
              <img
                className={styles.image}
                src={mainImage.image.medium}
                alt=""
              />
            ) : (
              <div className={styles.imageMissing}>
                Obrázek chybí
                {readonly || !event.propagation?.is_shown_on_web ? null : (
                  <ButtonLink to="upravit?krok=7">Přidat</ButtonLink>
                )}
              </div>
            )}
            <div className={styles.tags}>
              <div className={styles.tag}>{event.program.name}</div>
              <div className={styles.tag}>{event.group.name}</div>
            </div>
          </div>
          <table className={styles.table}>
            <tbody>
              <tr>
                <th>Datum</th>
                <td>{formatDateRange(event.start, event.end)}</td>
              </tr>
              <tr>
                <th>Místo</th>
                <td>{event.location?.name}</td>
              </tr>
              <tr>
                <th>Věk</th>
                <td>
                  {event.propagation?.minimum_age ?? '?'} -{' '}
                  {event.propagation?.maximum_age ?? '?'} let
                </td>
              </tr>
              <tr>
                <th>Začátek akce</th>
                <td>
                  {formatDateTime(event.start, event.start_time ?? undefined)}
                </td>
              </tr>
              <tr>
                <th>Cena</th>
                <td>{event.propagation?.cost} Kč</td>
              </tr>
              <tr>
                <th>Kontaktní osoba</th>
                <td>
                  <div>{event.propagation?.contact_name}</div>
                  <div>{event.propagation?.contact_phone}</div>
                  <div>{event.propagation?.contact_email}</div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className={styles.invitationTexts}>
          <header>Co na nás čeká</header>
          <section
            dangerouslySetInnerHTML={{
              __html: sanitize(
                event.propagation?.invitation_text_introduction ?? '',
              ),
            }}
          />
          <header>Co, kde a jak</header>
          <section
            dangerouslySetInnerHTML={{
              __html: sanitize(
                event.propagation?.invitation_text_practical_information ?? '',
              ),
            }}
          />
          <header>Dobrovolnická pomoc</header>
          <section
            dangerouslySetInnerHTML={{
              __html: sanitize(
                event.propagation?.invitation_text_work_description ?? '',
              ),
            }}
          />
          <header>Malá ochutnávka</header>
          <section
            dangerouslySetInnerHTML={{
              __html: sanitize(
                event.propagation?.invitation_text_about_us ?? '',
              ),
            }}
          />
          <div className={styles.imageList}>
            {otherImages.map(img => (
              <img
                className={styles.image}
                key={img.id}
                src={img.image.medium}
                alt=""
              />
            ))}
          </div>
        </div>
        {/* <pre className={styles.data}>{JSON.stringify(event, null, 2)}</pre> */}
        <h2 className={styles.dataHeader}>Data</h2>
        <DataView
          data={formattedEvent}
          translations={combinedTranslations.event}
          genericTranslations={combinedTranslations.generic}
        />
      </div>
    </>
  )
}
