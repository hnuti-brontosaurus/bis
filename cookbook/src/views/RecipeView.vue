<script setup>
import {
  NAlert,
  NFlex,
  NTag,
  NText,
  NButton,
  NSwitch,
  NImage,
  NH1,
  NH2,
  useDialog,
} from "naive-ui"
import { faPen, faTrash } from "@fortawesome/free-solid-svg-icons"
import { icon } from "@/contrib/composables/render.js"
import { computed, onMounted, onUnmounted, watch } from "vue"
import { useRoute, useRouter } from "vue-router"
import { storeToRefs } from "pinia"
import { useWakeLock } from "@vueuse/core"
import { useRecipesStore, useRecipe } from "@/data/recipes.js"
import { useChefsStore } from "@/data/chefs.js"
import { useRecipeDifficultiesStore } from "@/data/recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "@/data/recipeRequiredTimes.js"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { useAllergensStore } from "@/data/allergens.js"
import { useAuthStore } from "@/data/auth.js"
import { handleAxiosError } from "@/contrib/composables/setup.js"
import RecipeIngredients from "@/components/recipe/RecipeIngredients.vue"
import CollapseList from "@/contrib/components/CollapseList.vue"
import AppPage from "@/components/app/AppPage.vue"
import LinkifiedText from "@/components/app/LinkifiedText.vue"
import WithHint from "@/contrib/components/WithHint.vue"
import { _ } from "@/composables/translations.js"

const route = useRoute()
const router = useRouter()
const dialog = useDialog()
const recipesStore = useRecipesStore()
const { isEditor, chefId } = storeToRefs(useAuthStore())

useChefsStore().fetchAll()
useRecipeDifficultiesStore().fetchAll()
useRecipeRequiredTimesStore().fetchAll()
useRecipeTagsStore().fetchAll()
useIngredientsStore().fetchAll()
useUnitsStore().fetchAll()
useAllergensStore().fetchAll()

const ensureLoaded = id => recipesStore.fetchOne(id)
onMounted(() => ensureLoaded(route.params.id))
watch(() => route.params.id, ensureLoaded)

const recipeId = computed(() => route.params.id)
const recipe = useRecipe(recipeId)

const {
  isSupported: wakeLockSupported,
  isActive: cookMode,
  request,
  release,
} = useWakeLock()
const toggleCookMode = async value => {
  if (value) await request("screen")
  else await release()
}
onUnmounted(() => release())

// Mirrors the backend's _can_write rule for Recipe: editor can edit any
// recipe; a chef can edit only their own.
const canEdit = computed(() => {
  if (!recipe.value) return false
  return isEditor.value || (chefId.value && recipe.value.chef_id === chefId.value)
})

const togglePublic = async value => {
  try {
    await recipesStore.save({ id: recipe.value.id, is_public: value })
  } catch (e) {
    handleAxiosError(_.value.recipes.delete_error)(e)
  }
}

const facts = computed(() =>
  [
    [_.value.recipes.chef, recipe.value.chef],
    [_.value.recipes.required_time, recipe.value.required_time],
    [_.value.recipes.difficulty, recipe.value.difficulty],
  ].filter(([, item]) => item),
)

const onDelete = () => {
  dialog.warning({
    title: _.value.recipes.delete_title,
    content: _.value.recipes.delete_content,
    positiveText: _.value.recipes.delete,
    negativeText: _.value.common.back,
    onPositiveClick: async () => {
      try {
        await recipesStore.remove(recipe.value.id)
        router.push({ name: "recipes" })
      } catch (e) {
        handleAxiosError(_.value.recipes.delete_error)(e)
      }
    },
  })
}
</script>

<template>
  <AppPage v-if="recipe">
    <template v-if="canEdit" #actions>
      <n-switch :value="!!recipe.is_public" @update:value="togglePublic" :round="false">
        <template #checked>{{ _.recipes.is_public }}</template>
        <template #unchecked>{{ _.recipes.is_private }}</template>
      </n-switch>
      <n-button
        :render-icon="icon(faPen)"
        @click="$router.push({ name: 'edit_recipe', params: { id: recipe.id } })"
        >{{ _.recipes.edit }}</n-button
      >
      <n-button type="error" ghost :render-icon="icon(faTrash)" @click="onDelete">{{
        _.recipes.delete
      }}</n-button>
    </template>
    <div class="hero" :class="{ 'with-photo': recipe.photo }">
      <n-image
        v-if="recipe.photo"
        class="hero-photo"
        :src="recipe.photo.large"
        :alt="recipe.name"
        object-fit="cover"
      />
      <div class="hero-text">
        <n-flex v-if="recipe.tags.length" :size="6">
          <n-tag v-for="tag in recipe.tags" :key="tag.id" size="small">{{
            tag.name
          }}</n-tag>
        </n-flex>
        <n-h1>{{ recipe.name }}</n-h1>
        <n-text v-if="recipe.intro" depth="3" class="prose">
          <LinkifiedText :text="recipe.intro" />
        </n-text>
        <div class="facts">
          <div v-for="[label, item] in facts" :key="label" class="fact">
            <div class="fact-label">{{ label }}</div>
            <div class="fact-value">{{ item.name }}</div>
          </div>
        </div>
      </div>
    </div>

    <n-alert
      v-if="recipe.allergens.length"
      type="warning"
      :title="
        _.recipes.allergen_warning + ': ' + recipe.allergens.map(a => a.name).join(', ')
      "
    />

    <div class="columns">
      <section class="panel">
        <RecipeIngredients :recipe="recipe"></RecipeIngredients>
      </section>
      <section class="panel">
        <n-flex justify="space-between" align="center" :wrap="false">
          <n-h2>{{ _.recipes.steps }}</n-h2>
          <WithHint
            v-if="wakeLockSupported"
            :hint="_.recipes.cook_mode_hint"
            :width="220"
          >
            <n-switch :value="cookMode" @update:value="toggleCookMode" :round="false">
              <template #checked>{{ _.recipes.cook_mode }}</template>
              <template #unchecked>{{ _.recipes.cook_mode }}</template>
            </n-switch>
          </WithHint>
        </n-flex>
        <n-text v-if="recipe.difficulty_note" depth="3" class="prose difficulty-note">
          <LinkifiedText :text="recipe.difficulty_note" />
        </n-text>
        <CollapseList :data="recipe.steps" checked-key="done" class="steps">
          <template #header="{ item, i }">
            <span class="step-number display-font" :class="{ done: item.done }">{{
              i + 1
            }}</span>
            <em v-if="item.is_optional" :class="{ muted: item.done }">{{
              item.name
            }}</em>
            <span v-else :class="{ muted: item.done }">{{ item.name }}</span>
          </template>
          <template #default="{ item }">
            <n-flex v-if="item.description || item.photo">
              <n-text v-if="item.description"
                ><LinkifiedText :text="item.description"
              /></n-text>
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
      </section>
    </div>

    <section v-if="recipe.tips.length">
      <n-h2>{{ _.recipes.tips }}</n-h2>
      <CollapseList :data="recipe.tips" class="tips">
        <template #default="{ item }">
          <LinkifiedText :text="item.description" />
        </template>
      </CollapseList>
    </section>
    <section v-if="recipe.comments.length">
      <n-h2>{{ _.recipes.comments }}</n-h2>
      <CollapseList :data="recipe.comments" />
    </section>
    <section v-if="recipe.sources">
      <n-h2>{{ _.recipes.sources }}</n-h2>
      <n-text class="prose"><LinkifiedText :text="recipe.sources" /></n-text>
    </section>
  </AppPage>
</template>

<style scoped>
.hero {
  display: grid;
  gap: 28px;
  align-items: center;
}

.hero-photo {
  aspect-ratio: 4 / 3;
  border: 1px solid var(--line);
  border-radius: 4px;
}

.hero-photo :deep(img) {
  width: 100%;
  height: 100%;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 0;
}

.hero-text .n-h1 {
  margin: 0;
}

.difficulty-note {
  display: block;
  margin-bottom: 8px;
}

.prose {
  max-width: 66ch;
}

.facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.fact {
  padding: 4px 12px;
  border-left: 2px solid var(--primary);
}

.fact-label {
  color: var(--muted);
  font-size: 0.74em;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.fact-value {
  font-weight: 600;
}

.step-number {
  display: inline-grid;
  flex: none;
  place-items: center;
  width: 30px;
  height: 30px;
  margin-right: 12px;
  border-radius: 3px;
  background: var(--primary-soft);
  color: var(--primary-text);
}

.step-number.done {
  background: var(--primary);
  color: var(--primary-ink);
}

.tips :deep(.n-collapse-item) {
  max-width: 66ch;
  margin: 12px 0 0;
  padding: 10px 14px;
  border: 0;
  border-left: 4px solid var(--accent);
  border-radius: 0 3px 3px 0;
  background: var(--accent-soft);
}

.tips :deep(.n-collapse-item__header) {
  padding: 0;
}

@media (min-width: 720px) {
  .hero.with-photo {
    grid-template-columns: minmax(0, 5fr) minmax(0, 6fr);
  }
}
</style>
