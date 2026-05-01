<script setup>
import { NButton, NFlex, NForm, useDialog } from "naive-ui"
import { computed, onMounted, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import axios from "axios"
import AppPage from "@/components/app/AppPage.vue"
import GenericForm from "@/contrib/components/GenericForm.vue"
import { scrollToFirstFormError } from "@/contrib/composables/helpers.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { _ } from "@/composables/translations.js"

const route = useRoute()
const router = useRouter()
const dialog = useDialog()
const form = ref()

const ingredientsStore = useIngredientsStore()

const ingredient_id = route.params.id
const ingredient = ref(ingredient_id ? null : { name: "", state: "solid" })

onMounted(async () => {
  if (ingredient_id) {
    const fresh = await ingredientsStore.fetchOne(ingredient_id)
    ingredient.value = JSON.parse(JSON.stringify(fresh))
  }
})

const stateOptions = computed(() => [
  { value: "solid", label: _.value.ingredients.state_solid },
  { value: "liquid", label: _.value.ingredients.state_liquid },
])

const inputs = computed(() => {
  if (!ingredient.value) return []
  return [
    { type: "text", key: "name", required: true },
    {
      type: "select",
      key: "state",
      required: true,
      options: stateOptions.value,
    },
    { type: "number", key: "g_per_piece" },
    { type: "number", key: "g_per_liter" },
    { type: "number", key: "g_per_serving" },
  ]
})

const backendErrors = ref({})

const save = async () => {
  backendErrors.value = {}
  try {
    await form.value.validate()
    await ingredientsStore.save(ingredient.value)
    router.push({ name: "ingredients" })
  } catch (e) {
    if (axios.isAxiosError(e) && e.response?.status === 400 && e.response.data) {
      backendErrors.value = e.response.data
    } else {
      scrollToFirstFormError()
    }
    handleAxiosError(_.value.ingredients.upsert_error)(e)
  }
}

const onDelete = () => {
  dialog.warning({
    title: _.value.ingredients.delete_title,
    content: _.value.ingredients.delete_content,
    positiveText: _.value.ingredients.delete,
    negativeText: _.value.common.back,
    onPositiveClick: async () => {
      try {
        await ingredientsStore.remove(ingredient.value.id)
        router.push({ name: "ingredients" })
      } catch (e) {
        handleAxiosError(_.value.ingredients.delete_error)(e)
      }
    },
  })
}
</script>

<template>
  <AppPage :title="ingredient_id ? _.ingredients.edit_title : _.ingredients.new_title">
    <template #actions>
      <n-flex>
        <n-button @click="save">{{ _.common.save }}</n-button>
        <n-button v-if="ingredient_id" type="error" ghost @click="onDelete">{{
          _.ingredients.delete
        }}</n-button>
      </n-flex>
    </template>
    <n-form v-if="ingredient" ref="form" :model="ingredient" @keydown.enter="save">
      <GenericForm
        v-model:data="ingredient"
        :inputs="inputs"
        :backend-errors="backendErrors"
        group="Ingredient"
      />
    </n-form>
  </AppPage>
</template>

<style scoped></style>
