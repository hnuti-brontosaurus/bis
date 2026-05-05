<script setup>
import { NInputGroup, NSelect, NInputNumber, NButton, useDialog } from "naive-ui"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { storeOptions } from "@/data/helpers.js"
import { _ } from "@/composables/translations.js"
import { ref } from "vue"
import { handleAxiosError } from "@/contrib/composables/setup.js"

const ingredientsStore = useIngredientsStore()
const unitsStore = useUnitsStore()

const value = defineModel("value")
const dialog = useDialog()
const loading = ref(false)

const ingredientOptions = storeOptions(ingredientsStore)
const unitOptions = storeOptions(unitsStore)

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
      v-model:value="value.unit_id"
      :options="unitOptions"
      filterable
      :clearable="false"
      placeholder=""
      show-on-focus
    />
  </n-input-group>
</template>

<style scoped>
.n-base-select-menu__empty {
  display: none;
}
</style>
