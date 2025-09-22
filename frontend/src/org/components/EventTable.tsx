import { Menu, MenuButton, MenuItem } from '@szhsin/react-menu'
import { api } from 'app/services/bis'
import { Event } from 'app/services/bisTypes'
import classNames from 'classnames'
import styles from 'components/Table.module.scss'
import { useQueries } from 'hooks/queries'
// import { useRemoveEvent } from 'hooks/removeEvent'
import { useAllowedToCreateEvent } from 'hooks/useAllowedToCreateEvent'
import { useCancelEvent, useRestoreCanceledEvent } from 'hooks/useCancelEvent'
import { FC, ReactElement, useMemo } from 'react'
import { AiOutlineStop } from 'react-icons/ai'
import { FaRegCheckCircle } from 'react-icons/fa'
import { TbDotsVertical } from 'react-icons/tb'
import { Link, useNavigate } from 'react-router-dom'
import { formatDateRange } from 'utils/helpers'

/**
 * A list of default actions for different event statuses
 */

interface EventAction {
  title: string
  link: string
  icon: ReactElement
}

const getEventAction = (event: Event): EventAction => {
  if (event.is_canceled) {
    return {
      title: 'akce zrušena',
      link: `/org/akce/${event.id}`,
      icon: <AiOutlineStop className={styles.canceled} />,
    }
  } else if (event.is_archived) {
    return {
      title: 'akce je archivovaná (prohlédnout akci)',
      link: `/org/akce/${event.id}`,
      icon: <FaRegCheckCircle className={styles.closed} />,
    }
  } else if (event.is_closed) {
    return {
      title: 'akce je uzavřená (prohlédnout akci)',
      link: `/org/akce/${event.id}`,
      icon: <FaRegCheckCircle className={styles.finished} />,
    }
  } else {
    return {
      title: 'akce je otevřená (nahrát povinné informace po akci)',
      link: `/org/akce/${event.id}/uzavrit`,
      icon: <FaRegCheckCircle className={styles.inProgress} />,
    }
  }
}

export const EventTable: FC<{
  data: Event[]
  action?: 'view' | 'edit' | 'finish'
  columnsToHideOnMobile?: number[]
}> = ({ data: events, action = 'view', columnsToHideOnMobile }) => {
  const locationRequests = useQueries(
    api.endpoints.readLocation,
    useMemo(
      () =>
        events
          .filter(event => event.location)
          .map(event => ({ id: event.location as number })),
      [events],
    ),
  )

  // possibility to delete event was removed
  // const [removeEvent, { isLoading: isEventRemoving }] = useRemoveEvent()
  const [cancelEvent, { isLoading: isEventCanceling }] = useCancelEvent()
  const [restoreCanceledEvent, { isLoading: isEventRestoring }] =
    useRestoreCanceledEvent()
  const [canAddEvent] = useAllowedToCreateEvent()
  const navigate = useNavigate()

  return (
    <table
      className={classNames(styles.table, styles.verticalLine1, 'tableEvents')}
    >
      <thead>
        <tr>
          <th
            className={classNames(
              columnsToHideOnMobile?.includes(1) && 'mobileHiddenCell',
            )}
          >
            Status
          </th>
          <th
            className={classNames(
              columnsToHideOnMobile?.includes(2) && 'mobileHiddenCell',
            )}
          >
            Název
          </th>
          <th
            className={classNames(
              columnsToHideOnMobile?.includes(3) && 'mobileHiddenCell',
            )}
          >
            Termín
          </th>
          <th
            className={classNames(
              columnsToHideOnMobile?.includes(4) && 'mobileHiddenCell',
            )}
          >
            Lokalita
          </th>
          <th
            className={classNames(
              columnsToHideOnMobile?.includes(5) && 'mobileHiddenCell',
            )}
          ></th>
        </tr>
      </thead>
      <tbody>
        {events.map(event => {
          const eventAction = getEventAction(event)
          return (
            <tr key={event.id}>
              <td
                className={classNames(
                  'cellWithButton',
                  columnsToHideOnMobile?.includes(1) && 'mobileHiddenCell',
                )}
              >
                <Link title={eventAction.title} to={eventAction.link}>
                  {eventAction.icon}
                </Link>
              </td>
              <td
                onClick={() => {
                  navigate(
                    `/org/akce/${event.id}` +
                      (action === 'finish' ? '/uzavrit' : ''),
                  )
                }}
                className={classNames(
                  columnsToHideOnMobile?.includes(2) && 'mobileHiddenCell',
                )}
              >
                {event.name}
              </td>
              <td
                onClick={() => {
                  navigate(
                    `/org/akce/${event.id}` +
                      (action === 'finish' ? '/uzavrit' : ''),
                  )
                }}
                className={classNames(
                  columnsToHideOnMobile?.includes(3) && 'mobileHiddenCell',
                )}
              >
                {formatDateRange(event.start, event.end)}
              </td>
              <td
                onClick={() => {
                  navigate(
                    `/org/akce/${event.id}` +
                      (action === 'finish' ? '/uzavrit' : ''),
                  )
                }}
                className={classNames(
                  columnsToHideOnMobile?.includes(4) && 'mobileHiddenCell',
                )}
              >
                {
                  locationRequests.find(
                    request => request.data?.id === event?.location,
                  )?.data?.name
                }
              </td>
              <td
                className={classNames(
                  'cellWithButton',
                  columnsToHideOnMobile?.includes(1) && 'mobileHiddenCell',
                )}
              >
                <Menu
                  menuButton={
                    <MenuButton>
                      <div className={'cellWithButtonMenuIcon'}>
                        <TbDotsVertical />
                      </div>
                    </MenuButton>
                  }
                  className={styles.buttonInsideCell}
                >
                  {!event.is_archived && (
                    <MenuItem>
                      <Link to={`/org/akce/${event.id}/upravit`}>upravit</Link>
                    </MenuItem>
                  )}
                  {canAddEvent && (
                    <MenuItem>
                      <Link to={`/org/akce/vytvorit?klonovat=${event.id}`}>
                        klonovat
                      </Link>
                    </MenuItem>
                  )}
                  {!event.is_archived && (
                    <>
                      <MenuItem>
                        <Link to={`/org/akce/${event.id}/uzavrit`}>
                          po akci
                        </Link>
                      </MenuItem>
                      <MenuItem>
                        {event.is_canceled ? (
                          <button
                            disabled={isEventRestoring}
                            onClick={() => restoreCanceledEvent(event)}
                          >
                            obnovit
                          </button>
                        ) : (
                          <button
                            disabled={isEventCanceling}
                            onClick={() => cancelEvent(event)}
                          >
                            zrušit
                          </button>
                        )}
                      </MenuItem>
                      {/* Possibility to delete event was removed, use Cancel ("zrušit") instead */}
                      {/* <MenuItem>
                        <button
                          disabled={isEventRemoving}
                          onClick={() => removeEvent(event)}
                        >
                          smazat
                        </button>
                      </MenuItem> */}
                    </>
                  )}
                </Menu>
              </td>
            </tr>
          )
        })}
      </tbody>
    </table>
  )
}
