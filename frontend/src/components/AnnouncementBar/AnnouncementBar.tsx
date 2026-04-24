import { api } from 'app/services/bis'
import { useCallback, useState } from 'react'
import styles from './AnnouncementBar.module.scss'

const STORAGE_KEY = 'dismissedAnnouncements'

const getDismissed = (): number[] => {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]')
  } catch {
    return []
  }
}

export const AnnouncementBar = () => {
  const { data: announcements } = api.useReadAnnouncementsQuery(undefined, {
    pollingInterval: 5 * 60 * 1000,
  })
  const [dismissed, setDismissed] = useState<number[]>(getDismissed)

  const dismiss = useCallback((id: number) => {
    setDismissed(prev => {
      const next = [...prev, id]
      localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
      return next
    })
  }, [])

  const active = (announcements ?? []).filter(a => !dismissed.includes(a.id))

  if (!active.length) return null

  return (
    <div>
      {active.map(announcement => (
        <div
          key={announcement.id}
          className={`${styles.bar} ${styles[announcement.severity]}`}
        >
          <span>{announcement.text}</span>
          <button
            className={styles.closeButton}
            onClick={() => dismiss(announcement.id)}
            aria-label="Zavřít"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}
