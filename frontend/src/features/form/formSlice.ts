import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { UserPayload } from 'app/services/bisTypes'
import { RootState } from 'app/store'
import mergeWith from 'lodash/mergeWith'
import type { EventFormShape } from 'org/components/EventForm'
import { OpportunityFormShape } from 'org/components/OpportunityForm/OpportunityForm'
import { CloseEventFormShape } from 'org/pages/CloseEvent/CloseEventForm'
import { RegistrationFormShapeWithStep } from 'pages/EventRegistration/EventRegistrationForm'
import { DeepPartial, ValuesType } from 'utility-types'
import { withOverwriteArray } from 'utils/helpers'

export type FormState<K extends string = string> = {
  event: Record<K, EventFormShape>
  closeEvent: Record<K, CloseEventFormShape>
  opportunity: Record<K, OpportunityFormShape>
  registration: Record<K, RegistrationFormShapeWithStep>
  user: Record<K, UserPayload>
}

export type PersistentFormType =
  | 'event'
  | 'closeEvent'
  | 'opportunity'
  | 'registration'
  | 'user'

export type PersistentFormValue<K extends PersistentFormType> = ValuesType<
  FormState[K]
>

type SaveEventPayload<
  K extends string = string,
  T extends keyof FormState<K> = keyof FormState<K>,
> = {
  id: K
  type: T
  data: DeepPartial<FormState<K>[T][K]>
}

type RemoveEventPayload = Pick<SaveEventPayload, 'id' | 'type'>

const slice = createSlice({
  name: 'form',
  initialState: {
    event: {},
    closeEvent: {},
    opportunity: {},
    registration: {},
    user: {},
  } as FormState<string>,
  reducers: {
    saveForm: (state, { payload }: PayloadAction<SaveEventPayload>) => {
      state[payload.type][payload.id] = mergeWith(
        {},
        state[payload.type][payload.id],
        payload.data,
        withOverwriteArray,
      )
    },
    removeForm: (state, { payload }: PayloadAction<RemoveEventPayload>) => {
      delete state[payload.type][payload.id]
    },
  },
})

export const { actions, reducer } = slice

export const selectFormByTypeAndId = createSelector(
  [
    (state: RootState) => state.form,
    (state, type: keyof FormState) => type,
    (state, type, id: string) => id,
  ],
  (form, type, id) => form[type][id],
)
