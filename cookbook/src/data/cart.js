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

const normalizeOtherItem = item => ({
  id: item.id ?? newId(),
  name: item.name ?? "",
  count: item.count ?? 1,
  bought: !!item.bought,
})

const sanitize = items => (Array.isArray(items) ? items.map(normalizeGroup) : [])

const sanitizeOther = otherItems =>
  Array.isArray(otherItems) ? otherItems.map(normalizeOtherItem) : []

const groupIsAllBought = group =>
  group.ingredients.length > 0 && group.ingredients.every(entry => entry.bought)

export const cartApi = {
  fetch: () => client.get("/cart/").then(r => r.data),
  update: (items, other_items) =>
    client.patch("/cart/", { items, other_items }).then(r => r.data),
}

export const useCartStore = defineStore(
  "cart",
  () => {
    const items = ref([])
    const otherItems = ref([])
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
          await cartApi.update(items.value, otherItems.value)
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

    const addOtherItem = (name, count) => {
      otherItems.value = [...otherItems.value, normalizeOtherItem({ name, count })]
    }

    const removeOtherItem = itemId => {
      otherItems.value = otherItems.value.filter(item => item.id !== itemId)
    }

    const addCustomGroup = name => {
      const group = normalizeGroup({ recipe_id: null, recipe_name: name })
      items.value = [...items.value, group]
      schedulePush()
      return group.id
    }

    const apply = state => {
      items.value = state.items
      otherItems.value = state.other_items
    }

    const resolveConflict = strategy => {
      if (!conflict.value) return
      const { local, server } = conflict.value
      if (strategy === "keep_server") apply(server)
      else if (strategy === "use_local") apply(local)
      else if (strategy === "merge")
        apply({
          items: [...server.items, ...local.items],
          other_items: [...server.other_items, ...local.other_items],
        })
      conflict.value = null
      schedulePush()
    }

    const reconcile = async () => {
      let serverCart
      try {
        serverCart = await cartApi.fetch()
      } catch (e) {
        handleAxiosError("Failed to fetch cart")(e)
        return
      }
      // Drop everything already bought from both sides — it's stale shopping
      // history, not data the user wants to reconcile.
      const unbought = (groups, others) => ({
        items: groups.filter(group => !groupIsAllBought(group)),
        other_items: others.filter(item => !item.bought),
      })
      const server = unbought(
        sanitize(serverCart.items),
        sanitizeOther(serverCart.other_items),
      )
      const local = unbought(items.value, otherItems.value)
      const hasContent = state => state.items.length || state.other_items.length
      // After a successful sync the two sides are byte-identical (we just
      // wrote them). Without this check, every refresh would re-fire the
      // conflict modal.
      const sameAsServer = JSON.stringify(local) === JSON.stringify(server)
      suppressWatchPush = true
      try {
        if (sameAsServer) {
          apply(server)
          return
        }
        if (hasContent(server) && hasContent(local)) {
          conflict.value = { local, server }
          return
        }
        apply(hasContent(server) ? server : local)
      } finally {
        suppressWatchPush = false
      }
      if (!sameAsServer) schedulePush()
    }

    // Deep watch lets child components mutate cart entries in place
    // (e.g. IngredientInput rewriting amount / unit_id) and still trigger
    // a debounced sync without each callsite having to call schedulePush.
    watch(
      [items, otherItems],
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
      otherItems,
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
      addOtherItem,
      removeOtherItem,
      resolveConflict,
    }
  },
  { persist: { key: "cookbook:cart:v1", pick: ["items", "otherItems"] } },
)
