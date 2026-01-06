<script setup>
import {
  NFlex,
  NH1,
  NTag,
  NList,
  NText,
  NPageHeader,
  NButton,
  NListItem,
  NButtonGroup,
  NCard,
  NInputGroup,
  NImage,
  NH2,
  NGridItem,
  NGrid,
  NInputNumber,
  NDataTable,
  useThemeVars,
} from "naive-ui"
import { rand } from "@vueuse/core"
import { useConnector } from "@/composables/connector.js"
import { useRoute } from "vue-router"
import { computed, onMounted } from "vue"
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue"
import RecipeSteps from "@/components/recipe/RecipeSteps.vue"
import CollapseList from "@/contrib/components/CollapseList.vue"
import { useRender } from "@/contrib/composables/render.js"
import { faCartPlus } from "@fortawesome/free-solid-svg-icons"
import AppPage from "@/components/app/AppPage.vue"

const route = useRoute()
const { icon } = useRender()

const { recipes, refresh } = useConnector("recipes", false)
refresh(route.params.id)
const recipe = computed(() => recipes.value[route.params.id])

const getIngredientTitle = ingredient =>
  `${ingredient.amount * servings.value} ${ingredient.unit.name} ${ingredient.ingredient.name}`
</script>

<template>
  <AppPage vertical :title="recipe.name">
    <template #actions>
      <n-button
        @click="$router.push({ name: 'edit_recipe', params: { id: $route.params.id } })"
        >upravit</n-button
      >
    </template>

    <template #extra>
      <n-flex>
        <n-image :src="recipe.photo.large" :alt="recipe.name" height="300" />
        <n-list>
          <n-list-item>
            <template #prefix>Autorstvo:</template>{{ recipe.chef.name }}
          </n-list-item>
          <n-list-item>
            <template #prefix>Obtížnost:</template>{{ recipe.difficulty.name }}
          </n-list-item>
          <n-list-item>
            <template #prefix>Tagy:</template>
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
        <n-h2>Postup</n-h2>
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
        <n-h2>Tipy a triky</n-h2>
        <CollapseList :data="recipe.tips">
          <template #default="{ item }">
            {{ item.description }}
          </template>
        </CollapseList>
      </n-grid-item>
      <n-grid-item>
        <n-h2>Komentáře</n-h2>
        <CollapseList :data="recipe.comments" />
      </n-grid-item>
      <n-grid-item span="2">
        <n-h2>Zdroje</n-h2>
        <n-text>{{ recipe.sources }}</n-text>
      </n-grid-item>
    </n-grid>
  </AppPage>
</template>

<style scoped></style>
