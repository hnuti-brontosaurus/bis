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
      component: () => import("@/views/MeView.vue"),
    },
    {
      path: "/recipes/",
      name: "recipes",
      component: () => import("@/views/RecipesView.vue"),
    },
    {
      path: "/recipe/:id/",
      name: "recipe",
      component: () => import("@/views/RecipeView.vue"),
    },
    {
      path: "/recipe/:id/edit/",
      name: "edit_recipe",
      meta: { requiresAuth: true },
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/recipe/create/",
      name: "create_recipe",
      meta: { requiresAuth: true },
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/menus/",
      name: "menus",
      component: () => import("@/views/TodoView.vue"),
    },
    {
      path: "/chefs/",
      name: "chefs",
      component: () => import("@/views/ChefsView.vue"),
    },
    {
      path: "/ingredients/",
      name: "ingredients",
      component: () => import("@/views/IngredientsView.vue"),
    },
    {
      path: "/ingredient/:id/edit/",
      name: "edit_ingredient",
      meta: { requiresAuth: true },
      component: () => import("@/views/EditIngredientView.vue"),
    },
    {
      path: "/ingredient/create/",
      name: "create_ingredient",
      meta: { requiresAuth: true },
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
