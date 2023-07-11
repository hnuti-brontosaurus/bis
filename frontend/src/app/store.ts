import {
  Action,
  combineReducers,
  configureStore,
  createListenerMiddleware,
  isAnyOf,
  Reducer,
  ThunkAction,
} from '@reduxjs/toolkit'
import {
  FLUSH,
  PAUSE,
  PERSIST,
  persistReducer,
  persistStore,
  PURGE,
  REGISTER,
  REHYDRATE,
} from 'redux-persist'
import storage from 'redux-persist/lib/storage'

import { reducer as authReducer } from 'features/auth/authSlice'
import { reducer as formReducer } from 'features/form/formSlice'
import { reducer as systemMessageReducer } from 'features/systemMessage/systemMessageSlice'
import { reducer as uiReducer } from 'features/ui/uiSlice'
import { api } from './services/bis'

const persistConfig = {
  key: 'auth',
  version: 1,
  storage,
}

const listenerMiddleware = createListenerMiddleware()

/**
 * Clear persistent state after (successful or unsuccessful) log out api call
 */
listenerMiddleware.startListening({
  matcher: isAnyOf(
    api.endpoints.logout.matchFulfilled,
    api.endpoints.logout.matchRejected,
  ),
  effect: async () => {
    await resetStore()
  },
})

const persistedAuthReducer = persistReducer(persistConfig, authReducer)
const persistedFormReducer = persistReducer(
  { ...persistConfig, key: 'form' },
  formReducer,
)

const appReducer = combineReducers({
  // [emptySplitApi.reducerPath]: emptySplitApi.reducer,
  [api.reducerPath]: api.reducer,
  auth: persistedAuthReducer,
  ui: uiReducer,
  systemMessage: systemMessageReducer,
  form: persistedFormReducer,
})

// clear redux state after (successful or unsuccessful) log out api call
const rootReducer: Reducer<RootState> = (state, action) => {
  if (
    isAnyOf(
      api.endpoints.logout.matchFulfilled,
      api.endpoints.logout.matchRejected,
    )(action)
  ) {
    return appReducer(undefined, action)
  }

  return appReducer(state, action)
}

export const store = configureStore({
  reducer: rootReducer,
  middleware: getDefaultMiddleware =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    })
      .prepend(listenerMiddleware.middleware)
      .concat(api.middleware),
})

export const persistor = persistStore(store)

export const resetStore = async () => {
  await persistor.purge()
  await persistor.flush()
  await persistor.persist()
}

export type AppDispatch = typeof store.dispatch
export type RootState = ReturnType<typeof appReducer>
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>
