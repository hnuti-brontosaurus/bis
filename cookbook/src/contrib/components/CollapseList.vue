<script setup>
import { NCollapse, NCollapseItem, NCheckbox } from "naive-ui"
import { useSlots } from "vue"
import { isEmptyVNode } from "@/contrib/composables/helpers.js"

const props = defineProps({
  data: {},
  columns: {},
  getKey: { default: () => item => item.id },
  checkedKey: {},
})

const slots = useSlots()

// The row opens the item and the whole checkbox area ticks it; a row with
// nothing to open ticks instead.
const onItemClick = (event, item, i) => {
  if (!props.checkedKey || !event.target.closest(".n-collapse-item__header")) return
  if (event.target.closest(".n-checkbox")) return
  if (
    event.target.closest(".n-collapse-item__header-extra") ||
    hasNoContent({ item, i })
  )
    item[props.checkedKey] = !item[props.checkedKey]
}
const hasNoContent = item => {
  try {
    return slots.default?.(item).every(isEmptyVNode)
  } catch {
    return true
  }
}
</script>

<template>
  <n-collapse
    display-directive="show"
    :trigger-areas="checkedKey ? ['main', 'arrow'] : ['main', 'extra', 'arrow']"
    :class="{ checkable: checkedKey }"
  >
    <n-collapse-item
      v-for="(item, i) in data"
      :key="getKey(item)"
      :name="getKey(item)"
      @click="onItemClick($event, item, i)"
    >
      <template #header>
        <slot name="header" :item="item" :i="i">
          {{ item.name }}
        </slot>
      </template>
      <slot name="default" :item="item" :i="i">
        <div :style="`margin-top: -16px`"></div>
      </slot>
      <template #arrow v-if="hasNoContent({ item, i })">
        <i class="n-base-icon"></i>
      </template>
      <template #header-extra v-if="checkedKey">
        <n-checkbox @click.stop v-model:checked="item[checkedKey]" />
      </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style scoped>
.checkable :deep(.n-collapse-item__header) {
  cursor: pointer;
}

.checkable :deep(.n-collapse-item__header-extra) {
  align-self: stretch;
  margin: -10px -10px -10px 0;
  padding: 10px 10px 10px 16px;
}
</style>
