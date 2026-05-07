<script setup>
import { NCard, NFlex, NButton, NEmpty, NInput, NCheckbox } from "naive-ui"
import { nextTick, ref, watch } from "vue"
import { useRouter } from "vue-router"
import IngredientInput from "@/contrib/components/IngredientInput.vue"
import { faPlus, faTrash } from "@fortawesome/free-solid-svg-icons"
import { useRender } from "@/contrib/composables/render.js"
import { useCartStore } from "@/data/cart.js"
import { _ } from "@/composables/translations.js"

const { icon } = useRender()
const cart = useCartStore()
const router = useRouter()

const focusedGroupId = defineModel("focusedGroupId", { default: null })
const groupRefs = ref({})

// When opened from the shopping tab, scroll the requested group into view
// once it's mounted, then clear the focus so a tab re-entry doesn't keep
// re-scrolling.
watch(
  focusedGroupId,
  async id => {
    if (!id) return
    await nextTick()
    groupRefs.value[id]?.scrollIntoView({ behavior: "smooth", block: "start" })
    focusedGroupId.value = null
  },
  { immediate: true },
)

const newCustomName = ref("")

// Edits flow through direct mutation of cart.items entries — the store's
// deep watch debounces a single sync. Add/remove ingredient still go through
// the store action so the immutable replacement keeps refs stable for v-for.
const onAddRow = group => {
  group.ingredients.push({
    ingredient_id: null,
    unit_id: null,
    amount: 1,
    bought: false,
  })
}

const onRemoveRow = (group, index) => {
  group.ingredients.splice(index, 1)
}

const onAddCustomGroup = () => {
  const name = newCustomName.value.trim() || _.value.cart.custom_group
  cart.addCustomGroup(name)
  newCustomName.value = ""
}
</script>

<template>
  <n-flex vertical :size="16">
    <n-empty v-if="!cart.items.length" :description="_.cart.empty" />

    <n-card
      v-for="group in cart.items"
      :key="group.id"
      :ref="el => (groupRefs[group.id] = el?.$el ?? el)"
      size="small"
      :bordered="true"
    >
      <template #header>
        <n-flex align="center" justify="space-between" :wrap="false">
          <n-input
            v-if="!group.recipe_id"
            size="small"
            v-model:value="group.recipe_name"
            :placeholder="_.cart.custom_group"
            style="max-width: 320px"
          />
          <n-button
            v-else
            text
            tag="a"
            style="font-weight: 600"
            @click="router.push({ name: 'recipe', params: { id: group.recipe_id } })"
          >
            {{ group.recipe_name }}
          </n-button>
          <n-button
            type="error"
            ghost
            size="small"
            :render-icon="icon(faTrash)"
            @click="cart.removeGroup(group.id)"
          />
        </n-flex>
      </template>

      <n-flex vertical :size="6">
        <n-flex
          v-for="(ingredient, index) in group.ingredients"
          :key="index"
          align="center"
          :wrap="false"
          :size="8"
        >
          <n-checkbox v-model:checked="ingredient.bought" />
          <div style="flex: 1; min-width: 0">
            <IngredientInput :value="ingredient" />
          </div>
          <n-button
            quaternary
            circle
            size="small"
            :render-icon="icon(faTrash)"
            @click="onRemoveRow(group, index)"
          />
        </n-flex>
        <n-button
          dashed
          block
          size="small"
          :render-icon="icon(faPlus)"
          @click="onAddRow(group)"
        >
          {{ _.cart.add_ingredient }}
        </n-button>
      </n-flex>
    </n-card>

    <n-card size="small" :bordered="true">
      <n-flex align="center" :wrap="false" :size="8">
        <n-input
          size="small"
          v-model:value="newCustomName"
          :placeholder="_.cart.new_group_placeholder"
          style="flex: 1"
        />
        <n-button
          type="primary"
          size="small"
          :render-icon="icon(faPlus)"
          @click="onAddCustomGroup"
        >
          {{ _.cart.add_group }}
        </n-button>
      </n-flex>
    </n-card>
  </n-flex>
</template>
