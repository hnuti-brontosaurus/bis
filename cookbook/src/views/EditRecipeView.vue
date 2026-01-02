<script setup>
import {
  NFlex,
  NH1,
  NForm,
  NFormItem,
  NTag,
  NList,
  NText,
  NSelect,
  NPageHeader,
  NButton,
  NListItem,
  NButtonGroup,
  NCard,
  NInput,
  NInputGroup,
  NImage,
  NH2,
  NGridItem,
  NGrid,
  NInputNumber,
  NDataTable,
  useThemeVars,
} from "naive-ui"
import {rand} from "@vueuse/core";
import {useConnector} from "@/composables/connector.js";
import {useRoute} from "vue-router";
import {computed, onMounted, ref} from "vue";
import RecipeIngrediences from "@/components/recipe/RecipeIngrediences.vue";
import RecipeSteps from "@/components/recipe/RecipeSteps.vue";
import {useServings} from "@/composables/servings.js";
import CollapseList from "@/contrib/components/CollapseList.vue";
import {useRender} from "@/contrib/composables/render.js";
import {faCartPlus} from "@fortawesome/free-solid-svg-icons";
import AppPage from "@/components/app/AppPage.vue";
import {useHelpers} from "@/contrib/composables/helpers.js";

const route = useRoute();
const {icon} = useRender()
const {mapping} = useHelpers()

const {recipes, refresh} = useConnector("recipes");
const {recipe_difficulties} = useConnector("recipe_difficulties");
const {chefs} = useConnector("chefs")

const recipe_id = route.params.id
onMounted(() => recipe_id ? refresh(recipe_id) : null)

const recipe = recipe_id ? computed(() => recipes.value[recipe_id]) : ref({})

const getIngredientTitle = (ingredient) => `${ingredient.amount * servings.count.value} ${ingredient.unit.name} ${ingredient.ingredient.name}`

const servings = useServings()
const vars = useThemeVars()

const authors = computed(() => Object.values(chefs.value).map(chef => ({label: chef.name, value: chef.id})))
const difficulties = computed(() => Object.values(recipe_difficulties.value).map(_ => ({label: _.name, value: _.id})))

const chefId = mapping(
  () => recipe.value.chef?.id,
  value => recipe.value.chef = chefs.value[value]
)

const difficultyId = mapping(
  () => recipe.value.difficulty?.id,
  value => recipe.value.difficulty = recipe_difficulties.value[value]
)

</script>

<template>
  <AppPage :title="recipe_id ? 'Úprava receptu' : 'Nový recept'">
    <n-form>
      <n-form-item label="Název">
        <n-input v-model:value="recipe.name"/>
      </n-form-item>
      <n-form-item label="Autor">
        <n-select :options="authors" v-model:value="chefId">

        </n-select>
      </n-form-item>
      <n-form-item label="Obtížnost">
        <n-select :options="difficulties" v-model:value="difficultyId">

        </n-select>
      </n-form-item>


    </n-form>

    {{ recipe }}

    name
    chef
    difficulty
    tags
    photo
    intro
    sources
    ingredients
    steps
    tips
    comments
    is_public
<!--    <template #actions>-->
<!--      <n-button>upravit</n-button>-->
<!--    </template>-->

<!--    <template #extra>-->
<!--      <n-flex>-->
<!--        <n-image :src="recipe.photo.large" :alt="recipe.name" height="300"/>-->
<!--        <n-list>-->
<!--          <n-list-item>-->
<!--            <template #prefix>Autorstvo:</template>{{recipe.chef.name}}-->
<!--          </n-list-item>-->
<!--          <n-list-item>-->
<!--            <template #prefix>Obtížnost:</template>{{recipe.difficulty.name}}-->
<!--          </n-list-item>-->
<!--          <n-list-item>-->
<!--            <template #prefix>Tagy:</template>-->
<!--            <n-tag v-for="tag in recipe.tags" :key="id" round>-->
<!--              {{tag.name}}-->
<!--            </n-tag>-->
<!--          </n-list-item>-->
<!--        </n-list>-->
<!--      </n-flex>-->
<!--    </template>-->

<!--    <n-text v-if="recipe.intro">-->
<!--      {{ recipe.intro }}-->
<!--    </n-text>-->

<!--    <n-grid cols="1 m:2" responsive="screen" x-gap="32" y-gap="32">-->
<!--      <n-grid-item>-->
<!--        <n-flex align="end" justify="space-between" :style="{'margin-bottom': '30px'}">-->
<!--          <n-h2 style="margin-bottom: 0">Ingredience</n-h2>-->
<!--          <n-flex align="baseline" :wrap="false">-->
<!--            <n-text>Porcí:</n-text>-->
<!--            <n-input-group>-->
<!--              <n-input-number size="small" style="width: 110px" v-model:value="servings.count.value" min="1"-->
<!--                              :precision="0"/>-->
<!--              <n-button :render-icon="icon(faCartPlus)" size="small"></n-button>-->
<!--            </n-input-group>-->
<!--          </n-flex>-->

<!--        </n-flex>-->
<!--        <CollapseList :data="recipe.ingredients" checked-key="is_required">-->
<!--          <template #header="{item, i}">-->
<!--            {{ item.amount * servings.count.value }} {{ item.unit.name }} {{ item.ingredient.name }}-->
<!--          </template>-->
<!--          <template #default="{item}">-->
<!--            <n-text v-if="item.comment">{{ item.comment }}</n-text>-->
<!--          </template>-->
<!--        </CollapseList>-->
<!--      </n-grid-item>-->
<!--      <n-grid-item>-->
<!--        <n-h2>Postup</n-h2>-->
<!--        <CollapseList :data="recipe.steps" checked-key="done">-->
<!--          <template #header="{item, i}">-->
<!--            {{ i + 1 }}. {{ item.name }}-->
<!--          </template>-->
<!--          <template #default="{item}">-->
<!--            <n-flex v-if="item.description || item.photo">-->
<!--              <n-text v-if="item.description">{{ item.description }}</n-text>-->
<!--              <n-image v-if="item.photo" :preview-src="item.photo.large" :src="item.photo.medium" style="width: 100%"-->
<!--                       width="100%"></n-image>-->
<!--            </n-flex>-->

<!--          </template>-->
<!--        </CollapseList>-->
<!--      </n-grid-item>-->
<!--      <n-grid-item v-if="recipe.tips.length">-->
<!--        <n-h2>Tipy a triky</n-h2>-->
<!--        <CollapseList :data="recipe.tips">-->
<!--          <template #default="{item}">-->
<!--            {{ item.description }}-->
<!--          </template>-->
<!--        </CollapseList>-->
<!--      </n-grid-item>-->
<!--      <n-grid-item v-if="recipe.comments.length">-->
<!--        <n-h2>Komentáře</n-h2>-->
<!--        <CollapseList :data="recipe.comments"/>-->
<!--      </n-grid-item>-->
<!--      <n-grid-item span="2">-->
<!--        <n-h2>Zdroje</n-h2>-->
<!--        <n-text>{{ recipe.sources }}</n-text>-->
<!--      </n-grid-item>-->
<!--    </n-grid>-->

  </AppPage>
</template>

<style scoped></style>
