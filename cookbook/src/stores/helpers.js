import { computed } from "vue"

/**
 * Map a store's `list` getter into naive-ui {label, value} options.
 */
export const storeOptions = store =>
  computed(() => store.list.map(item => ({ label: item.name, value: item.id })))

/**
 * Bidirectional id <-> object mapping for naive-ui selects whose v-model is
 * a nested object on the parent.
 */
export const storeIdMapping = (store, ref_) =>
  computed({
    get: () => ref_.value?.id,
    set: value => {
      ref_.value = store.byId[value]
    },
  })
