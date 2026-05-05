<script setup>
import { h } from "vue"
import { NButton, NDataTable, NTag, NSpace } from "naive-ui"
import { computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { storeToRefs } from "pinia"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useAllergensStore } from "@/data/allergens.js"
import { useAuthStore } from "@/data/auth.js"
import AppPage from "@/components/app/AppPage.vue"
import { _ } from "@/composables/translations.js"

const router = useRouter()
const ingredientsStore = useIngredientsStore()
const allergensStore = useAllergensStore()
const { isChef } = storeToRefs(useAuthStore())

onMounted(() => {
  ingredientsStore.fetchAll()
  allergensStore.fetchAll()
})

const stateLabel = state =>
  state === "liquid"
    ? _.value.ingredients.state_liquid
    : _.value.ingredients.state_solid

const renderAllergens = row => {
  const ids = row.allergen_ids ?? []
  if (!ids.length) return ""
  return h(NSpace, { size: "small" }, () =>
    ids
      .map(id => allergensStore.byId[id])
      .filter(Boolean)
      .map(a => h(NTag, { type: "warning", round: true, size: "small" }, () => a.name)),
  )
}

const columns = computed(() => [
  { title: _.value.ingredients.name, key: "name" },
  {
    title: _.value.ingredients.state,
    key: "state",
    render: row => stateLabel(row.state),
  },
  { title: _.value.ingredients.g_per_piece, key: "g_per_piece" },
  { title: _.value.ingredients.g_per_liter, key: "g_per_liter" },
  { title: _.value.ingredients.g_per_serving, key: "g_per_serving" },
  {
    title: _.value.Ingredient.allergens,
    key: "allergen_ids",
    render: renderAllergens,
  },
])

const rowProps = row => ({
  style: "cursor: pointer",
  onClick: () => {
    if (isChef.value) {
      router.push({ name: "edit_ingredient", params: { id: row.id } })
    }
  },
})

const data = computed(() =>
  [...ingredientsStore.list].sort((a, b) => a.name.localeCompare(b.name)),
)
</script>

<template>
  <AppPage :title="_.ingredients.title">
    <template #actions>
      <n-button v-if="isChef" @click="router.push({ name: 'create_ingredient' })">{{
        _.ingredients.create
      }}</n-button>
    </template>
    <n-data-table
      :columns="columns"
      :data="data"
      :row-props="rowProps"
      :pagination="{ pageSize: 50 }"
    />
  </AppPage>
</template>

<style scoped></style>
