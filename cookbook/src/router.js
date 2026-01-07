import { createRouter, createWebHistory } from "vue-router"

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
      component: () => import("@/views/EditRecipeView.vue"),
    },
    {
      path: "/recipe/create/",
      name: "create_recipe",
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

export default router
