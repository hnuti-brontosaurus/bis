import { skipToken } from '@reduxjs/toolkit/dist/query'
import { ALL_USERS, api } from 'app/services/bis'
import {
  Actions,
  Breadcrumbs,
  Button,
  ButtonLink,
  ExternalButtonLink,
  InfoBox,
  Loading,
} from 'components'
import { sanitize } from 'dompurify'
import type { FullEvent } from 'app/services/bisTypes'
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
  FaThumbsUp,
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
import { ExportFilesButton } from 'org/components'
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
      ? { id: event.record.participants, pageSize: ALL_USERS }
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

  function registration() {
    if (event.registration?.is_registration_required) {
      if (
        event.registration?.is_event_full &&
        event.registration?.alternative_registration_link == ''
      ) {
        return 'Akce je plná, dalo se přihlásit standardní přihláškou na brontowebu'
      } else if (
        event.registration?.is_event_full &&
        event.registration?.alternative_registration_link != ''
      ) {
        return 'Akce je plná, dalo se přihlásit pomocí jiné elektronické přihlášky'
      } else if (
        event.registration?.is_registration_required &&
        event.registration?.alternative_registration_link == ''
      ) {
        return (
          <>
            Standardní přihláška na brontoweb
            <p className={styles.invitationText}>
              <span className={styles.inlineHeader}> Úvod do dotazníku: </span>
              {event.registration?.questionnaire?.introduction}
            </p>
            <p className={styles.invitationText}>
              <span className={styles.inlineHeader}> Text po odeslání: </span>
              {event.registration?.questionnaire?.after_submit_text}
            </p>
          </>
        )
      } else if (
        event.registration?.is_registration_required &&
        event.registration?.alternative_registration_link != ''
      ) {
        return (
          'Jiná elektronická přihláška: ' +
          event.registration?.alternative_registration_link
        )
      }
    } else {
      return 'Registrace není potřeba'
    }
  }

  function vip() {
    return event?.vip_propagation ? (
      <>
        <header>VIP propagace</header>
        <section>
          <p className={styles.invitationText}>
            <span className={styles.inlineHeaderSmall}>
              Cíle akce a přínos pro prvoúčastníky:{' '}
            </span>
            {event?.vip_propagation?.goals_of_event}
          </p>
          <p className={styles.invitationText}>
            <span className={styles.inlineHeaderSmall}>
              Programové pojetí akce pro prvoúčastníky:{' '}
            </span>
            {event?.vip_propagation?.program}
          </p>
          <p className={styles.invitationText}>
            <span className={styles.inlineHeaderSmall}>
              Krátký zvací text do propagace:{' '}
            </span>
            {event?.vip_propagation?.short_invitation_text}
          </p>
          <p className={styles.invitationText}>
            <span className={styles.inlineHeaderSmall}>
              Propagovat akci v Roverském kmeni?:{' '}
            </span>
            {event?.vip_propagation?.rover_propagation ? 'ano' : 'ne'}
          </p>
        </section>
      </>
    ) : null
  }

  function work() {
    return event.propagation?.working_hours ? (
      <tr>
        <th>Práce</th>
        <td>
          Odpracovaných hodin (denně): {event.propagation?.working_hours}
          <br></br>
          {event.propagation?.working_days
            ? 'Počet pracovních dní: ' + event.propagation?.working_days
            : ''}
        </td>
      </tr>
    ) : null
  }

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
                  <FaRegCheckCircle /> účastníci + evidence akce
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
            <ExportFilesButton eventId={eventId} />
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
                {event.record?.feedback_form && (
                  <>
                    <ButtonLink
                      secondary
                      to={`/org/akce/${eventId}/zpetna_vazba`}
                    >
                      <FaThumbsUp /> zpětné vazby
                    </ButtonLink>
                    <ButtonLink secondary to={`/akce/${eventId}/zpetna_vazba`}>
                      <FaRegEye /> zpětná vazba
                    </ButtonLink>
                  </>
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

        {event.record?.feedback_form && (
          <InfoBox className={styles.feedbackLink}>
            Odkaz na formulář zpětné vazby, který můžeš poslat účastníkům:{' '}
            <ButtonLink to={`/akce/${eventId}/zpetna_vazba`} tertiary>
              {window.location.origin}/akce/{eventId}/zpetna_vazba
            </ButtonLink>
          </InfoBox>
        )}

        <div className={styles.infoBoxDetail}>
          <div className={styles.imageWrapper}>
            {mainImage ? (
              <img
                className={styles.mainImage}
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
              {event?.propagation ? (
                <tr>
                  <th>Věk</th>
                  <td>
                    {event.propagation?.minimum_age ?? '?'} -{' '}
                    {event.propagation?.maximum_age ?? '?'} let
                  </td>
                </tr>
              ) : null}
              <tr>
                <th>Začátek akce</th>
                <td>
                  {formatDateTime(event.start, event.start_time ?? undefined)}
                </td>
              </tr>
              {event?.propagation ? (
                <>
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
                </>
              ) : null}
            </tbody>
          </table>
        </div>
        <div className={styles.eventInfo}>
          <div className={styles.eventInfoNarrow}>
            <table className={styles.table}>
              <tbody>
                <tr>
                  <th>Druh</th>
                  <td>{event.group.name}</td>
                </tr>
                <tr>
                  <th>Typ</th>
                  <td> {event.category.name}</td>
                </tr>
                <tr>
                  <th>Program</th>
                  <td>{event.program.name}</td>
                </tr>
                <tr>
                  <th>Organizační jednotka</th>
                  <td>{eventAdministrationUnits}</td>
                </tr>
                {event.tags && event.tags.length > 0 ? (
                  <tr>
                    <th>Tagy</th>
                    <td>
                      {event.tags
                        .map(tag => {
                          if (typeof tag === 'object') return tag.name
                          else return tag
                        })
                        .join(', ')}
                    </td>
                  </tr>
                ) : null}
                <tr>
                  <th>Pro koho</th>
                  <td>{event.intended_for.name}</td>
                </tr>
                <tr>
                  <th>Místo konání</th>
                  <td>
                    {event.location?.name}
                    {event.location?.gps_location?.coordinates
                      ? `, GPS: ${event.location?.gps_location?.coordinates}`
                      : ''}
                    {event.online_link}
                  </td>
                </tr>
                <tr>
                  <th>Počet akcí v uvedeném období</th>
                  <td>{event?.number_of_sub_events}</td>
                </tr>
                {event?.propagation ? (
                  <>
                    <tr>
                      <th>Věk</th>
                      <td>
                        {event.propagation?.minimum_age ?? '?'} -{' '}
                        {event.propagation?.maximum_age ?? '?'} let
                      </td>
                    </tr>
                    <tr>
                      <th>Ubytování</th>
                      <td>
                        {' '}
                        {!event.propagation ||
                        event.propagation?.accommodation == ''
                          ? '-'
                          : event.propagation?.accommodation}
                      </td>
                    </tr>
                    <tr>
                      <th>Strava</th>
                      <td>
                        {event.propagation?.diets &&
                        event.propagation?.diets.length > 0
                          ? event.propagation?.diets
                              .map(diet => diet.name)
                              .join(', ')
                          : '-'}
                      </td>
                    </tr>
                  </>
                ) : null}
                {work()}
                {event?.propagation ? (
                  <tr>
                    <th>Web o akci</th>
                    <td>
                      {!event.propagation || event.propagation?.web_url == ''
                        ? '-'
                        : event.propagation?.web_url}
                    </td>
                  </tr>
                ) : null}
                <tr>
                  <th>Poznámka</th>
                  <td>
                    {event.internal_note == '' ? '-' : event.internal_note}
                  </td>
                </tr>
              </tbody>
            </table>
            {event?.propagation ? (
              <div className={styles.invitationTexts}>
                {vip()}
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
                      event.propagation
                        ?.invitation_text_practical_information ?? '',
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
              </div>
            ) : null}
          </div>

          {event?.propagation ? (
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
          ) : null}

          <div className={styles.eventInfoNarrow}>
            <table className={styles.table}>
              <tbody>
                <tr>
                  <th>Hlavní organizátor</th>
                  <td>{event.main_organizer?.display_name}</td>
                </tr>
                <tr>
                  <th>Organizační tým</th>
                  <td>
                    {event.other_organizers
                      .map(organizer => organizer.display_name)
                      .join(', ')}
                  </td>
                </tr>
                {event?.propagation ? (
                  <tr>
                    <th>Těší se na tebe</th>
                    <td>
                      {event.propagation ? event.propagation?.organizers : '-'}
                    </td>
                  </tr>
                ) : null}
                <tr>
                  <th>Způsob přihlášení</th>
                  <td>{registration()}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/*  <pre className={styles.data}>{JSON.stringify(event, null, 2)}</pre> */}
        {/*  <h2 className={styles.dataHeader}>Data</h2>
        <DataView
          data={formattedEvent}
          translations={combinedTranslations.event}
          genericTranslations={combinedTranslations.generic}
        /> */}
      </div>
    </>
  )
}
