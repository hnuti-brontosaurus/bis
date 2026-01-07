import { createRouter, createWebHistory } from "vue-router"
import { me } from "@/composables/auth.js"

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
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
      component: () => import("@/views/TodoView.vue"),
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !me.value?.is_chef) {
    return { name: "me", query: { next: to.fullPath } }
  }
})

export default router
