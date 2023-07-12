/* eslint-disable @typescript-eslint/no-unused-vars */
// TODO enable the above rule again when we use this feature again
import { skipToken } from '@reduxjs/toolkit/dist/query'
import { api } from 'app/services/bis'
import { hasRequiredQualification } from 'org/utils/validateQualifications'
import { useCurrentUser } from './currentUser'

export const useAllowedToCreateEvent = () => {
  const { data: currentUser, isLoading: isLoadingUser } = useCurrentUser()
  const { data: allQualifications, isLoading } =
    api.endpoints.readQualifications.useQuery(currentUser ? {} : skipToken)

  const canAddNewEvent =
    currentUser &&
    allQualifications &&
    hasRequiredQualification(
      currentUser,
      allQualifications.results.map(q => q.slug),
      allQualifications.results,
    )
  /* The line below is commented out because at the moment,
      we want to allow every organizer to create actions
      To make it work again (stop organizers without qualifications to create events), 
      just uncomment the line
      */
  // return [canAddNewEvent, isLoading || isLoadingUser]
  return [true, false]
}
