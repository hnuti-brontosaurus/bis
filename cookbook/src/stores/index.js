import { createPinia } from "pinia"
import piniaPluginPersistedstate from "pinia-plugin-persistedstate"

// Bumping this key invalidates the persisted cache for all cookbook stores
// (handy for shape changes after a deploy).
export const PERSISTED_VERSION = "1"

export const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)
