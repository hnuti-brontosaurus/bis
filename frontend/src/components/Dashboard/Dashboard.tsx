import { FC } from 'react'
import { DashboardItem } from 'app/services/testApi'
import classNames from 'classnames'
import { formatDateTime } from 'utils/helpers'
import styles from './Dashboard.module.scss'

export const Dashboard: FC<{ items: DashboardItem[] }> = ({ items }) => (
  <div className={styles.main}>{items.map(DashboardRow)}</div>
)

const DashboardRow: FC<DashboardItem> = ({
  visible_date,
  name,
  description,
  date,
}) => (
  <>
    <div
      className={classNames(styles.date, { [styles.single]: !description })}
      dangerouslySetInnerHTML={{ __html: visible_date || formatDateTime(date) }}
    />
    <div
      className={classNames(styles.title, { [styles.single]: !description })}
      dangerouslySetInnerHTML={{ __html: name }}
    />
    {description && (
      <div
        className={styles.description}
        dangerouslySetInnerHTML={{ __html: description }}
      />
    )}
  </>
)
