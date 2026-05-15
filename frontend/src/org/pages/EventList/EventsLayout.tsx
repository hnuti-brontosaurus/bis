import { ListHeader } from 'components'
import listStyles from 'components/ListHeader/ListHeader.module.scss'
import { ClearPageMargin, Content, Header, Layout } from 'layout/Layout'
import { useMemo } from 'react'
import { Outlet, useLocation } from 'react-router-dom'

export const EventsLayout = () => {
  const location = useLocation()

  const pathnameThemes = useMemo(
    () =>
      ({
        '/org/akce/aktualni': 'editEvent',
        '/org/akce/vsechny': 'editEvent',
        '/org/akce/nevyplnene': 'closeEvent',
      }) as const,
    [],
  )

  const theme = pathnameThemes[location.pathname as keyof typeof pathnameThemes]

  return (
    <ClearPageMargin style={{ height: '100%' }}>
      <Layout>
        <Header>
          <ListHeader
            header="Moje akce (organizátor/ka)"
            theme={theme}
            tabs={[
              {
                key: 'vsechny',
                to: 'vsechny',
                name: 'Všechny akce',
              },
              {
                key: 'nevyplnene',
                to: 'nevyplnene',
                name: 'Nevyplněné akce',
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
