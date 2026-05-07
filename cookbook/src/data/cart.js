import { defineStore } from "pinia"
import { computed, ref, watch } from "vue"
import { client } from "./client.js"
import { useAuthStore } from "./auth.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"

const STALE_MS = 12 * 60 * 60 * 1000
const SYNC_DEBOUNCE_MS = 400

const newId = () =>
  globalThis.crypto?.randomUUID?.() ??
  `g_${Date.now()}_${Math.random().toString(36).slice(2)}`

const normalizeIngredient = entry => ({
  ingredient_id: entry.ingredient_id,
  unit_id: entry.unit_id,
  amount: entry.amount,
  bought: !!entry.bought,
})

const normalizeGroup = group => ({
  id: group.id ?? newId(),
  recipe_id: group.recipe_id ?? null,
  recipe_name: group.recipe_name ?? "",
  added_at: group.added_at ?? new Date().toISOString(),
  ingredients: (group.ingredients ?? []).map(normalizeIngredient),
})

const sanitize = items => (Array.isArray(items) ? items.map(normalizeGroup) : [])

const groupIsAllBought = group =>
  group.ingredients.length > 0 && group.ingredients.every(entry => entry.bought)

export const cartApi = {
  fetch: () => client.get("/cart/").then(r => r.data),
  update: items => client.patch("/cart/", { items }).then(r => r.data),
}

export const useCartStore = defineStore(
  "cart",
  () => {
    const items = ref([])
    const conflict = ref(null)

    let reconciled = false
    let pushTimer = null
    // Suppress the deep-watch sync while the store is bulk-loading items
    // (reconcile, conflict resolve, persist hydrate) — those paths push
    // explicitly and we don't want a second redundant push from the watch.
    let suppressWatchPush = false

    // Groups that still have at least one unbought ingredient. Used for the
    // "is the cart actually in use" question — a fully-bought cart counts
    // as effectively empty for conflict detection and the staleness prompt.
    const meaningful = computed(() =>
      items.value.filter(group => !groupIsAllBought(group)),
    )

    const isStale = computed(() => {
      const list = meaningful.value
      if (!list.length) return false
      const newest = Math.max(...list.map(group => Date.parse(group.added_at) || 0))
      return Date.now() - newest > STALE_MS
    })

    const schedulePush = () => {
      if (!useAuthStore().isAuthenticated) return
      clearTimeout(pushTimer)
      pushTimer = setTimeout(async () => {
        try {
          await cartApi.update(items.value)
        } catch (e) {
          handleAxiosError("Failed to sync cart")(e)
        }
      }, SYNC_DEBOUNCE_MS)
    }

    const addGroup = group => {
      items.value = [...items.value, normalizeGroup(group)]
      schedulePush()
    }

    const replaceWith = group => {
      items.value = [normalizeGroup(group)]
      schedulePush()
    }

    const setItems = next => {
      items.value = sanitize(next)
      schedulePush()
    }

    const clear = () => {
      items.value = []
      schedulePush()
    }

    const removeGroup = groupId => {
      items.value = items.value.filter(group => group.id !== groupId)
      schedulePush()
    }

    const updateGroup = (groupId, patch) => {
      items.value = items.value.map(group =>
        group.id === groupId ? normalizeGroup({ ...group, ...patch }) : group,
      )
      schedulePush()
    }

    const setIngredientBought = (groupId, ingredientIndex, bought) => {
      items.value = items.value.map(group => {
        if (group.id !== groupId) return group
        const next = group.ingredients.map((entry, index) =>
          index === ingredientIndex ? { ...entry, bought } : entry,
        )
        return { ...group, ingredients: next }
      })
      schedulePush()
    }

    const setIngredientBoughtAcross = (ingredientId, bought) => {
      items.value = items.value.map(group => ({
        ...group,
        ingredients: group.ingredients.map(entry =>
          entry.ingredient_id === ingredientId ? { ...entry, bought } : entry,
        ),
      }))
      schedulePush()
    }

    const addCustomGroup = name => {
      const group = normalizeGroup({ recipe_id: null, recipe_name: name })
      items.value = [...items.value, group]
      schedulePush()
      return group.id
    }

    const resolveConflict = strategy => {
      if (!conflict.value) return
      const { local, server } = conflict.value
      if (strategy === "keep_server") items.value = sanitize(server)
      else if (strategy === "use_local") items.value = sanitize(local)
      else if (strategy === "merge")
        items.value = [...sanitize(server), ...sanitize(local)]
      conflict.value = null
      schedulePush()
    }

    const reconcile = async () => {
      let serverItems
      try {
        serverItems = (await cartApi.fetch()).items ?? []
      } catch (e) {
        handleAxiosError("Failed to fetch cart")(e)
        return
      }
      // Drop fully-bought groups from both sides — they're stale shopping
      // history, not data the user wants to reconcile.
      const server = sanitize(serverItems).filter(group => !groupIsAllBought(group))
      const local = items.value.filter(group => !groupIsAllBought(group))
      // After a successful sync the two sides are byte-identical (we just
      // wrote them). Without this check, every refresh would re-fire the
      // conflict modal.
      const sameAsServer = JSON.stringify(local) === JSON.stringify(server)
      suppressWatchPush = true
      try {
        if (sameAsServer) {
          items.value = server
          return
        }
        if (server.length && local.length) {
          conflict.value = { local, server }
          return
        }
        items.value = server.length ? server : local
      } finally {
        suppressWatchPush = false
      }
      if (!sameAsServer) schedulePush()
    }

    // Deep watch lets child components mutate cart entries in place
    // (e.g. IngredientInput rewriting amount / unit_id) and still trigger
    // a debounced sync without each callsite having to call schedulePush.
    watch(
      items,
      () => {
        if (!suppressWatchPush) schedulePush()
      },
      { deep: true },
    )

    watch(
      () => useAuthStore().isAuthenticated,
      isAuthed => {
        if (isAuthed && !reconciled) {
          reconciled = true
          reconcile()
        } else if (!isAuthed) {
          reconciled = false
          conflict.value = null
        }
      },
      { immediate: true },
    )

    return {
      items,
      conflict,
      meaningful,
      isStale,
      addGroup,
      replaceWith,
      setItems,
      clear,
      removeGroup,
      updateGroup,
      setIngredientBought,
      setIngredientBoughtAcross,
      addCustomGroup,
      resolveConflict,
    }
  },
  { persist: { key: "cookbook:cart:v1", pick: ["items"] } },
)
