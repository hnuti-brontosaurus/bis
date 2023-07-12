import { api } from 'app/services/bis'
import {
  ButtonLink,
  InfoMessage,
  ListHeader,
  Loading,
  UnscalablePaginatedList,
} from 'components'
import listStyles from 'components/ListHeader/ListHeader.module.scss'
import * as opportunityTexts from 'config/static/opportunity'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import { ClearPageMargin, Content, Header, Layout } from 'layout/Layout'
import { OpportunityTable } from 'org/components/OpportunityTable'
import { FaPlus } from 'react-icons/fa'

export const OpportunityList = () => {
  useTitle('Příležitosti')
  const { data: currentUser } = useCurrentUser()
  // it's safe to assume that the user is already loaded
  const userId = currentUser!.id
  const { data: opportunities } = api.endpoints.readOpportunities.useQuery({
    userId,
    page: 1,
    pageSize: 10000,
  })

  return (
    <ClearPageMargin style={{ height: '100%' }}>
      <Layout>
        <Header>
          <ListHeader
            header="Příležitosti"
            theme="opportunities"
            tabs={[]}
            actions={[
              <ButtonLink key="new" to="/org/prilezitosti/vytvorit">
                <FaPlus />
                Nová příležitost
              </ButtonLink>,
            ]}
          />
        </Header>
        <InfoMessage id="opportunity-list-about" closable>
          {opportunityTexts.about}
        </InfoMessage>
        <Content>
          {opportunities ? (
            <UnscalablePaginatedList
              data={opportunities.results}
              table={OpportunityTable}
              className={listStyles.listContent}
            />
          ) : (
            <Loading>Stahujeme příležitosti</Loading>
          )}
        </Content>
      </Layout>
    </ClearPageMargin>
  )
}
