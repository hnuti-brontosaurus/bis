import classNames from 'classnames'
import { cloneElement, ReactElement } from 'react'
import { NavLink, To } from 'react-router-dom'
import styles from './ListHeader.module.scss'

export const ListHeader = ({
  header,
  tabs,
  actions,
  theme,
}: {
  header: string
  tabs: { to: To; name: string; key: string }[]
  actions: ReactElement[]
  theme?: 'createEvent' | 'editEvent' | 'closeEvent' | 'opportunities'
}) => {
  const themeClass = theme && styles[theme]

  return (
    <header className={classNames(styles.header, themeClass)}>
      <h1>{header}</h1>
      {actions.map(element =>
        cloneElement(element, {
          className: styles.headerActionButton,
        }),
      )}
      <nav className={styles.tabs}>
        {tabs.map(({ name, to, key }) => (
          <NavLink
            key={key}
            to={to}
            className={({ isActive }) =>
              classNames(isActive && styles.active, styles.tab)
            }
          >
            {name}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
