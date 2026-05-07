<script setup>
import {
  NFlex,
  NText,
  NButton,
  NH2,
  NDataTable,
  NInputNumber,
  NInputGroup,
  useDialog,
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
import { pluralizeUnit } from "@/data/unitConversion.js"
import { useCartStore } from "@/data/cart.js"
import AddToCartDialog from "@/components/cart/AddToCartDialog.vue"

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
    {
      key: "ingredient.name",
      render: row =>
        row.is_optional ? h("em", {}, row.ingredient?.name) : row.ingredient?.name,
    },
    {
      key: "amount",
      render: row => {
        const amount = Math.round(row.amount * servings.value * 100) / 100
        const text = `${amount} ${pluralizeUnit(amount, row.unit)}`
        return row.is_optional ? h("em", {}, text) : text
      },
    },
    { type: "selection" },
  ]
})

const ready = ref([])
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

const dialog = useDialog()
const cartStore = useCartStore()
const showAddToCart = ref(false)

const onConfirmAdd = group => {
  if (!cartStore.meaningful.length) {
    cartStore.replaceWith(group)
    return
  }
  if (cartStore.isStale) {
    dialog.warning({
      title: _.value.cart.stale_title,
      content: _.value.cart.stale_content,
      positiveText: _.value.cart.replace,
      negativeText: _.value.cart.append,
      onPositiveClick: () => cartStore.replaceWith(group),
      onNegativeClick: () => cartStore.addGroup(group),
    })
  } else {
    cartStore.addGroup(group)
  }
}
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
        <n-button
          :render-icon="icon(faCartPlus)"
          size="small"
          @click="showAddToCart = true"
        ></n-button>
      </n-input-group>
    </n-flex>
  </n-flex>

  <AddToCartDialog
    v-model:show="showAddToCart"
    :recipe="recipe"
    @confirm="onConfirmAdd"
  />

  <n-data-table
    :data="data"
    :columns="columns"
    v-model:checked-row-keys="ready"
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
