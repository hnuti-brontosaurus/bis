import { Menu, MenuButton, MenuItem } from '@szhsin/react-menu'
import type { Opportunity } from 'app/services/bisTypes'
import styles from 'components/Table.module.scss'
import { useCurrentUser } from 'hooks/currentUser'
import { useRemoveOpportunity } from 'hooks/removeOpportunity'
import { TbDotsVertical } from 'react-icons/tb'
import { Link } from 'react-router-dom'

export const OpportunityTable = ({
  data: opportunities,
}: {
  data: Opportunity[]
}) => {
  const { data } = useCurrentUser()
  const userId = data!.id

  const [removeOpportunity, { isLoading: isOpportunityRemoving }] =
    useRemoveOpportunity()
  return (
    <table className={styles.table}>
      <thead>
        <tr>
          <th>Název</th>
          <th>Kategorie</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {opportunities &&
          opportunities.map(opportunity => (
            <tr key={opportunity.id}>
              <td>
                <Link to={`/org/prilezitosti/${opportunity.id}`}>
                  {opportunity.name}
                </Link>
              </td>
              <td>{opportunity.category.name}</td>
              <td>
                <Menu
                  menuButton={
                    <MenuButton>
                      <TbDotsVertical />
                    </MenuButton>
                  }
                >
                  <MenuItem>
                    <Link to={`/org/prilezitosti/${opportunity.id}/upravit`}>
                      upravit
                    </Link>
                  </MenuItem>
                  <MenuItem>
                    <button
                      disabled={isOpportunityRemoving}
                      onClick={() =>
                        removeOpportunity({
                          id: opportunity.id,
                          userId,
                          name: opportunity.name,
                        })
                      }
                    >
                      smazat
                    </button>
                  </MenuItem>
                </Menu>
              </td>
            </tr>
          ))}
      </tbody>
    </table>
  )
}
