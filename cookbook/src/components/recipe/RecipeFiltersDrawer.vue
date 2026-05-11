<script setup>
import {
  NDrawer,
  NDrawerContent,
  NForm,
  NFormItem,
  NSelect,
  NRadioGroup,
  NRadio,
  NSpace,
  NButton,
  NFlex,
} from "naive-ui"
import { computed } from "vue"
import {
  useRecipeFilters,
  useRecipeFilterOptions,
} from "@/composables/recipeFilters.js"
import { useAuthStore } from "@/data/auth.js"
import { _ } from "@/composables/translations.js"

defineProps({
  show: { type: Boolean, required: true },
})
const emit = defineEmits(["update:show"])

const { filters, reset, isActive } = useRecipeFilters()
const {
  chefOptions,
  ingredientOptions,
  tagOptions,
  allergenOptions,
  difficultyOptions,
  requiredTimeOptions,
} = useRecipeFilterOptions()

const auth = useAuthStore()
const canSeePrivate = computed(() => auth.isChef || auth.isEditor)

const sortOptions = computed(() => [
  { label: _.value.recipes.sort_newest, value: "newest" },
  { label: _.value.recipes.sort_oldest, value: "oldest" },
  { label: _.value.recipes.sort_name_asc, value: "name_asc" },
  { label: _.value.recipes.sort_name_desc, value: "name_desc" },
])

const close = () => emit("update:show", false)
</script>

<template>
  <n-drawer
    :show="show"
    :width="420"
    placement="right"
    @update:show="emit('update:show', $event)"
  >
    <n-drawer-content :title="_.common.filters" closable>
      <n-form label-placement="top">
        <n-form-item :label="_.recipes.sort_by">
          <n-select v-model:value="filters.sort" :options="sortOptions" />
        </n-form-item>

        <n-form-item :label="_.recipes.chef">
          <n-select
            v-model:value="filters.chef_ids"
            multiple
            filterable
            clearable
            :options="chefOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.difficulty">
          <n-select
            v-model:value="filters.difficulty_ids"
            multiple
            clearable
            :options="difficultyOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.required_time">
          <n-select
            v-model:value="filters.required_time_ids"
            multiple
            clearable
            :options="requiredTimeOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.tags_include">
          <n-select
            v-model:value="filters.tag_ids_include"
            multiple
            filterable
            clearable
            :options="tagOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.tags_exclude">
          <n-select
            v-model:value="filters.tag_ids_exclude"
            multiple
            filterable
            clearable
            :options="tagOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.allergens_exclude">
          <n-select
            v-model:value="filters.allergen_ids_exclude"
            multiple
            filterable
            clearable
            :options="allergenOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.ingredients_include">
          <n-select
            v-model:value="filters.ingredient_ids_include"
            multiple
            filterable
            clearable
            :options="ingredientOptions"
          />
        </n-form-item>

        <n-form-item :label="_.recipes.ingredients_exclude">
          <n-select
            v-model:value="filters.ingredient_ids_exclude"
            multiple
            filterable
            clearable
            :options="ingredientOptions"
          />
        </n-form-item>

        <n-form-item v-if="canSeePrivate" :label="_.recipes.visibility">
          <n-radio-group v-model:value="filters.visibility">
            <n-space>
              <n-radio value="all">{{ _.recipes.visibility_all }}</n-radio>
              <n-radio value="public">{{ _.recipes.is_public }}</n-radio>
              <n-radio value="private">{{ _.recipes.is_private }}</n-radio>
            </n-space>
          </n-radio-group>
        </n-form-item>
      </n-form>

      <template #footer>
        <n-flex justify="space-between" style="width: 100%">
          <n-button :disabled="!isActive" @click="reset">{{
            _.recipes.clear_filters
          }}</n-button>
          <n-button type="primary" @click="close">{{ _.common.close }}</n-button>
        </n-flex>
      </template>
    </n-drawer-content>
  </n-drawer>
</template>
