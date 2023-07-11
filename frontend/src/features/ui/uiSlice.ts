import { createSelector, createSlice, PayloadAction } from '@reduxjs/toolkit'
import { RootState } from 'app/store'

type UIState = {
  showHeader: boolean
  infoSections: {
    [id: string]: {
      hidden?: boolean
    }
  }
}

const slice = createSlice({
  name: 'ui',
  initialState: { showHeader: true, infoSections: {} } as UIState,
  reducers: {
    showHeader: (state, { payload: show }: PayloadAction<boolean>) => {
      state.showHeader = show
    },
    hideInfoMessage: (state, { payload: id }: PayloadAction<string>) => {
      state.infoSections[id] = { hidden: true }
    },
    toggleInfoMessage: (
      state,
      { payload: { show, id } }: PayloadAction<{ show: boolean; id: string }>,
    ) => {
      state.infoSections[id] = { hidden: !show }
    },
  },
})

export const { actions, reducer } = slice

export const selectShowHeader = (state: RootState) => state.ui.showHeader

export const selectInfoMessageVisibility = createSelector(
  [(state: RootState) => state.ui.infoSections, (state, id: string) => id],
  (sections, id) => !sections[id]?.hidden,
)
