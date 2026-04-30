<script setup>
import { NCollapse, NCollapseItem, NCheckbox } from "naive-ui"
import { useSlots } from "vue"
import { isEmptyVNode } from "@/contrib/composables/helpers.js"

defineProps({
  data: {},
  columns: {},
  getKey: { default: () => item => item.id },
  checkedKey: {},
})

const slots = useSlots()
const hasNoContent = item => {
  try {
    return slots.default?.(item).every(isEmptyVNode)
  } catch {
    return true
  }
}
</script>

<template>
  <!--  <n-collapse display-directive="show" :default-expanded-names="data.map(getKey)">-->
  <n-collapse display-directive="show">
    <n-collapse-item v-for="(item, i) in data" :key="getKey(item)" :name="getKey(item)">
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
        <n-checkbox @click.stop v-model:checked="item[checkedKey]" size="small" />
      </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style scoped></style>
