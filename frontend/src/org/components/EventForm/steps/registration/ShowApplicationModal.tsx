import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import type {
  AdministrationUnit,
  EventApplication,
  MembershipCategory,
  User,
} from 'app/services/bisTypes'
import { DataView } from 'components'
import { StyledModal } from 'components'
import { FC } from 'react'
import { mergeWith, omit } from 'lodash'
import { withOverwriteArray } from 'utils/helpers'
import * as combinedTranslations from 'config/static/combinedTranslations'

interface IShowApplicationModalProps {
  open: boolean
  onClose: () => void
  currentApplication?: EventApplication
  eventName: string
  eventId: number
  userId?: string
  categories: MembershipCategory[]
  administrationUnits: AdministrationUnit[]
  currentParticipant?: User
  participantsMap?: { [s: string]: string[] }
}

// TODO: This modal is still WIP (no need to review atm)
export const ShowApplicationModal: FC<IShowApplicationModalProps> = ({
  open,
  onClose,
  eventName,
  userId,
}) => {
  const { data: user } = api.endpoints.readUser.useQuery(
    userId
      ? {
          id: userId,
        }
      : skipToken,
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
      <DataView
        data={formattedUser}
        translations={combinedTranslations.user}
        genericTranslations={combinedTranslations.generic}
      />
    </StyledModal>
  )
}
