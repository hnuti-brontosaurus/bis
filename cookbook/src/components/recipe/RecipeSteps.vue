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
  useThemeVars
} from "naive-ui"
import {rand} from "@vueuse/core";
import {useConnector} from "@/composables/connector.js";
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue";
import {useServings} from "@/composables/servings.js";

const props = defineProps(["recipe"])
const recipe = computed(() => props.recipe)

const vars = useThemeVars()
</script>

<template>
  <n-h2>Postup</n-h2>
  <n-collapse accordion>
    <n-collapse-item v-for="(step, i) in recipe.steps" :key="step.id" :title="`${i+1}. ${step.name}`">
      <template v-if="step.description">
        {{ step.description }}
      </template>
      <template v-else>
        <div :style="`margin-top: -16px`"></div>
      </template>
      <template #arrow v-if="!step.description">
        <div :style="{width: vars.fontSizeMedium}"></div>
      </template>
    <template #header-extra>
      <n-checkbox @click.stop v-model:checked="step.done"/>
    </template>
    </n-collapse-item>
  </n-collapse>
</template>

<style scoped></style>
