import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import { ListHeader } from 'components'
import listStyles from 'components/ListHeader/ListHeader.module.scss'
import { useCurrentUser } from 'hooks/currentUser'
import { ClearPageMargin, Content, Header, Layout } from 'layout/Layout'
import { Outlet } from 'react-router-dom'

export const UserEventsLayout = () => {
  const { data: currentUser } = useCurrentUser()

  const { data: events } = api.endpoints.readOrganizedEvents.useQuery(
    currentUser
      ? { userId: currentUser.id, page: 1, pageSize: 10000 } // fetch all and don't worry about it anymore
      : skipToken,
  )

  return (
    <ClearPageMargin style={{ height: '100%' }}>
      <Layout>
        <Header>
          <ListHeader
            header="Moje akce (uživatel/ka)"
            tabs={[
              {
                key: 'zucastnene',
                to: 'zucastnene',
                name: 'Účast',
              },
              {
                key: 'prihlasene',
                to: 'prihlasene',
                name: 'Přihlášení',
              },
            ]}
            actions={[]}
          />
        </Header>
        <Content>
          <div className={listStyles.listContent}>
            <Outlet context={events} />
          </div>
        </Content>
      </Layout>
    </ClearPageMargin>
  )
}
