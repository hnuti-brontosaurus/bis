import { computed } from "vue"

/**
 * Map a store's `list` getter into naive-ui {label, value} options.
 */
export const storeOptions = store =>
  computed(() => store.list.map(item => ({ label: item.name, value: item.id })))
