<script setup>
import { NInputGroup, NSelect, NText, NInputNumber, NButton, useDialog } from "naive-ui"
import { useWindowSize } from "@vueuse/core"
import { propertyRef, textFilter, toValueLabel } from "@/contrib/composables/helpers.js"
import {
  chefs,
  dataIdMapping,
  dataOptions,
  ingredients,
  units,
  useConnector,
} from "@/composables/connector.js"
import { _ } from "@/composables/translations.js"
import { ref } from "vue"
import { handleAxiosError } from "@/contrib/composables/setup.js"

const { width } = useWindowSize()
const connector = useConnector("ingredients", false)

const value = defineModel("value")
const dialog = useDialog()
const loading = ref(false)

const ingredientValue = dataIdMapping(ingredients, propertyRef(value, "ingredient"))
const ingredientOptions = dataOptions(ingredients)
const unitValue = dataIdMapping(units, propertyRef(value, "unit"))
const unitOptions = dataOptions(units)

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
        value.value.ingredient = await connector.upsert({ name: input.value })
      } catch (e) {
        handleAxiosError(_.value.ingredients.upsert_error)
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
      v-model:value="ingredientValue"
      :options="ingredientOptions"
      filterable
      :clearable="false"
      placeholder=""
      show-on-focus
      :fallback-option="fallback"
      @search="v => (input = v)"
      :loading="loading"
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
    <n-input-number v-model:value="value.amount" :show-button="false" />
    <n-select
      v-model:value="unitValue"
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
