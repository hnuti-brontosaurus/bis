import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import type {
  AdministrationUnit,
  EventApplication,
  MembershipCategory,
  User,
} from 'app/services/bisTypes'
import { EmailButton, PhoneButton, StyledModal, DataView } from 'components'
import styles from '../ParticipantsStep.module.scss'
import { FC, Fragment } from 'react'
import { mergeWith, omit } from 'lodash'
import { withOverwriteArray } from 'utils/helpers'
import * as combinedTranslations from 'config/static/combinedTranslations'

interface IShowApplicationModalProps {
  open: boolean
  onClose: () => void
  currentApplication?: EventApplication
  eventName: string
  eventId: number
  userId?: string | null
  categories: MembershipCategory[]
  administrationUnits: AdministrationUnit[]
  currentParticipant?: User
  participantsMap?: { [s: string]: string[] }
}

// TODO: This modal is still WIP (no need to review atm)
export const ShowApplicationModal: FC<IShowApplicationModalProps> = ({
  open,
  onClose,
  currentApplication: currentApplicationProp,
  eventName,
  eventId,
  // setCurrentApplicationId,
  // setShowAddParticipantModal,
  // deleteEventApplication,
  userId,
  categories,
  administrationUnits,
  currentParticipant,
  participantsMap,
}) => {
  const { data: currentApplicationData } =
    api.endpoints.readEventApplication.useQuery(
      currentParticipant &&
        participantsMap &&
        participantsMap[currentParticipant.id]?.length > 0
        ? {
            eventId,
            //TODO: add here showing an array of applications
            applicationId: Number(participantsMap[currentParticipant.id][0]),
          }
        : skipToken,
    )

  const currentApplication = currentApplicationProp || currentApplicationData

  const { data: user } = api.endpoints.readUser.useQuery(
    userId
      ? {
          id: userId,
        }
      : skipToken,
  )
  // we'll also show last year membership till end of February
  // we want to give people time to register for the new year
  // and still show continuity of membership
  const currentYear = new Date().getFullYear()
  const currentMonth = new Date().getMonth()
  const currentMemberships = (user?.memberships ?? []).filter(
    membership =>
      membership.year === currentYear ||
      (currentMonth < 2 && membership.year === currentYear - 1),
  )
  // TODO consider showing historical memberships, too

  const formattedUser = mergeWith(
    omit(user, 'id', '_search_id', 'display_name'),
    { memberships: user?.memberships },
    withOverwriteArray,
  )

  if (!open) return null

  return (
    <StyledModal
      open={open}
      onClose={onClose}
      title={`Přihláška na akci ${eventName}`}
    >
      {currentApplication &&
        (!participantsMap ||
          !user ||
          (user && currentApplication.id.toString() === user.id)) && (
          <div>
            {' '}
            <h3>Přihláška:</h3>
            <div className={styles.showUserApplicationNameBox}>
              <h4>
                {currentApplication.first_name} {currentApplication.last_name}{' '}
                {currentApplication.nickname &&
                  `(${currentApplication.nickname})`}{' '}
              </h4>
            </div>
            {currentApplication.birthday && (
              <div>
                <span>Datum narození: </span>
                <span>{currentApplication.birthday}</span>
              </div>
            )}
            {currentApplication.pronoun?.name && (
              <div>
                <span>Oslovení: </span>
                <span>{currentApplication.pronoun.name}</span>
              </div>
            )}
            {currentApplication.email && (
              <div>
                <span>E-mail: </span>
                <span>
                  <EmailButton>{currentApplication.email}</EmailButton>
                </span>
              </div>
            )}
            {currentApplication.phone && (
              <div>
                <span>Telefon: </span>
                <span>
                  <PhoneButton>{currentApplication.phone}</PhoneButton>
                </span>
              </div>
            )}
            {currentApplication.health_issues && (
              <div>
                <span>Zdravotní omezení: </span>
                <span>{currentApplication.health_issues}</span>
              </div>
            )}
            {currentApplication.close_person && (
              <div>
                <span>Blízká osoba: </span>
                <span>{`${currentApplication.close_person.first_name} ${currentApplication.close_person.last_name}`}</span>
                {currentApplication.close_person.email && (
                  <>
                    <span>email:</span>
                    <EmailButton>
                      {currentApplication.close_person.email}
                    </EmailButton>
                  </>
                )}
                {currentApplication.close_person.phone && (
                  <>
                    <span>tel: </span>
                    <PhoneButton>
                      {currentApplication.close_person.phone}
                    </PhoneButton>
                  </>
                )}
              </div>
            )}
            {currentApplication.answers &&
              currentApplication.answers.map(answer => (
                <div key={answer.question.id} className={styles.QAContainer}>
                  <div>
                    <h5>{answer.question.question}</h5>
                  </div>
                  <div>{answer.answer}</div>
                </div>
              ))}
            <div>
              <div>
                <h5>Poznámka</h5>
              </div>
              <div>{currentApplication.note}</div>
            </div>
          </div>
        )}
      {userId && user && (
        <div>
          <div className={styles.addedUserBlock}>
            <h3>Uživatel přidaný na akci: </h3>
            <h4>
              {user.first_name} {user.last_name}{' '}
              {user.nickname && `(${user.nickname})`}{' '}
            </h4>
          </div>

          {user.birthday && (
            <div>
              <span>Datum narození: </span>
              <span>{user.birthday}</span>
            </div>
          )}
          {user.pronoun?.name && (
            <div>
              <span>Oslovení: </span>
              <span>{user.pronoun.name}</span>
            </div>
          )}

          {user.email && (
            <div>
              <span>E-mail: </span>
              <span>
                <EmailButton>{user.email}</EmailButton>
              </span>
            </div>
          )}
          {user.phone && (
            <div>
              <span>Telefon: </span>
              <span>
                <PhoneButton>{user.phone}</PhoneButton>
              </span>
            </div>
          )}
          {user.health_issues && (
            <div>
              <span>Zdravotní omezení: </span>
              <span>{user.health_issues}</span>
            </div>
          )}
          {user.close_person && (
            <div>
              <span>Blízká osoba: </span>
              <span>{`${user.close_person.first_name} ${user.close_person.last_name}`}</span>
              {user.close_person.email && (
                <span>
                  'email: ' <EmailButton>{user.close_person.email}</EmailButton>
                </span>
              )}
              {user.close_person.phone && (
                <span>
                  'tel: ' <PhoneButton>{user.close_person.phone}</PhoneButton>
                </span>
              )}
            </div>
          )}
          {currentMemberships && currentMemberships.length !== 0 && (
            <div>
              <span>Členství: </span>
              <div>
                {currentMemberships.map(membership => {
                  return (
                    <Fragment
                      key={`${membership.year}-${membership.administration_unit}-${membership.category}`}
                    >
                      {administrationUnits && categories && (
                        <div>
                          {
                            administrationUnits.find(
                              unit =>
                                membership.administration_unit === unit.id,
                            )?.name
                          }
                          {' - '}
                          {
                            categories.find(
                              category =>
                                membership.category.id === category.id,
                            )?.name
                          }{' '}
                          ({membership.year})
                        </div>
                      )}
                    </Fragment>
                  )
                })}
              </div>
            </div>
          )}
        </div>
      )}
      {userId &&
        user &&
        currentApplication &&
        currentApplication.email === formattedUser.email && (
          <div>
            <h3>Detaily uživatele:</h3>
            <DataView
              data={formattedUser}
              translations={combinedTranslations.user}
              genericTranslations={combinedTranslations.generic}
            />
          </div>
        )}
    </StyledModal>
  )
}
