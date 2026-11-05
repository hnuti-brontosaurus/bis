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
import { computed, h, ref, watch } from "vue"
import {
  faCalculator,
  faCartPlus,
  faChevronDown,
  faChevronRight,
} from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"
import { _ } from "@/composables/translations.js"
import {
  convertAmount,
  convertibleUnits,
  pluralizeUnit,
  roundAmount,
} from "@/data/unitConversion.js"
import { useCartStore } from "@/data/cart.js"
import { useUnitsStore } from "@/data/units.js"
import AddToCartDialog from "@/components/cart/AddToCartDialog.vue"
import UnitConverterDialog from "@/components/recipe/UnitConverterDialog.vue"
import HtmlText from "@/components/app/HtmlText.vue"
import RecipePhotos from "@/components/recipe/RecipePhotos.vue"
import { isPartHeading, withPartHeadings } from "@/data/ingredientParts.js"

const { icon } = useRender()
const props = defineProps(["recipe"])
const recipe = computed(() => props.recipe)
const servings = ref()
watch(
  () => [recipe.value.id, recipe.value.default_servings],
  () => (servings.value = recipe.value.default_servings),
  { immediate: true },
)
const unitsStore = useUnitsStore()

// Units picked in the converter, by recipe ingredient id; kept for the visit.
const shownUnitIds = ref({})
const converting = ref(null)
const showConverter = ref(false)
const convert = row => {
  converting.value = row
  showConverter.value = true
}
const recipeAmount = row => row.amount * servings.value
const shownUnit = row => unitsStore.byId[shownUnitIds.value[row.id]] ?? row.unit
const shownAmount = row =>
  roundAmount(
    convertAmount(recipeAmount(row), row.unit, shownUnit(row), row.ingredient),
  )
const isConvertible = row => convertibleUnits(unitsStore.list, row).length > 1

const expandable = row => !row.optionalHeading && (row.comment || row.photos?.length)
const columns = computed(() => {
  return [
    {
      type: "expand",
      width: 28,
      className: "compact",
      expandable,
      renderExpand: row =>
        h(NFlex, { vertical: true }, () => [
          row.comment && h(HtmlText, { html: row.comment }),
          row.photos.length &&
            h(RecipePhotos, { photos: row.photos, alt: row.ingredient?.name }),
        ]),
      // Kept in the layout when there is nothing to expand, because the
      // button is what gives the header row its height.
      title: h(
        NButton,
        {
          size: "tiny",
          quaternary: true,
          onClick: expandAll,
          style: recipe.value.ingredients.some(expandable) ? "" : "visibility: hidden",
        },
        expanded.value.length ? icon(faChevronDown) : icon(faChevronRight),
      ),
    },
    {
      key: "ingredient.name",
      // An optional heading is a divider, so it has no checkbox to keep.
      colSpan: row => (row.optionalHeading ? 4 : isPartHeading(row) ? 3 : 1),
      render: row => {
        if (row.optionalHeading)
          return h("span", { class: "optional-heading" }, _.value.recipes.optional)
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
        const amount = shownAmount(row)
        const unit = h(NText, { depth: 3 }, () => pluralizeUnit(amount, shownUnit(row)))
        return h(row.is_optional ? "em" : "span", {}, [`${amount ?? "–"} `, unit])
      },
    },
    {
      key: "convert",
      width: 32,
      className: "compact",
      render: row =>
        isConvertible(row) &&
        h(NButton, {
          size: "tiny",
          quaternary: true,
          title: _.value.recipes.convert_units,
          renderIcon: icon(faCalculator),
          onClick: () => convert(row),
        }),
    },
    { type: "selection", width: 32, className: "compact" },
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
  style: row.optionalHeading ? "" : "cursor: pointer",
  onClick: event => {
    if (row.optionalHeading) return
    if (event.target.closest(".n-checkbox, .n-button, .n-data-table-expand-trigger"))
      return
    if (expandable(row) && !event.target.closest(".n-data-table-td--selection"))
      expanded.value = toggled(expanded.value, row.key)
    else updateReady(toggled(ready.value, row.key))
  },
})

// Within each part the optional ingredients come last, below a divider.
const data = computed(() => {
  const rows = []
  let ingredients = []
  const addIngredients = () => {
    const optional = ingredients.filter(row => row.is_optional)
    rows.push(...ingredients.filter(row => !row.is_optional))
    if (optional.length)
      rows.push({ key: `optional-${rows.length}`, optionalHeading: true }, ...optional)
    ingredients = []
  }
  withPartHeadings(recipe.value.ingredients).forEach(row => {
    if (isPartHeading(row)) {
      addIngredients()
      rows.push({ ...row, key: `part-${row.name}` })
    } else ingredients.push({ ...row, key: row.id })
  })
  addIngredients()
  return rows
})
const tickable = computed(() => data.value.filter(row => !row.optionalHeading))

// The table has no header-row hook.
const onHeaderClick = event => {
  if (!event.target.closest(".n-data-table-thead")) return
  if (event.target.closest(".n-checkbox, .n-button")) return
  if (!event.target.closest(".n-data-table-th--selection")) expandAll()
  else if (ready.value.length === tickable.value.length) updateReady([])
  else updateReady(tickable.value.map(row => row.key))
}

const partIngredients = computed(() => {
  const parts = {}
  let heading
  data.value.forEach(row => {
    if (isPartHeading(row)) parts[(heading = row.key)] = []
    else if (heading && !row.optionalHeading) parts[heading].push(row.key)
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
  <n-text v-if="recipe.servings_note" tag="div" depth="3" class="servings-note">
    <HtmlText :html="recipe.servings_note" />
  </n-text>

  <AddToCartDialog
    v-model:show="showAddToCart"
    v-model:servings="servings"
    :recipe="recipe"
    @confirm="onConfirmAdd"
  />

  <UnitConverterDialog
    v-model:show="showConverter"
    :row="converting"
    :amount="converting && recipeAmount(converting)"
    :unit-id="converting && shownUnitIds[converting.id]"
    @update:unit-id="unitId => (shownUnitIds[converting.id] = unitId)"
  />

  <n-data-table
    :data="data"
    :columns="columns"
    :row-props="rowProps"
    :row-class-name="row => (row.optionalHeading ? 'optional-row' : '')"
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
.servings-note {
  display: block;
  max-width: 66ch;
  margin-bottom: 8px;
}

:deep(.n-data-table-thead) {
  cursor: pointer;
}

:deep(.compact) {
  padding-right: 4px;
  padding-left: 4px;
}

:deep(.optional-row td) {
  padding-top: 16px;
  padding-bottom: 4px;
}

:deep(.optional-heading) {
  color: var(--muted);
  font-size: 0.8em;
  font-style: italic;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

:deep(.amount) {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
</style>
