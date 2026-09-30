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
import { isPartHeading, withPartHeadings } from "@/data/ingredientParts.js"

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
      colSpan: row => (isPartHeading(row) ? 2 : 1),
      render: row => {
        if (isPartHeading(row)) return h("span", { class: "section-heading" }, row.name)
        return row.is_optional
          ? h("em", {}, row.ingredient?.name)
          : row.ingredient?.name
      },
    },
    {
      key: "amount",
      align: "right",
      className: "amount",
      render: row => {
        const amount = Math.round(row.amount * servings.value * 100) / 100
        const unit = h(NText, { depth: 3 }, () => pluralizeUnit(amount, row.unit))
        return h(row.is_optional ? "em" : "span", {}, [`${amount} `, unit])
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

const toggled = (keys, key) =>
  keys.includes(key) ? keys.filter(other => other !== key) : [...keys, key]

// A part heading ticks or unticks every ingredient below it, and shows as
// ticked exactly when all of them are.
const updateReady = keys => {
  const next = new Set(keys)
  Object.entries(partIngredients.value).forEach(([heading, ingredients]) => {
    if (next.has(heading) !== ready.value.includes(heading)) {
      if (next.has(heading)) ingredients.forEach(key => next.add(key))
      else ingredients.forEach(key => next.delete(key))
    }
    if (ingredients.every(key => next.has(key))) next.add(heading)
    else next.delete(heading)
  })
  ready.value = [...next]
}

// The checkbox and the expand arrow are small targets, so the whole row opens
// the comment and the whole checkbox cell ticks the ingredient; a row with
// nothing to open ticks instead. Clicks that land on the controls themselves
// are left to the table.
const rowProps = row => ({
  style: "cursor: pointer",
  onClick: event => {
    if (event.target.closest(".n-checkbox, .n-data-table-expand-trigger")) return
    if (expandable(row) && !event.target.closest(".n-data-table-td--selection"))
      expanded.value = toggled(expanded.value, row.key)
    else updateReady(toggled(ready.value, row.key))
  },
})

const data = computed(() => {
  return withPartHeadings(recipe.value.ingredients).map(row =>
    isPartHeading(row) ? { ...row, key: `part-${row.name}` } : { ...row, key: row.id },
  )
})

// The table has no header-row hook.
const onHeaderClick = event => {
  if (!event.target.closest(".n-data-table-thead")) return
  if (event.target.closest(".n-checkbox, .n-button")) return
  if (!event.target.closest(".n-data-table-th--selection")) expandAll()
  else if (ready.value.length === data.value.length) updateReady([])
  else updateReady(data.value.map(row => row.key))
}

const partIngredients = computed(() => {
  const parts = {}
  let heading
  data.value.forEach(row => {
    if (isPartHeading(row)) parts[(heading = row.key)] = []
    else if (heading) parts[heading].push(row.key)
  })
  return parts
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
  <n-flex align="center" justify="space-between">
    <n-h2>{{ _.recipes.ingredients }}</n-h2>
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
    :row-props="rowProps"
    :checked-row-keys="ready"
    @update:checked-row-keys="updateReady"
    v-model:expanded-row-keys="expanded"
    :bordered="false"
    :bottom-bordered="false"
    @click="onHeaderClick"
  >
  </n-data-table>
</template>

<style scoped>
:deep(.n-data-table-thead) {
  cursor: pointer;
}

:deep(.amount) {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
