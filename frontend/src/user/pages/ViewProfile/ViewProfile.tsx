import { api } from 'app/services/bis'
import { Fragment } from 'react'
import { User } from 'app/services/bisTypes'
import {
  Actions,
  Breadcrumbs,
  ButtonLink,
  DataView,
  ExternalButtonLink,
  InfoBox,
  PageHeader,
} from 'components'
import * as combinedTranslations from 'config/static/combinedTranslations'
import { useCurrentUser } from 'hooks/currentUser'
import { useTitle } from 'hooks/title'
import { mergeWith, omit } from 'lodash'
import { FaPencilAlt } from 'react-icons/fa'
import { useOutletContext } from 'react-router-dom'
import { withOverwriteArray, formatDateTime } from 'utils/helpers'
import styles from './ViewProfile.module.scss'

export const ViewProfile = () => {
  const { user } = useOutletContext<{ user: User }>()
  const { data: currentUser } = useCurrentUser()

  const { data: administrationUnits } =
    api.endpoints.readAdministrationUnits.useQuery({ pageSize: 2000 })

  const isSelf = currentUser?.id === user.id

  const title = isSelf ? 'Můj profil' : `Profil uživatele ${user.display_name}`

  useTitle(title)

  const formattedMemberships = user.memberships.map(
    ({ administration_unit, ...rest }) => ({
      administration_unit:
        administrationUnits?.results.find(au => au.id === administration_unit)
          ?.name ?? administration_unit,
      ...rest,
    }),
  )
  const formattedUser = mergeWith(
    omit(user, 'id', '_search_id', 'display_name'),
    { memberships: formattedMemberships },
    withOverwriteArray,
  )

  const ALL_COLUMNS = 8

  const compareEmails = (
    email: string | null | undefined,
    allEmails: string[],
  ) => {
    if (!email || !allEmails) return false
    const filteredEmails = allEmails.filter(e => e && e === email)
    return filteredEmails.length >= 1
  }

  return (
    <>
      <Breadcrumbs userName={user.display_name} />
      <div className={styles.pageContainer}>
        <PageHeader>{title}</PageHeader>
        <Actions>
          <ButtonLink primary to="upravit">
            <FaPencilAlt /> Upravit
          </ButtonLink>
          {user.id === currentUser?.id && (
            <ExternalButtonLink
              secondary
              target="_blank"
              rel="noopener noreferrer"
              href="https://forms.gle/gPUL3CgSeAHtNVuu8"
            >
              Zažádat o EYCA/HB kartu
            </ExternalButtonLink>
          )}
        </Actions>
        {user.photo ? (
          <img
            className={styles.profilePicture}
            src={user.photo.small}
            alt="fotka uživatele"
          />
        ) : (
          ''
        )}
        <section>
          <table className={styles.horizontalTable}>
            <tbody>
              <tr>
                <td colSpan={ALL_COLUMNS} className={styles.oneCellRow}>
                  Osobní údaje
                </td>
              </tr>
              <tr>
                <th>Jméno</th>
                <td>{user.first_name}</td>
              </tr>
              <tr>
                <th>Příjmení</th>
                <td>{user.last_name}</td>
              </tr>
              <tr>
                <th>Přezdívka</th>
                <td>{user.nickname ? user.nickname : '-'}</td>
              </tr>
              <tr>
                <th>Oslovení</th>
                <td>
                  {user.pronoun?.name.length > 0 ? user.pronoun?.name : '-'}
                </td>
              </tr>
              <tr>
                <th>Rodné příjmení</th>
                <td>{user.birth_name ? user.birth_name : '-'}</td>
              </tr>
              <tr>
                <th>Datum narození</th>
                <td>{user.birthday ? formatDateTime(user.birthday) : null}</td>
              </tr>

              <tr>
                <th>Zdravotní pojišťovna</th>
                <td>{user.health_insurance_company?.name ?? '-'}</td>
              </tr>
              <tr>
                <th>Alergie a zdravotní omezení</th>
                <td>{user.health_issues ? user.health_issues : '-'}</td>
              </tr>
              <tr>
                <td colSpan={ALL_COLUMNS} className={styles.oneCellRow}>
                  Kontaktní údaje
                </td>
              </tr>
              <tr>
                <th>E-mail</th>
                <td>{user.email}</td>
              </tr>
              {compareEmails(user.email, user.all_emails) ? (
                ''
              ) : (
                <tr>
                  <th>Všechny e-maily</th>
                  <td>{user.all_emails}</td>
                </tr>
              )}
              <tr>
                <th>Telefon</th>
                <td>{user.phone ? user.phone : '-'}</td>
              </tr>
              <tr>
                <th>Odebírá novinky?</th>
                <td>{user.subscribed_to_newsletter ? 'ano' : 'ne'}</td>
              </tr>
              <tr>
                <td colSpan={ALL_COLUMNS} className={styles.oneCellRowSmall}>
                  Adresa
                </td>
              </tr>
              <tr>
                <th>Ulice a číslo domu</th>
                <td>{user.address?.street ?? '-'}</td>
              </tr>
              <tr>
                <th>Obec</th>
                <td>{user.address?.city ?? '-'}</td>
              </tr>
              <tr>
                <th>Směrovací číslo</th>
                <td>{user.address?.zip_code ?? '-'}</td>
              </tr>
              {user.contact_address?.city ? (
                <>
                  <tr>
                    <td
                      colSpan={ALL_COLUMNS}
                      className={styles.oneCellRowSmall}
                    >
                      Kontaktní adresa
                    </td>
                  </tr>
                  <tr>
                    <th>Ulice a číslo domu</th>
                    <td>{user.contact_address?.street}</td>
                  </tr>
                  <tr>
                    <th>Obec</th>
                    <td>{user.contact_address?.city}</td>
                  </tr>
                  <tr>
                    <th>Směrovací číslo</th>
                    <td>{user.contact_address?.zip_code}</td>
                  </tr>
                </>
              ) : (
                ''
              )}
              {user.close_person?.first_name ? (
                <>
                  <tr>
                    <td
                      colSpan={ALL_COLUMNS}
                      className={styles.oneCellRowSmall}
                    >
                      Rodič / blízká osoba:
                    </td>
                  </tr>
                  <tr>
                    <th>Jméno</th>
                    <td>{user.close_person?.first_name}</td>
                  </tr>
                  <tr>
                    <th>Příjmení</th>
                    <td>{user.close_person?.last_name}</td>
                  </tr>
                  <tr>
                    <th>E-mail</th>
                    <td>{user.close_person?.email ?? '-'}</td>
                  </tr>
                  <tr>
                    <th>Telefon</th>
                    <td>{user.close_person?.phone ?? '-'}</td>
                  </tr>
                </>
              ) : (
                ''
              )}
              <tr>
                <td colSpan={ALL_COLUMNS} className={styles.oneCellRow}>
                  Organizační informace
                </td>
              </tr>
              <tr>
                <th>Role</th>
                <td>{user.roles?.map(role => role.name).join(', ')}</td>
              </tr>
              <tr>
                <th>Kvalifikace</th>
                <td>
                  {user.qualifications.length > 0
                    ? user.qualifications?.map(qualif => (
                        <div
                          className={styles.tableDiv}
                          key={qualif.category?.id}
                        >
                          <span className={styles.bold}>
                            {qualif.category?.name}
                            <br />
                          </span>
                          Datum získání: {formatDateTime(qualif.valid_since)}
                          <br />
                          Kvalifikaci udělil: {
                            qualif.approved_by?.first_name
                          }{' '}
                          {qualif.approved_by?.last_name}
                          <br />
                          Platnost kvalifikace do:{' '}
                          {formatDateTime(qualif.valid_till)}
                        </div>
                      ))
                    : '-'}
                </td>
              </tr>
              <tr>
                <th>Členství</th>
                <td>
                  {formattedMemberships.length > 0
                    ? formattedMemberships.map(memb => (
                        <Fragment key={memb.category?.id}>
                          <span className={styles.bold}>
                            Organizační jednotka:{' '}
                          </span>
                          {memb.administration_unit}
                          <br />
                          <span className={styles.bold}>Typ členství: </span>
                          {memb.category?.name}
                          <br />
                          <span className={styles.bold}>Členství v roce: </span>
                          {memb.year}
                        </Fragment>
                      ))
                    : '-'}
                </td>
              </tr>
              <tr>
                <th>EYCA nebo členská karta</th>
                <td>
                  {user.eyca_card ? (
                    'ano, platnost do: ' +
                    formatDateTime(user.eyca_card?.valid_till)
                  ) : (
                    <>
                      ne <br />
                      <ExternalButtonLink
                        tertiary
                        small
                        target="_blank"
                        href="https://www.eyca.cz/"
                      >
                        výhody EYCA evropské karty mládeže
                      </ExternalButtonLink>
                    </>
                  )}
                </td>
              </tr>
              <tr>
                <th>Datum vzniku tvého profilu v BIS</th>
                <td>{formatDateTime(user.date_joined)}</td>
              </tr>
            </tbody>
          </table>
          <div className={styles.buttonGroup}>
            <ButtonLink primary to="/user/akce/zucastnene">
              Akce, kterých jsem se zúčastnil/a
            </ButtonLink>
            <ButtonLink primary to="/org/akce/vsechny">
              Akce, které jsem organizoval/a
            </ButtonLink>
          </div>
          <InfoBox>
            <p>
              Jako organizátor Hnutí Brontosaurus můžeš pro pořádání akcí
              využívat podporu a zázemí HB. Zde najdeš užitečné informace a
              pořádání akcí, které jsou dostupné pouze pod heslem
            </p>
            <ul>
              <li>
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://mozek.brontosaurus.cz/"
                  className={styles.help}
                >
                  Mozek HB
                </a>
                , kde jsou všechny důležité dokumenty. Přihlašovací jméno:
                brontosaurus, heslo: Brontosaurus40
              </li>
              <li>
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://www.canva.com/ "
                >
                  Canva
                </a>
                , kde můžeš využívat předplacenou Canvu Pro pro vytváření
                plakátů a dalších propagačních materiálů. Přihlašovací email:
                marketing@brontosaurus.cz, heslo: jedemedal24
              </li>
              <li>
                Připravenou{' '}
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://zpetna-vazba.brontosaurus.cz/login.php"
                  className={styles.help}
                >
                  Zpětnou vazbu pro
                </a>{' '}
                vaše účastníky, vytvořenou speciálně pro akce HB. Přihlásíš se
                univerzálním heslem “vyplnto” nebo heslem vaší organizační
                jednotky.
              </li>
              <li>
                Vyplň{' '}
                <a
                  target="_blank"
                  rel="noopener noreferrer"
                  href="https://zpetna-vazba.brontosaurus.cz/login.php"
                  className={styles.help}
                >
                  Závěrečnou zprávu
                </a>{' '}
                pro neustále zlepšování vašich akcí. Přihlásíš se univerzálním
                heslem “vyplnto” nebo heslem vaší organizační jednotky.
              </li>
            </ul>
          </InfoBox>
        </section>

        {/* <pre className={styles.data}>{JSON.stringify(user, null, 2)}</pre> */}
        {/* <DataView
          data={formattedUser}
          translations={combinedTranslations.user}
          genericTranslations={combinedTranslations.generic}
        /> */}
      </div>
    </>
  )
}
