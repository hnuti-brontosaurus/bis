<script setup>
import {
  NFlex,
  NText,
  NButton,
  NH2,
  NDataTable,
  NInputNumber,
  NInputGroup,
} from "naive-ui"
import { computed, h, ref } from "vue"
import { servings } from "@/composables/servings.js"
import {
  faCartPlus,
  faChevronDown,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"
import { _ } from "@/composables/translations.js"

const { icon } = useRender()
const props = defineProps(["recipe"])
const recipe = computed(() => props.recipe)
const expandable = row => row.comment
const columns = computed(() => {
  return [
    {
      type: "expand",
      expandable,
      renderExpand: row => row.comment,
      title: h(
        NButton,
        { size: "tiny", quaternary: true, onClick: expandAll },
        expanded.value.length ? icon(faChevronDown) : icon(faChevronRight),
      ),
    },
    { key: "ingredient.name" },
    {
      key: "amount",
      render: row =>
        `${Math.round(row.amount * servings.value * 100) / 100} ${row.unit.name}`,
    },
    {
      type: "selection",
      options: [
        {
          key: "all",
          label: _.value.recipes.select_all,
          onSelect: () => (selected.value = recipe.value.ingredients.map(i => i.id)),
        },
        {
          key: "default",
          label: _.value.recipes.select_default,
          onSelect: () =>
            (selected.value = recipe.value.ingredients
              .filter(i => i.is_required)
              .map(i => i.id)),
        },
      ],
    },
  ]
})

const selected = ref(recipe.value.ingredients.filter(i => i.is_required).map(i => i.id))
const expanded = ref([])
const expandAll = () => {
  if (expanded.value.length) {
    expanded.value = []
  } else {
    expanded.value = recipe.value.ingredients.filter(expandable).map(i => i.id)
  }
}

const data = computed(() => {
  return recipe.value.ingredients.map(ingredient => ({
    ...ingredient,
    key: ingredient.id,
  }))
})
</script>

<template>
  <n-flex align="end" justify="space-between" :style="{ 'margin-bottom': '30px' }">
    <n-h2 style="margin-bottom: 0">{{ _.recipes.ingredients }}</n-h2>
    <n-flex align="baseline" :wrap="false">
      <n-text>{{ _.recipes.servings }}:</n-text>
      <n-input-group>
        <n-input-number
          size="small"
          style="width: 110px"
          v-model:value="servings"
          min="1"
          :precision="1"
        />
        <n-button :render-icon="icon(faCartPlus)" size="small"></n-button>
      </n-input-group>
    </n-flex>
  </n-flex>

  <n-data-table
    :data="data"
    :columns="columns"
    v-model:checked-row-keys="selected"
    v-model:expanded-row-keys="expanded"
    :bordered="false"
    :bottom-bordered="false"
  >
  </n-data-table>
</template>

<style scoped>
th {
  background-color: black !important;
}
</style>
