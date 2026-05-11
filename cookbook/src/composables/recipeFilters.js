import { computed } from "vue"
import { useLocalStorage } from "@vueuse/core"
import { useRecipesStore } from "@/data/recipes.js"
import { useChefsStore } from "@/data/chefs.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useRecipeTagsStore } from "@/data/recipeTags.js"
import { useAllergensStore } from "@/data/allergens.js"
import { useRecipeDifficultiesStore } from "@/data/recipeDifficulties.js"
import { useRecipeRequiredTimesStore } from "@/data/recipeRequiredTimes.js"

export const SORT_OPTIONS = ["newest", "oldest", "name_asc", "name_desc"]

const DEFAULT_FILTERS = () => ({
  search: "",
  sort: "newest",
  chef_ids: [],
  difficulty_ids: [],
  required_time_ids: [],
  tag_ids_include: [],
  tag_ids_exclude: [],
  allergen_ids_exclude: [],
  ingredient_ids_include: [],
  ingredient_ids_exclude: [],
  visibility: "all",
})

const STORAGE_KEY = "cookbook:recipeFilters:v1"

const filtersState = useLocalStorage(STORAGE_KEY, DEFAULT_FILTERS(), {
  mergeDefaults: true,
})

export const useRecipeFilters = () => {
  const recipesStore = useRecipesStore()
  const chefsStore = useChefsStore()
  const ingredientsStore = useIngredientsStore()

  const reset = () => {
    filtersState.value = DEFAULT_FILTERS()
  }

  const isActive = computed(() => {
    const f = filtersState.value
    return (
      !!f.search.trim() ||
      f.chef_ids.length > 0 ||
      f.difficulty_ids.length > 0 ||
      f.required_time_ids.length > 0 ||
      f.tag_ids_include.length > 0 ||
      f.tag_ids_exclude.length > 0 ||
      f.allergen_ids_exclude.length > 0 ||
      f.ingredient_ids_include.length > 0 ||
      f.ingredient_ids_exclude.length > 0 ||
      f.visibility !== "all"
    )
  })

  const tokenize = query =>
    query
      .toLowerCase()
      .split(/\s+/)
      .map(t => t.trim())
      .filter(Boolean)

  const matchesAll = (tokens, haystack) =>
    tokens.every(token => haystack.includes(token))

  // Score a recipe against the fulltext search; lower = better match.
  // 1 = name, 2 = intro/sources/ingredient names, 3 = nested text, 0 = no match.
  const searchScore = (recipe, tokens) => {
    if (!tokens.length) return 1

    const tier1 = (recipe.name || "").toLowerCase()
    if (matchesAll(tokens, tier1)) return 1

    const ingredientNames = (recipe.ingredients ?? [])
      .map(ri => ingredientsStore.byId[ri.ingredient_id]?.name ?? "")
      .join(" ")
    const tier2 =
      `${recipe.intro || ""} ${recipe.sources || ""} ${ingredientNames}`.toLowerCase()
    if (matchesAll(tokens, tier2)) return 2

    const stepText = (recipe.steps ?? [])
      .map(s => `${s.name || ""} ${s.description || ""}`)
      .join(" ")
    const tipText = (recipe.tips ?? [])
      .map(t => `${t.name || ""} ${t.description || ""}`)
      .join(" ")
    const ingredientComments = (recipe.ingredients ?? [])
      .map(ri => ri.comment || "")
      .join(" ")
    const commentText = (recipe.comments ?? []).map(c => c.comment || "").join(" ")
    const tier3 =
      `${ingredientComments} ${stepText} ${tipText} ${commentText}`.toLowerCase()
    if (matchesAll(tokens, tier3)) return 3
    return 0
  }

  const filteredRecipes = computed(() => {
    const f = filtersState.value
    const includeIngredients = new Set(f.ingredient_ids_include)
    const excludeIngredients = new Set(f.ingredient_ids_exclude)
    const includeTags = new Set(f.tag_ids_include)
    const excludeTags = new Set(f.tag_ids_exclude)
    const excludeAllergens = new Set(f.allergen_ids_exclude)
    const chefSet = new Set(f.chef_ids)
    const diffSet = new Set(f.difficulty_ids)
    const timeSet = new Set(f.required_time_ids)

    const tokens = tokenize(f.search)
    const scored = []
    for (const recipe of recipesStore.list) {
      if (chefSet.size && !chefSet.has(recipe.chef_id)) continue
      if (diffSet.size && !diffSet.has(recipe.difficulty_id)) continue
      if (timeSet.size && !timeSet.has(recipe.required_time_id)) continue

      const tagIds = recipe.tag_ids ?? []
      if (includeTags.size && ![...includeTags].every(id => tagIds.includes(id)))
        continue
      if (excludeTags.size && tagIds.some(id => excludeTags.has(id))) continue

      const allergenIds = recipe.allergen_ids ?? []
      if (excludeAllergens.size && allergenIds.some(id => excludeAllergens.has(id)))
        continue

      const ingredientIds = (recipe.ingredients ?? []).map(ri => ri.ingredient_id)
      if (
        includeIngredients.size &&
        ![...includeIngredients].every(id => ingredientIds.includes(id))
      )
        continue
      if (
        excludeIngredients.size &&
        ingredientIds.some(id => excludeIngredients.has(id))
      )
        continue

      if (f.visibility === "public" && !recipe.is_public) continue
      if (f.visibility === "private" && recipe.is_public) continue

      const score = searchScore(recipe, tokens)
      if (!score) continue
      scored.push({ recipe, score })
    }

    const cmp = (() => {
      switch (f.sort) {
        case "oldest":
          return (a, b) => new Date(a.created_at ?? 0) - new Date(b.created_at ?? 0)
        case "name_asc":
          return (a, b) => a.name.localeCompare(b.name, "cs")
        case "name_desc":
          return (a, b) => b.name.localeCompare(a.name, "cs")
        case "newest":
        default:
          return (a, b) => new Date(b.created_at ?? 0) - new Date(a.created_at ?? 0)
      }
    })()

    scored.sort((a, b) => a.score - b.score || cmp(a.recipe, b.recipe))
    return scored.map(s => s.recipe)
  })

  const chefName = id => chefsStore.byId[id]?.name ?? `#${id}`

  return {
    filters: filtersState,
    reset,
    isActive,
    filteredRecipes,
    chefName,
  }
}

export const useRecipeFilterOptions = () => {
  const chefsStore = useChefsStore()
  const ingredientsStore = useIngredientsStore()
  const tagsStore = useRecipeTagsStore()
  const allergensStore = useAllergensStore()
  const difficultiesStore = useRecipeDifficultiesStore()
  const requiredTimesStore = useRecipeRequiredTimesStore()

  const toOptions = list =>
    [...list].map(item => ({ label: item.name, value: item.id }))

  const sortByName = list =>
    [...list].sort((a, b) => a.name.localeCompare(b.name, "cs"))

  return {
    chefOptions: computed(() => toOptions(sortByName(chefsStore.list))),
    ingredientOptions: computed(() => toOptions(sortByName(ingredientsStore.list))),
    tagOptions: computed(() => toOptions(sortByName(tagsStore.list))),
    allergenOptions: computed(() => toOptions(sortByName(allergensStore.list))),
    difficultyOptions: computed(() => toOptions(difficultiesStore.list)),
    requiredTimeOptions: computed(() => toOptions(requiredTimesStore.list)),
  }
}
