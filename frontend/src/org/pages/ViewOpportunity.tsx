import classNames from 'classnames'
import { Actions, Button, ButtonLink, DataView, Loading } from 'components'
import * as combinedTranslations from 'config/static/combinedTranslations'
import { sanitize } from 'dompurify'
import { useCurrentUser } from 'hooks/currentUser'
import type { FullOpportunity } from 'hooks/readFullOpportunity'
import { useRemoveOpportunity } from 'hooks/removeOpportunity'
import { useTitle } from 'hooks/title'
import styles from 'org/pages/ViewEvent/ViewEvent.module.scss'
import { useNavigate, useOutletContext, useParams } from 'react-router-dom'
import { formatDateRange } from 'utils/helpers'

export const ViewOpportunity = () => {
  const params = useParams()
  const opportunityId = Number(params.opportunityId)
  const { data: user } = useCurrentUser()
  const userId = user!.id

  const navigate = useNavigate()

  const { opportunity } = useOutletContext<{ opportunity: FullOpportunity }>()

  useTitle(`Příležitost ${opportunity?.name ?? ''}`)

  const [removeOpportunity, { isLoading: isOpportunityRemoving }] =
    useRemoveOpportunity()

  if (isOpportunityRemoving) return <Loading>Mažeme příležitost</Loading>

  const handleClickRemove = async () => {
    const isRemoved = await removeOpportunity({ ...opportunity, userId })
    if (isRemoved) navigate('/org/prilezitosti')
  }

  return (
    <div className={classNames(styles.wrapper, 'opportunitySection')}>
      <header className={styles.name}>{opportunity.name}</header>
      <Actions>
        <ButtonLink primary to={`/org/prilezitosti/${opportunityId}/upravit`}>
          upravit
        </ButtonLink>
        <Button danger onClick={handleClickRemove}>
          smazat
        </Button>
      </Actions>
      <div className={styles.infoBoxDetail}>
        <div className={styles.imageWrapper}>
          <img className={styles.image} src={opportunity.image.medium} alt="" />
          <div className={styles.tags}>
            <div className={styles.tag}>{opportunity.category.name}</div>
          </div>
        </div>
        <table>
          <tbody>
            <tr>
              <th>Datum</th>
              <td>{formatDateRange(opportunity.start, opportunity.end)}</td>
            </tr>
            <tr>
              <th>Místo</th>
              <td>{opportunity.location.name}</td>
            </tr>
            <tr>
              <th>Kontaktní osoba</th>
              <td>
                <div>{opportunity.contact_name}</div>
                <div>{opportunity.contact_phone}</div>
                <div>{opportunity.contact_email}</div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div className={styles.invitationTexts}>
        <header>Představení příležitosti</header>
        <section
          dangerouslySetInnerHTML={{
            __html: sanitize(opportunity.introduction),
          }}
        />
        <header>Popis činnosti</header>
        <section
          dangerouslySetInnerHTML={{
            __html: sanitize(opportunity.description),
          }}
        />
        <header>Přínos pro lokalitu</header>
        <section
          dangerouslySetInnerHTML={{
            __html: sanitize(opportunity.location_benefits ?? ''),
          }}
        />
        <header>Co mi to přinese?</header>
        <section
          dangerouslySetInnerHTML={{
            __html: sanitize(opportunity.personal_benefits),
          }}
        />
        {opportunity.requirements ? (
          <>
            <header>Co potřebuji ke spolupráci</header>
            <section
              dangerouslySetInnerHTML={{
                __html: sanitize(opportunity.requirements),
              }}
            />
          </>
        ) : null}
      </div>
      {/* <pre className={styles.data}>
        {JSON.stringify(opportunity, null, 2)}
      </pre> */}
      <h2>Data</h2>
      <DataView
        data={opportunity}
        translations={combinedTranslations.opportunity}
        genericTranslations={combinedTranslations.generic}
      />
    </div>
  )
}
