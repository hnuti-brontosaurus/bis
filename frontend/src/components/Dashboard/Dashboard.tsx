import { FC } from 'react'
import { DashboardItem } from 'app/services/testApi'
import { formatDateTime } from 'utils/helpers'
import classNames from 'classnames'
import styles from './Dashboard.module.scss'

export const Dashboard: FC<{ items: DashboardItem[] }> = ({ items }) => (
  <div className={styles.main}>{items.map(DashboardRow)}</div>
)

const DashboardRow: FC<DashboardItem> = ({ date, name, description }) => (
  <>
    <div className={classNames(styles.date, { [styles.single]: !description })}>
      {formatDateTime(date)}
    </div>
    <div
      className={classNames(styles.title, { [styles.single]: !description })}
    >
      {name}
    </div>
    {description && <div className={styles.description}>{description}</div>}
  </>
)
