import { api } from 'app/services/bis'
import {
  ButtonLink,
  InfoMessage,
  ListHeader,
  Loading,
  PAGINATED_LIST_PAGE_SIZE,
  PaginatedList,
} from 'components'
import listStyles from 'components/ListHeader/ListHeader.module.scss'
import * as opportunityTexts from 'config/static/opportunity'
import { useCurrentUser } from 'hooks/currentUser'
import { useSearchParamsState } from 'hooks/searchParamsState'
import { useTitle } from 'hooks/title'
import { ClearPageMargin, Content, Header, Layout } from 'layout/Layout'
import { OpportunityTable } from 'org/components/OpportunityTable'
import { FaExternalLinkAlt, FaPlus } from 'react-icons/fa'
import { ExternalButtonLink } from 'components/Button/Button'

export const OpportunityList = () => {
  useTitle('Příležitosti')
  const { data: currentUser } = useCurrentUser()
  const userId = currentUser!.id
  const [page, setPage] = useSearchParamsState('s', 1, Number)
  const { data: opportunities } = api.endpoints.readOpportunities.useQuery({
    userId,
    page,
    pageSize: PAGINATED_LIST_PAGE_SIZE,
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
              <ExternalButtonLink
                key="apply-link"
                href="https://docs.google.com/forms/d/e/1FAIpQLSdkhNLXC3YvMFgykj8r8KrQ_-xwfcZr13Hsfyy5Diyyvx2JLg/viewform"
                target="__blank"
                rel="noopener noreferrer"
              >
                <FaExternalLinkAlt />
                Chci se zapojit
              </ExternalButtonLink>,
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
            <PaginatedList
              data={opportunities.results}
              totalCount={opportunities.count}
              page={page}
              pageSize={PAGINATED_LIST_PAGE_SIZE}
              onPageChange={setPage}
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
