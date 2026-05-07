<script setup>
import { NModal, NCard, NFlex, NCheckbox, NButton, NText, NInputNumber } from "naive-ui"
import { computed, ref, watch } from "vue"
import IngredientInput from "@/contrib/components/IngredientInput.vue"
import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"
import { _ } from "@/composables/translations.js"
import { servings } from "@/composables/servings.js"

const { icon } = useRender()

const props = defineProps({
  show: { type: Boolean, default: false },
  recipe: { type: Object, required: true },
  selectedIds: { type: Array, default: () => [] },
})
const emit = defineEmits(["update:show", "confirm"])

const newRowKey = () =>
  globalThis.crypto?.randomUUID?.() ??
  `r_${Date.now()}_${Math.random().toString(36).slice(2)}`

const rows = ref([])

const buildRowsFromRecipe = () => {
  const selected = new Set(props.selectedIds)
  return props.recipe.ingredients.map(ri => ({
    key: `recipe_${ri.id}`,
    checked: selected.has(ri.id),
    baseAmount: ri.amount,
    value: {
      ingredient_id: ri.ingredient_id,
      unit_id: ri.unit_id,
      amount: ri.amount * servings.value,
    },
  }))
}

watch(
  () => props.show,
  show => {
    if (show) rows.value = buildRowsFromRecipe()
  },
  { immediate: true },
)

watch(servings, n => {
  if (!props.show) return
  rows.value.forEach(r => {
    if (r.baseAmount != null) r.value.amount = r.baseAmount * n
  })
})

const addRow = () => {
  rows.value = [
    ...rows.value,
    {
      key: newRowKey(),
      checked: true,
      value: { ingredient_id: null, unit_id: null, amount: 1 },
    },
  ]
}

const removeRow = key => {
  rows.value = rows.value.filter(r => r.key !== key)
}

const canConfirm = computed(() =>
  rows.value.some(
    r => r.checked && r.value.ingredient_id && r.value.unit_id && r.value.amount > 0,
  ),
)

const onConfirm = () => {
  const ingredients = rows.value
    .filter(
      r => r.checked && r.value.ingredient_id && r.value.unit_id && r.value.amount > 0,
    )
    .map(r => ({ ...r.value }))
  if (!ingredients.length) return
  emit("confirm", {
    recipe_id: props.recipe.id,
    recipe_name: props.recipe.name,
    ingredients,
  })
  emit("update:show", false)
}

const onCancel = () => emit("update:show", false)
</script>

<template>
  <n-modal :show="show" @update:show="v => emit('update:show', v)">
    <n-card
      :title="`${_.cart.add_to_cart}: ${recipe.name}`"
      style="max-width: 720px; width: 90vw"
      :bordered="false"
      role="dialog"
    >
      <n-flex vertical>
        <n-flex align="baseline" :wrap="false">
          <n-text>{{ _.recipes.servings }}:</n-text>
          <n-input-number
            size="small"
            style="width: 110px"
            v-model:value="servings"
            min="1"
            :precision="1"
          />
        </n-flex>
        <n-flex
          v-for="row in rows"
          :key="row.key"
          align="center"
          :wrap="false"
          :size="8"
        >
          <n-checkbox v-model:checked="row.checked" />
          <div style="flex: 1; min-width: 0">
            <IngredientInput v-model:value="row.value" />
          </div>
          <n-button
            quaternary
            circle
            size="small"
            :render-icon="icon(faTrash)"
            @click="removeRow(row.key)"
          />
        </n-flex>
        <n-button dashed block :render-icon="icon(faPlus)" @click="addRow">
          {{ _.cart.add_ingredient }}
        </n-button>
      </n-flex>
      <template #action>
        <n-flex justify="end">
          <n-button @click="onCancel">{{ _.common.back }}</n-button>
          <n-button type="primary" :disabled="!canConfirm" @click="onConfirm">
            {{ _.cart.add }}
          </n-button>
        </n-flex>
      </template>
    </n-card>
  </n-modal>
</template>
