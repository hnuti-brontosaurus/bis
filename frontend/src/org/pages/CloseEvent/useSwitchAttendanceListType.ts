import { useAppDispatch } from 'app/hooks'
import { api } from 'app/services/bis'
import type { AttendanceListTypeEnum } from 'app/services/bisTypes'
import { useShowApiErrorMessage } from 'features/systemMessage/useSystemMessage'

/**
 * Switches how participants are recorded for an event.
 *
 * The participant list and both counts are wiped in the same PATCH: a
 * simple-list participant may be anyone, so their full profile must not
 * become visible just by flipping the event to full-list, and a count
 * entered in one mode is meaningless in another. Mirroring the wipe into
 * the form is left to the caller, which owns the form state.
 *
 * Resolves to true when the switch went through.
 */
export const useSwitchAttendanceListType = (eventId: number) => {
  const [updateEvent, { isLoading, error }] =
    api.endpoints.updateEvent.useMutation()
  useShowApiErrorMessage(error, 'Nepodařilo se změnit způsob zadání účastníků')
  const dispatch = useAppDispatch()

  const switchAttendanceListType = async (type: AttendanceListTypeEnum) => {
    try {
      await updateEvent({
        id: eventId,
        event: {
          record: {
            participants: [],
            attendance_list_type: type,
            number_of_participants: null,
            number_of_participants_under_26: null,
          },
        },
      }).unwrap()
    } catch {
      return false
    }
    // Clear the cached participants synchronously so the about-to-mount
    // full-list view doesn't briefly render against the simple-list
    // projection while the invalidation-triggered refetch is in flight.
    dispatch(
      api.util.updateQueryData('readEventParticipants', { eventId }, draft => {
        draft.count = 0
        draft.next = null
        draft.previous = null
        draft.results = []
      }),
    )
    return true
  }

  return [switchAttendanceListType, isLoading] as const
}
