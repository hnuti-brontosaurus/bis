import { FC } from 'react'
import { DashboardItem } from 'app/services/testApi'
import { formatDateTime } from 'utils/helpers'

export const Dashboard: FC<{ items: DashboardItem[] }> = ({ items }) => (
  <table>
    <tbody>{items.map(DashboardRow)}</tbody>
  </table>
)

const DashboardRow: FC<DashboardItem> = ({ date, name, description }) => (
  <>
    <tr>
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
