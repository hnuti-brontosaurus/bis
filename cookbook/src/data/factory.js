import { defineStore } from "pinia"
import { computed, ref } from "vue"

// Bumping this key invalidates the persisted cache for every cookbook store
// (handy for shape changes after a deploy).
export const PERSISTED_VERSION = "2"

/**
 * Build a Pinia store keyed by entity id.
 *
 * @param id      store id (e.g. "chefs")
 * @param api     module exposing { list, get?, save? }
 * @param options { persist?: boolean, serialize?: (item) => item }
 */
export const defineByIdStore = (id, api, { persist = true, serialize } = {}) => {
  const persistConfig = persist
    ? {
        persist: {
          key: `cookbook:${id}:v${PERSISTED_VERSION}`,
          ...(serialize
            ? {
                serializer: {
                  serialize: state =>
                    JSON.stringify({
                      byId: Object.fromEntries(
                        Object.entries(state.byId).map(([k, v]) => [k, serialize(v)]),
                      ),
                    }),
                  deserialize: JSON.parse,
                },
              }
            : {}),
        },
      }
    : undefined

  return defineStore(
    id,
    () => {
      const byId = ref({})
      const list = computed(() => Object.values(byId.value))

      const upsertLocal = item => {
        if (item && item.id != null) byId.value[item.id] = item
      }

      const fetchAll = async () => {
        const items = await api.list()
        const next = {}
        for (const item of items) next[item.id] = item
        byId.value = next
      }

      const fetchOne = async itemId => {
        if (!api.get) throw new Error(`${id} store: api.get not provided`)
        const item = await api.get(itemId)
        upsertLocal(item)
        return item
      }

      const save = async payload => {
        if (!api.save) throw new Error(`${id} store: api.save not provided`)
        const saved = await api.save(payload)
        upsertLocal(saved)
        return saved
      }

      const remove = async itemId => {
        if (!api.remove) throw new Error(`${id} store: api.remove not provided`)
        await api.remove(itemId)
        delete byId.value[itemId]
      }

      return { byId, list, fetchAll, fetchOne, save, remove, upsertLocal }
    },
    persistConfig,
  )
}
