<script setup>
import { NCollapse, NCollapseItem, NCheckbox, NH2 } from "naive-ui"
import { computed } from "vue"
import { theme } from "@/composables/theme.js"

const props = defineProps(["recipe"])
const recipe = computed(() => props.recipe)
</script>

<template>
  <n-h2>Postup</n-h2>
  <n-collapse accordion>
    <n-collapse-item
      v-for="(step, i) in recipe.steps"
      :key="step.id"
      :title="`${i + 1}. ${step.name}`"
    >
      <template v-if="step.description">
        {{ step.description }}
      </template>
      <template v-else>
        <div :style="`margin-top: -16px`"></div>
      </template>
      <template #arrow v-if="!step.description">
        <div :style="{ width: theme.common.fontSizeMedium }"></div>
      </template>
      <template #header-extra>
        <n-checkbox @click.stop v-model:checked="step.done" />
      </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style scoped></style>
