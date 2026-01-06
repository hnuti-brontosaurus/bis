<script setup>
import {
  NCollapse,
  NCollapseItem,
  NCheckbox,
  NPageHeader,
  NButton,
  NH2,
  NGridItem,
  NGrid,
  NCard,
  NDataTable,
  useThemeVars,
} from "naive-ui"
import { rand } from "@vueuse/core"
import { useConnector } from "@/composables/connector.js"
import { useRoute } from "vue-router"
import { computed, onMounted, ref, useSlots } from "vue"
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue"
import { isEmptyVNode } from "@/contrib/composables/helpers.js"

const props = defineProps({
  data: {},
  columns: {},
  getKey: { default: () => item => item.id },
  checkedKey: {},
})

const slots = useSlots()
const hasNoContent = item => {
  try {
    return slots.default?.(item).every(isEmptyVNode)
  } catch (e) {
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
