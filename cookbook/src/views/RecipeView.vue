<script setup>
import {
  NFlex,
  NTag,
  NList,
  NText,
  NButton,
  NListItem,
  NImage,
  NH2,
  NGridItem,
  NGrid,
} from "naive-ui"
import { computed, onMounted, watch } from "vue"
import { useRoute } from "vue-router"
import { useRecipesStore, useRecipe } from "@/data/recipes.js"
import { useChefsStore } from "@/data/chefs.js"
import { useRecipeDifficultiesStore } from "@/data/recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "@/data/recipeRequiredTimes.js"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue"
import CollapseList from "@/contrib/components/CollapseList.vue"
import AppPage from "@/components/app/AppPage.vue"
import { _ } from "@/composables/translations.js"

const route = useRoute()
const recipesStore = useRecipesStore()

// Reference data — needed to resolve `_id` fields into objects.
useChefsStore().fetchAll()
useRecipeDifficultiesStore().fetchAll()
useRecipeRequiredTimesStore().fetchAll()
useRecipeTagsStore().fetchAll()
useIngredientsStore().fetchAll()
useUnitsStore().fetchAll()

const ensureLoaded = id => recipesStore.fetchOne(id)
onMounted(() => ensureLoaded(route.params.id))
watch(() => route.params.id, ensureLoaded)

const recipeId = computed(() => route.params.id)
const recipe = useRecipe(recipeId)
</script>

<template>
  <AppPage v-if="recipe" vertical :title="recipe.name">
    <template #actions>
      <n-button
        @click="$router.push({ name: 'edit_recipe', params: { id: $route.params.id } })"
        >{{ _.recipes.edit }}</n-button
      >
    </template>

    <template #extra>
      <n-flex>
        <n-image :src="recipe.photo.large" :alt="recipe.name" height="300" />
        <n-list>
          <n-list-item v-if="recipe.chef">
            <template #prefix>{{ _.recipes.chef }}:</template>{{ recipe.chef.name }}
          </n-list-item>
          <n-list-item v-if="recipe.difficulty">
            <template #prefix>{{ _.recipes.difficulty }}:</template
            >{{ recipe.difficulty.name }}
          </n-list-item>
          <n-list-item>
            <template #prefix>{{ _.recipes.tags }}:</template>
            <n-flex size="small">
              <n-tag v-for="tag in recipe.tags" :key="tag.id" round>{{
                tag.name
              }}</n-tag>
            </n-flex>
          </n-list-item>
        </n-list>
      </n-flex>
    </template>

    <n-text v-if="recipe.intro">
      {{ recipe.intro }}
    </n-text>

    <n-grid cols="1 m:2" responsive="screen" x-gap="64" y-gap="64">
      <n-grid-item>
        <RecipeIngrediences :recipe="recipe"></RecipeIngrediences>
      </n-grid-item>
      <n-grid-item>
        <n-h2>{{ _.recipes.steps }}</n-h2>
        <CollapseList :data="recipe.steps" checked-key="done">
          <template #header="{ item, i }"> {{ i + 1 }}. {{ item.name }} </template>
          <template #default="{ item }">
            <n-flex v-if="item.description || item.photo">
              <n-text v-if="item.description">{{ item.description }}</n-text>
              <n-image
                v-if="item.photo"
                :preview-src="item.photo.large"
                :src="item.photo.medium"
                style="width: 100%"
                width="100%"
              ></n-image>
            </n-flex>
          </template>
        </CollapseList>
      </n-grid-item>
      <n-grid-item v-if="recipe.tips.length">
        <n-h2>{{ _.recipes.tips }}</n-h2>
        <CollapseList :data="recipe.tips">
          <template #default="{ item }">
            {{ item.description }}
          </template>
        </CollapseList>
      </n-grid-item>
      <n-grid-item>
        <n-h2>{{ _.recipes.comments }}</n-h2>
        <CollapseList :data="recipe.comments" />
      </n-grid-item>
      <n-grid-item span="2">
        <n-h2>{{ _.recipes.sources }}</n-h2>
        <n-text>{{ recipe.sources }}</n-text>
      </n-grid-item>
    </n-grid>
  </AppPage>
</template>

<style scoped></style>
