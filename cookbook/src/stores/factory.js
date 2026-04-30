import { defineStore } from "pinia"
import { computed, ref } from "vue"
import { PERSISTED_VERSION } from "./index.js"

/**
 * Build a Pinia store keyed by entity id.
 *
 * @param id      store id (e.g. "chefs")
 * @param api     module exposing { list, get?, save? }
 * @param options { persist?: boolean }
 */
export const defineByIdStore = (id, api, { persist = true } = {}) =>
  defineStore(
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

      return { byId, list, fetchAll, fetchOne, save, upsertLocal }
    },
    persist
      ? {
          persist: { key: `cookbook:${id}:v${PERSISTED_VERSION}` },
        }
      : undefined,
  )
