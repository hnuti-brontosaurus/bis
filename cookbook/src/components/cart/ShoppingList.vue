<script setup>
import {
  NFlex,
  NCheckbox,
  NText,
  NButton,
  NEmpty,
  NSelect,
  NInputNumber,
  NCollapseTransition,
} from "naive-ui"
import { computed, ref } from "vue"
import { faChevronDown, faChevronRight } from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"
import { useCartStore } from "@/data/cart.js"
import { useUnitsStore } from "@/data/units.js"
import { useCartSummed } from "@/composables/cartSummed.js"
import { convertAmount, isUnitAllowed } from "@/data/unitConversion.js"
import { _ } from "@/composables/translations.js"

const { icon } = useRender()
const emit = defineEmits(["jump-to-edit"])

const cart = useCartStore()
const unitsStore = useUnitsStore()
const { summed, displayAmountInUnit } = useCartSummed()

const hideBought = defineModel("hideBought", { type: Boolean, default: true })

// UI-only state — chosen display unit per summed row and per source row,
// expanded state per ingredient. Resets on navigation.
const chosenUnit = ref({})
const chosenUnitForSource = ref({})
const expanded = ref({})

const visibleRows = computed(() =>
  hideBought.value ? summed.value.filter(row => !row.bought) : summed.value,
)

const round2 = value => (value == null ? null : Math.round(value * 100) / 100)

const unitOptions = ingredient => {
  const all = unitsStore.list
  const allowed = ingredient ? all.filter(u => isUnitAllowed(u, ingredient)) : all
  return allowed.map(unit => ({
    label: unit.abbreviation || unit.name,
    value: unit.id,
  }))
}

const summedDisplay = row => {
  const unitId = chosenUnit.value[row.ingredient_id] ?? row.default_unit?.id
  if (unitId == null) return { unitId: null, amount: null }
  const amount =
    unitId === row.default_unit?.id
      ? row.default_amount
      : displayAmountInUnit(row, unitId)
  return { unitId, amount }
}

const sourceKey = source => `${source.group_id}:${source.ingredient_index}`

const sourceDisplay = (source, ingredient) => {
  const overrideId = chosenUnitForSource.value[sourceKey(source)]
  const fromUnit = unitsStore.byId[source.unit_id]
  if (overrideId == null || overrideId === source.unit_id) {
    return { unitId: source.unit_id, amount: source.amount, unit: fromUnit }
  }
  const target = unitsStore.byId[overrideId]
  const converted =
    target && fromUnit && ingredient
      ? convertAmount(source.amount, fromUnit, target, ingredient)
      : null
  return { unitId: overrideId, amount: converted, unit: target }
}

const toggleSummed = row => {
  cart.setIngredientBoughtAcross(row.ingredient_id, !row.bought)
}

const toggleSource = source => {
  cart.setIngredientBought(source.group_id, source.ingredient_index, !source.bought)
}

const toggleExpand = id => {
  expanded.value = { ...expanded.value, [id]: !expanded.value[id] }
}
</script>

<template>
  <n-flex vertical :size="16">
    <n-empty
      v-if="!visibleRows.length"
      :description="summed.length ? _.cart.all_bought : _.cart.empty"
    />

    <n-flex
      v-for="row in visibleRows"
      :key="row.ingredient_id"
      vertical
      :size="4"
      :style="{
        opacity: row.bought ? 0.55 : 1,
        borderBottom: '1px solid rgba(255,255,255,0.06)',
        paddingBottom: '8px',
      }"
    >
      <n-flex align="center" :wrap="false" :size="8">
        <n-checkbox :checked="row.bought" @update:checked="toggleSummed(row)" />
        <n-button
          quaternary
          size="small"
          :render-icon="
            icon(expanded[row.ingredient_id] ? faChevronDown : faChevronRight)
          "
          @click="toggleExpand(row.ingredient_id)"
        />
        <n-text
          :style="{
            flex: 1,
            textDecoration: row.bought ? 'line-through' : 'none',
          }"
        >
          {{ row.ingredient?.name ?? `#${row.ingredient_id}` }}
        </n-text>
        <template v-if="row.convertible.length && row.default_unit">
          <n-input-number
            size="small"
            style="width: 110px"
            :show-button="false"
            :value="round2(summedDisplay(row).amount)"
            disabled
            :format="value => (value == null ? '' : String(value))"
          />
          <n-select
            size="small"
            style="width: 90px"
            :value="summedDisplay(row).unitId"
            :options="unitOptions(row.ingredient)"
            @update:value="value => (chosenUnit[row.ingredient_id] = value)"
          />
        </template>
      </n-flex>

      <n-collapse-transition :show="!!expanded[row.ingredient_id]">
        <n-flex vertical :size="4" :style="{ paddingLeft: '36px', marginTop: '6px' }">
          <n-flex
            v-for="source in row.sources"
            v-show="!hideBought || !source.bought"
            :key="sourceKey(source)"
            align="center"
            :wrap="false"
            :size="8"
          >
            <n-checkbox
              :checked="source.bought"
              @update:checked="toggleSource(source)"
            />
            <n-button
              text
              tag="a"
              :style="{
                flex: 1,
                justifyContent: 'flex-start',
                textDecoration: source.bought ? 'line-through' : 'none',
              }"
              @click="emit('jump-to-edit', source.group_id)"
            >
              {{ source.recipe_name || _.cart.custom_group }}
            </n-button>
            <n-input-number
              size="small"
              style="width: 90px"
              :show-button="false"
              :value="round2(sourceDisplay(source, row.ingredient).amount)"
              disabled
              :format="value => (value == null ? '' : String(value))"
            />
            <n-select
              size="small"
              style="width: 90px"
              :value="sourceDisplay(source, row.ingredient).unitId"
              :options="unitOptions(row.ingredient)"
              @update:value="value => (chosenUnitForSource[sourceKey(source)] = value)"
            />
          </n-flex>
        </n-flex>
      </n-collapse-transition>
    </n-flex>
  </n-flex>
</template>
