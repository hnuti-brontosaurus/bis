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
    path: "/statistiky/",
    name: "statistics",
    component: () => import("@/views/StatisticsView.vue"),
  },
  {
    path: "/chci-vyvesit/",
    name: "want_to_hang",
    component: () => import("@/views/WantToHangView.vue"),
  },
  {
    path: "/napoveda/",
    name: "help",
    component: () => import("@/views/HelpView.vue"),
  },
  {
    path: "/napoveda/:slug/",
    name: "help_article",
    component: () => import("@/views/HelpView.vue"),
  },
  {
    path: "/oblast/:id/",
    name: "area",
    meta: { map: true, requiresLogin: true },
    component: () => import("@/views/AreaView.vue"),
  },
  {
    path: "/oblast/:id/tisk/",
    name: "area_print",
    meta: { requiresLogin: true },
    component: () => import("@/views/AreaPrintView.vue"),
  },
  {
    path: "/budka/:id/",
    name: "box",
    meta: { requiresLogin: true },
    component: () => import("@/views/BoxView.vue"),
  },
  {
    path: "/budka/:id/kontrola/",
    name: "check",
    meta: { requiresLogin: true },
    component: () => import("@/views/CheckView.vue"),
  },
  {
    path: "/obchuzka/:id/",
    name: "batch",
    meta: { requiresLogin: true },
    component: () => import("@/views/BatchView.vue"),
  },
  {
    path: "/obchuzky/",
    name: "open_batches",
    meta: { requiresLogin: true },
    component: () => import("@/views/OpenBatchesView.vue"),
  },
  {
    // The optional slug is the area's name, see linkRoute
    path: "/d/:slug?/:token([0-9a-f-]{36})/",
    meta: { volunteer: true },
    component: () => import("@/views/link/LinkView.vue"),
    children: [
      {
        path: "",
        name: "link",
        meta: { map: true },
        component: () => import("@/views/link/LinkAreaView.vue"),
      },
      {
        path: "budka/:boxId/",
        name: "link_check",
        component: () => import("@/views/link/LinkCheckView.vue"),
      },
      {
        path: "nova-budka/",
        name: "link_new_box",
        component: () => import("@/views/link/LinkNewBoxView.vue"),
      },
      {
        path: "napoveda/:slug?/",
        name: "link_help",
        component: () => import("@/views/link/LinkHelpView.vue"),
      },
    ],
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
