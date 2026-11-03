import { createRouter, createWebHistory } from "vue-router"

import { loginUrl, useAuthStore } from "@/data/auth.js"

const placeholder = (title, extra = {}) => ({
  component: () => import("@/views/PlaceholderView.vue"),
  props: { title },
  ...extra,
})

export const routes = [
  {
    path: "/",
    name: "landing",
    component: () => import("@/views/LandingView.vue"),
  },
  {
    path: "/mapa/",
    name: "areas",
    meta: { map: true },
    component: () => import("@/views/AreasMapView.vue"),
  },
  {
    path: "/chci-vyvesit/",
    name: "want_to_hang",
    component: () => import("@/views/WantToHangView.vue"),
  },
  { path: "/napoveda/", name: "help", ...placeholder("Jak na budky") },
  { path: "/napoveda/:slug/", name: "help_article", ...placeholder("Nápověda") },
  {
    path: "/oblast/:id/",
    name: "area",
    ...placeholder("Oblast", { meta: { map: true, requiresLogin: true } }),
  },
  {
    path: "/budka/:id/",
    name: "box",
    ...placeholder("Budka", { meta: { requiresLogin: true } }),
  },
  {
    path: "/budka/:id/kontrola/",
    name: "check",
    ...placeholder("Kontrola budky", { meta: { requiresLogin: true } }),
  },
  {
    path: "/davka/:id/",
    name: "batch",
    ...placeholder("Dávka kontrol", { meta: { requiresLogin: true } }),
  },
  {
    path: "/davky/",
    name: "open_batches",
    ...placeholder("Otevřené dávky", { meta: { requiresLogin: true } }),
  },
  {
    path: "/d/:token/",
    name: "link",
    ...placeholder("Čištění budek", { meta: { map: true, volunteer: true } }),
  },
  {
    path: "/d/:token/budka/:boxId/",
    name: "link_check",
    ...placeholder("Kontrola budky", { meta: { volunteer: true } }),
  },
  {
    path: "/d/:token/nova-budka/",
    name: "link_new_box",
    ...placeholder("Nová budka", { meta: { volunteer: true } }),
  },
  {
    path: "/:path(.*)*",
    name: "not_found",
    ...placeholder("Stránka neexistuje"),
  },
]

export const requireLogin = async to => {
  if (!to.meta.requiresLogin) return
  const auth = useAuthStore()
  await auth.loaded
  if (auth.isAnonymous) {
    window.location.assign(loginUrl(to.fullPath))
    return false
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  scrollBehavior: (to, from, savedPosition) => savedPosition || { top: 0 },
  routes,
})

router.beforeEach(requireLogin)

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
