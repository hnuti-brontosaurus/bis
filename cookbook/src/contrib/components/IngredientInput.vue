<script setup>
import { NInputGroup, NSelect, NInputNumber, NButton, useDialog } from "naive-ui"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { storeOptions } from "@/data/helpers.js"
import { _ } from "@/composables/translations.js"
import { computed, ref } from "vue"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import {
  isUnitAllowed,
  convertAmount,
  pluralizeUnit,
  SPECIAL_UNIT_GRAMS,
} from "@/data/unitConversion.js"

const ingredientsStore = useIngredientsStore()
const unitsStore = useUnitsStore()

const value = defineModel("value")
const dialog = useDialog()
const loading = ref(false)

const ingredientOptions = storeOptions(ingredientsStore)

const selectedIngredient = computed(
  () => ingredientsStore.byId[value.value.ingredient_id],
)

/**
 * Hide units that can't be converted to/from grams for this ingredient.
 * If no ingredient is picked yet, show every unit so the user isn't blocked.
 * Special piece units (clove, bulb, …) only appear for the ingredients that
 * declare them in SPECIAL_UNIT_GRAMS. The currently-selected unit is always
 * included even if it fails the filter — otherwise n-select would render the
 * raw unit_id as the label and the user couldn't see what they're switching from.
 */
const unitOptions = computed(() => {
  const all = unitsStore.list
  const ing = selectedIngredient.value
  const specialSlugs = new Set(
    Object.values(SPECIAL_UNIT_GRAMS).flatMap(m => Object.keys(m)),
  )
  const visible = ing
    ? all.filter(u => isUnitAllowed(u, ing) || u.id === value.value.unit_id)
    : all.filter(u => !specialSlugs.has(u.slug) || u.id === value.value.unit_id)
  return visible.map(u => ({
    label: pluralizeUnit(value.value.amount, u),
    value: u.id,
  }))
})

const onUnitChange = newUnitId => {
  const prevUnit = unitsStore.byId[value.value.unit_id]
  const nextUnit = unitsStore.byId[newUnitId]
  const ing = selectedIngredient.value
  if (ing && prevUnit && nextUnit && value.value.amount != null) {
    const converted = convertAmount(value.value.amount, prevUnit, nextUnit, ing)
    if (converted != null && Number.isFinite(converted)) {
      value.value.amount = Math.round(converted * 100) / 100
    }
  }
  value.value.unit_id = newUnitId
}

const input = ref("")
const fallback = () => ({ label: `${_.value.ingredients.new}: ${input.value}` })

const createIngredient = () => {
  dialog.create({
    title: _.value.ingredients.create_title,
    content: _.value.ingredients.create_content,
    positiveText: _.value.ingredients.create,
    negativeText: _.value.ingredients.go_back,
    onPositiveClick: async () => {
      loading.value = true
      try {
        const created = await ingredientsStore.save({ name: input.value })
        value.value.ingredient_id = created.id
      } catch (e) {
        handleAxiosError(_.value.ingredients.upsert_error)(e)
      } finally {
        loading.value = false
      }
    },
  })
}
</script>

<template>
  <n-input-group>
    <n-select
      v-model:value="value.ingredient_id"
      :options="ingredientOptions"
      filterable
      :clearable="false"
      placeholder=""
      show-on-focus
      :fallback-option="fallback"
      :loading="loading"
      @search="v => (input = v)"
    >
      <template #action>
        <n-button
          v-if="input.length"
          text
          style="width: 100%; justify-content: flex-start"
          @click="createIngredient"
          >{{ _.ingredients.new }}: {{ input }}</n-button
        >
      </template>
      <template #empty>
        <div class="input_empty_hide"></div>
      </template>
    </n-select>
    <n-input-number
      v-model:value="value.amount"
      :show-button="false"
      :format="v => (v != null ? String(Math.round(v * 100) / 100) : '')"
      :parse="parseFloat"
    />
    <n-select
      :value="value.unit_id"
      :options="unitOptions"
      filterable
      :clearable="false"
      placeholder=""
      show-on-focus
      @update:value="onUnitChange"
    />
  </n-input-group>
</template>

<style scoped>
.n-base-select-menu__empty {
  display: none;
}
</style>
