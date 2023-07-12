import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import { RootState } from 'app/store'

export type SystemMessage = {
  id: string
  message: string
  type: 'success' | 'info' | 'warning' | 'error'
  time: number
  timeout?: number
  detail?: string
}

type SystemMessageState = {
  messages: {
    byId: { [key: string]: SystemMessage }
  }
}

const slice = createSlice({
  name: 'systemMessage',
  initialState: { messages: { byId: {} } } as SystemMessageState,
  reducers: {
    addMessage: (state, { payload: message }: PayloadAction<SystemMessage>) => {
      state.messages.byId[message.id] = message
    },
    removeMessage: (state, { payload: messageId }: PayloadAction<string>) => {
      delete state.messages.byId[messageId]
    },
  },
})

export const { actions, reducer } = slice

export const selectMessages = (state: RootState) =>
  Object.values(state.systemMessage.messages.byId).sort(
    (a, b) => a.time - b.time,
  )
