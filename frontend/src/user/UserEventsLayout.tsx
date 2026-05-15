import { ListHeader } from 'components'
import listStyles from 'components/ListHeader/ListHeader.module.scss'
import { ClearPageMargin, Content, Header, Layout } from 'layout/Layout'
import { Outlet } from 'react-router-dom'

export const UserEventsLayout = () => {
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
            <Outlet />
          </div>
        </Content>
      </Layout>
    </ClearPageMargin>
  )
}
