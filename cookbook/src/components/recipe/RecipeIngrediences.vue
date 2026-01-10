<script setup>
import {
  NFlex,
  NH1,
  NText,
  NPageHeader,
  NButton,
  NH2,
  NH3,
  NH4,
  NH5,
  NH6,
  NCollapse,
  NCollapseItem,
  NGridItem,
  NGrid,
  NCard,
  NDataTable,
  useThemeVars,
  NInputNumber,
  NInputGroup,
  NCheckbox,
} from "naive-ui"
import { rand } from "@vueuse/core"
import { useConnector } from "@/composables/connector.js"
import { useRoute } from "vue-router"
import { computed, h, onMounted, ref } from "vue"
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue"
import { servings } from "@/composables/servings.js"
import {
  faCartPlus,
  faChevronDown,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"

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
    { key: "amount", render: row => `${row.amount * servings.value} ${row.unit.name}` },
    // {key: "selected", render: row => h(NCheckbox, {checked: row.is_required, 'onUpdate:checked': (val) => {
    //     recipe.value.ingredients.find(_ => _.id === row.id).is_required = val
    //     }})},
    {
      type: "selection",
      options: [
        {
          key: "all",
          label: "Vyber vše",
          onSelect: () => (selected.value = recipe.value.ingredients.map(_ => _.id)),
        },
        {
          key: "default",
          label: "Vyber výchozí",
          onSelect: () =>
            (selected.value = recipe.value.ingredients
              .filter(_ => _.is_required)
              .map(_ => _.id)),
        },
      ],
    },
  ]
})

const selected = ref(recipe.value.ingredients.filter(_ => _.is_required).map(_ => _.id))
const expanded = ref([])
const expandAll = () => {
  if (expanded.value.length) {
    expanded.value = []
  } else {
    expanded.value = recipe.value.ingredients.filter(expandable).map(_ => _.id)
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
    <n-h2 style="margin-bottom: 0">Ingredience</n-h2>
    <n-flex align="baseline" :wrap="false">
      <n-text>Porcí:</n-text>
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
