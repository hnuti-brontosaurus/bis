<script setup>
import { NDataTable, useThemeVars } from "naive-ui"
import { computed, useSlots } from "vue"
import { isEmptyVNode } from "@/contrib/composables/helpers.js"

const props = defineProps({
  data: {},
  columns: {},
  expandable: { default: true },
})

const slots = useSlots()
const hasNoContent = item => {
  try {
    return slots.default?.(item).every(isEmptyVNode)
  } catch (e) {
    return true
  }
}

const tableColumns = computed(() => {
  const expandable = props.columns.some(_ => _.expandable)

  if (!expandable) return props.columns

  return [
    {
      type: "expand",
      expandable: row => row.expandable,
      renderExpand: row => row.renderExpand,
    },
    ...props.columns,
  ]
})
</script>

<template></template>

<style scoped></style>
