import { createRouter, createWebHistory } from "vue-router"
import { useAuthStore } from "@/data/auth.js"

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
      path: "/me/",
      name: "me",
      meta: { back: { name: "home" } },
      component: () => import("@/views/MeView.vue"),
    },
    {
      path: "/recipes/",
      name: "recipes",
      meta: { back: { name: "home" } },
      component: () => import("@/views/RecipesView.vue"),
    },
    {
      path: "/recipe/:id/",
      name: "recipe",
      meta: { back: { name: "recipes" } },
      component: () => import("@/views/RecipeView.vue"),
    },
    {
      path: "/recipe/:id/edit/",
      name: "edit_recipe",
      meta: {
        requiresAuth: true,
        back: route => ({ name: "recipe", params: { id: route.params.id } }),
      },
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/recipe/create/",
      name: "create_recipe",
      meta: { requiresAuth: true, back: { name: "recipes" } },
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/menus/",
      name: "menus",
      meta: { back: { name: "home" } },
      component: () => import("@/views/TodoView.vue"),
    },
    {
      path: "/chefs/",
      name: "chefs",
      meta: { back: { name: "home" } },
      component: () => import("@/views/ChefsView.vue"),
    },
    {
      path: "/ingredients/",
      name: "ingredients",
      meta: { back: { name: "home" } },
      component: () => import("@/views/IngredientsView.vue"),
    },
    {
      path: "/ingredient/:id/edit/",
      name: "edit_ingredient",
      meta: { requiresAuth: true, back: { name: "ingredients" } },
      component: () => import("@/views/EditIngredientView.vue"),
    },
    {
      path: "/ingredient/create/",
      name: "create_ingredient",
      meta: { requiresAuth: true, back: { name: "ingredients" } },
      component: () => import("@/views/EditIngredientView.vue"),
    },
  ],
})

router.beforeEach(to => {
  if (to.meta.requiresAuth && !useAuthStore().isChef) {
    return { name: "me", query: { next: to.fullPath } }
  }
})

export default router
