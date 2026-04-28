import { api } from 'app/services/bis'
import { Announcement } from 'app/services/bisTypes'
import { useCallback, useEffect, useState } from 'react'
import { MdClose, MdError, MdInfo, MdWarning } from 'react-icons/md'
import styles from './AnnouncementBar.module.scss'

const STORAGE_KEY = 'dismissedAnnouncements'

const getDismissed = (): number[] => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
  } catch {
    return []
  }
}

const severityClasses: Record<Announcement['severity'], string> = {
  info: styles.info,
  warning: styles.warning,
  error: styles.error,
}

const severityIcons: Record<Announcement['severity'], JSX.Element> = {
  info: <MdInfo size={20} />,
  warning: <MdWarning size={20} />,
  error: <MdError size={20} />,
}

export const AnnouncementBar = () => {
  const { data: announcements } = api.useReadAnnouncementsQuery(undefined, {
    pollingInterval: 5 * 60 * 1000,
  })
  const [dismissed, setDismissed] = useState<number[]>(getDismissed)

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(dismissed))
  }, [dismissed])

  const dismiss = useCallback((id: number) => {
    setDismissed(prev => [...prev, id])
  }, [])

  const active = (announcements ?? []).filter(a => !dismissed.includes(a.id))

  if (!active.length) return null

  return (
    <>
      {active.map(announcement => (
        <div
          key={announcement.id}
          className={`${styles.bar} ${severityClasses[announcement.severity]}`}
        >
          <span className={styles.icon}>
            {severityIcons[announcement.severity]}
          </span>
          <span>{announcement.text}</span>
          <button
            className={styles.closeButton}
            onClick={() => dismiss(announcement.id)}
            aria-label="Zavřít"
          >
            <MdClose size={20} />
          </button>
        </div>
      ))}
    </>
  )
}
