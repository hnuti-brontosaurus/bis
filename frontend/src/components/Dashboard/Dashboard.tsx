import { FC } from 'react'
import { DashboardItem } from 'app/services/testApi'
import { formatDateTime } from 'utils/helpers'
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
    <tr className={styles.row}>
      <td>{formatDateTime(date)}</td>
      <td>{name}</td>
    </tr>
    {description && (
      <tr>
        <td colSpan={2}>{description}</td>
      </tr>
    )}
  </>
)
