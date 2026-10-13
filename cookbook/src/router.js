import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/data/auth.js"

// Article slugs (backend `Article.Slug`, also the menu keys) and their paths.
const articlePaths = {
  manifest: "manifest",
  how_to: "jak-zacit",
  risks: "zdravotni-rizika",
  where_to_go: "kam-dal",
  faq: "caste-dotazy",
  bronto: "vareni-na-akci",
  dumpster_diving: "dumpster-diving",
  zero_waste: "zero-waste",
  join_us: "pridej-se",
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
  routes: [
    {
      path: "/",
      name: "home",
      component: () => import("@/views/HomeView.vue"),
    },
    {
      path: "/ucet/",
      name: "me",
      meta: { back: { name: "home" } },
      component: () => import("@/views/MeView.vue"),
    },
    {
      path: "/recepty/",
      name: "recipes",
      meta: { back: { name: "home" } },
      component: () => import("@/views/RecipesView.vue"),
    },
    {
      path: "/recept/:id/",
      name: "recipe",
      meta: { back: { name: "recipes" } },
      component: () => import("@/views/RecipeView.vue"),
    },
    {
      path: "/recept/:id/upravit/",
      name: "edit_recipe",
      meta: {
        requiresAuth: true,
        back: route => ({ name: "recipe", params: { id: route.params.id } }),
      },
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/recept/vytvorit/",
      name: "create_recipe",
      meta: { requiresAuth: true, back: { name: "recipes" } },
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/jidelnicky/",
      name: "menus",
      meta: { back: { name: "home" } },
      component: () => import("@/views/TodoView.vue"),
    },
    {
      path: "/kucharstvo/",
      name: "chefs",
      meta: { back: { name: "home" } },
      component: () => import("@/views/ChefsView.vue"),
    },
    {
      path: "/prisady/",
      name: "ingredients",
      meta: { back: { name: "home" } },
      component: () => import("@/views/IngredientsView.vue"),
    },
    {
      path: "/kosik/",
      name: "cart",
      meta: { back: { name: "recipes" } },
      component: () => import("@/views/CartView.vue"),
    },
    {
      path: "/prisada/:id/upravit/",
      name: "edit_ingredient",
      meta: { requiresAuth: true, back: { name: "ingredients" } },
      component: () => import("@/views/EditIngredientView.vue"),
    },
    {
      path: "/prisada/vytvorit/",
      name: "create_ingredient",
      meta: { requiresAuth: true, back: { name: "ingredients" } },
      component: () => import("@/views/EditIngredientView.vue"),
    },
    ...Object.entries(articlePaths).map(([slug, path]) => ({
      path: `/${path}/`,
      name: slug,
      props: { slug },
      meta: { back: { name: "home" } },
      component: () => import("@/views/ArticleView.vue"),
    })),
  ],
})

router.beforeEach(to => {
  if (to.meta.requiresAuth && !useAuthStore().isChef) {
    return { name: "me", query: { next: to.fullPath } }
  }
})

// A tab opened before a deploy still asks for the previous build's chunks,
// which the new deploy no longer has, so load the target page afresh instead.
const missingChunkErrors = new WeakSet()
window.addEventListener("vite:preloadError", event =>
  missingChunkErrors.add(event.payload),
)

router.onError((error, to) => {
  if (missingChunkErrors.has(error))
    window.location.assign(router.resolve(to.fullPath).href)
})

export default router
