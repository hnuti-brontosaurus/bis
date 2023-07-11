import { createSlice, isAnyOf, PayloadAction } from '@reduxjs/toolkit'
import { api } from 'app/services/bis'
import { RootState } from 'app/store'
import type { AccessSlug } from 'utils/roles'

type AuthState = {
  access: AccessSlug | null
  token: string | null
  isLoggingOut: boolean
}

const slice = createSlice({
  name: 'auth',
  initialState: { access: null, token: null, isLoggingOut: false } as AuthState,
  reducers: {
    setAccess: (state, { payload }: PayloadAction<AccessSlug>) => {
      state.access = payload
    },
    setInitialAccess: (state, { payload }: PayloadAction<AccessSlug>) => {
      if (!state.access) state.access = payload
    },
  },
  extraReducers: builder => {
    builder
      .addMatcher(
        isAnyOf(
          api.endpoints.login.matchFulfilled,
          api.endpoints.resetPassword.matchFulfilled,
        ),
        (state, { payload }) => {
          state.token = payload.token
        },
      )
      .addMatcher(api.endpoints.logout.matchPending, state => {
        state.isLoggingOut = true
      })
      .addMatcher(
        isAnyOf(
          api.endpoints.logout.matchFulfilled,
          api.endpoints.logout.matchRejected,
        ),
        state => {
          state.isLoggingOut = false
        },
      )
  },
})

export const { actions, reducer } = slice

export const selectAuthenticated = (state: RootState) =>
  Boolean(state.auth.token)

export const selectAuthToken = (state: RootState) => state.auth.token

export const selectLoggingOut = (state: RootState) => state.auth.isLoggingOut

export const selectCurrentAccess = (state: RootState) => state.auth.access
