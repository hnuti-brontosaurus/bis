import { FC } from 'react'
import { DashboardItem } from 'app/services/testApi'
import { formatDateTime } from 'utils/helpers'
import classNames from 'classnames'
import styles from './Dashboard.module.scss'

export const Dashboard: FC<{ items: DashboardItem[] }> = ({ items }) => (
  <div className={styles.main}>
    <table>
      <tbody>{items.map(DashboardRow)}</tbody>
    </table>
  </div>
)

const DashboardRow: FC<DashboardItem> = ({ date, name, description }) => (
  <>
    <tr className={classNames(styles.title, { [styles.single]: !description })}>
      <td>{formatDateTime(date)}</td>
      <td>{name}</td>
    </tr>
    {description && (
      <tr className={styles.description}>
        <td colSpan={2}>{description}</td>
      </tr>
    )}
  </>
)
