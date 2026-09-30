<script setup>
import { NButton, NDropdown } from "naive-ui"
import { useRender } from "@/contrib/composables/render.js"
import { faUser } from "@fortawesome/free-regular-svg-icons"
import { faBars, faCartShopping, faMoon } from "@fortawesome/free-solid-svg-icons"
import { useRoute, useRouter } from "vue-router"
import { settings, useDarkTheme } from "@/composables/settings.js"
import { _, translatedKey } from "@/composables/translations.js"
import { useAuthStore } from "@/data/auth.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { useCartSummed } from "@/composables/cartSummed.js"
import { NBadge } from "naive-ui"
import { computed } from "vue"
import { storeToRefs } from "pinia"

const { icon } = useRender()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const { isChef, isAuthenticated } = storeToRefs(authStore)

const translatedMenuKey = translatedKey("menu")

// Font Awesome's solid sun reads as a cog at header size, so the rays are
// drawn as separate strokes here.
const faSun = {
  prefix: "fas",
  iconName: "sun-rays",
  icon: [
    24,
    24,
    [],
    "",
    "M12 7.5a4.5 4.5 0 1 0 0 9 4.5 4.5 0 0 0 0-9zM11 1h2v4h-2zM11 19h2v4h-2zM1 11h4v2H1zM19 11h4v2h-4zM4.22 5.64l1.42-1.42 2.83 2.83-1.42 1.42zM18.36 4.22l1.42 1.42-2.83 2.83-1.42-1.42zM4.22 18.36l2.83-2.83 1.42 1.42-2.83 2.83zM19.78 18.36l-1.42 1.42-2.83-2.83 1.42-1.42z",
  ],
}

const menuOptions = computed(() => [
  {
    ...translatedMenuKey("cookbook"),
    children: [
      translatedMenuKey("recipes"),
      translatedMenuKey("menus"),
      translatedMenuKey("chefs"),
      translatedMenuKey("ingredients"),
    ],
  },
  {
    ...translatedMenuKey("vegan"),
    children: [
      translatedMenuKey("manifest"),
      translatedMenuKey("how_to"),
      translatedMenuKey("risks"),
      translatedMenuKey("where_to_go"),
    ],
  },
  {
    ...translatedMenuKey("tips"),
    children: [
      translatedMenuKey("faq"),
      translatedMenuKey("bronto"),
      translatedMenuKey("dumpster_diving"),
      translatedMenuKey("zero_waste"),
    ],
  },
  {
    ...translatedMenuKey("join_us"),
  },
])

const userOptions = computed(() => {
  if (isChef.value)
    return [
      translatedMenuKey("my_recipes"),
      translatedMenuKey("settings"),
      translatedMenuKey("logout"),
    ]
  if (isAuthenticated.value)
    return [translatedMenuKey("create_profile"), translatedMenuKey("logout")]

  return [translatedMenuKey("login"), translatedMenuKey("register")]
})

// Ingredients + units back the summed-cart computation. They're cheap to
// fetch and cached in their stores; loading them in the header guarantees
// the badge has data on first paint instead of waiting for a route mount.
useIngredientsStore().fetchAll()
useUnitsStore().fetchAll()
const { unboughtCount } = useCartSummed()

const isActive = item => item.children?.some(child => child.key === route.name)

const toggleDarkTheme = () => {
  settings.value.darkTheme = !useDarkTheme.value
}

const select = value => {
  if (value === "logout") {
    authStore.logout()
    router.go(0)
    return
  }
  if (["login", "register", "create_profile", "settings"].includes(value)) value = "me"
  router.push({ name: value })
}
</script>

<template>
  <header class="header">
    <router-link to="/" class="brand display-font">
      <img src="/cookbook/logo.png" alt="" />
      {{ _.common.cookbook }}
    </router-link>

    <nav class="navigation">
      <n-dropdown
        v-for="item in menuOptions"
        :key="item.key"
        :options="item.children"
        @select="select"
      >
        <n-button
          quaternary
          class="navigation-link"
          :class="{ active: isActive(item) }"
          >{{ item.label }}</n-button
        >
      </n-dropdown>
    </nav>

    <div class="tools">
      <n-badge
        :value="unboughtCount"
        :show="unboughtCount > 0"
        :max="99"
        :offset="[-6, 6]"
      >
        <n-button
          :render-icon="icon(faCartShopping)"
          quaternary
          @click="router.push({ name: 'cart' })"
        />
      </n-badge>
      <n-dropdown :options="userOptions" placement="bottom-end" @select="select">
        <n-button :render-icon="icon(faUser)" quaternary />
      </n-dropdown>
      <n-button
        :render-icon="icon(useDarkTheme ? faSun : faMoon)"
        :title="_.profile.dark_theme"
        :aria-label="_.profile.dark_theme"
        :aria-pressed="useDarkTheme"
        quaternary
        @click="toggleDarkTheme"
      />
      <n-dropdown :options="menuOptions" placement="bottom-end" @select="select">
        <n-button class="menu-button" :render-icon="icon(faBars)" quaternary />
      </n-dropdown>
    </div>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  gap: 18px;
  max-width: 1120px;
  height: 100%;
  margin: 0 auto;
  padding: 0 20px;
}

.brand {
  display: flex;
  flex: 1;
  align-items: center;
  gap: 10px;
  color: var(--text);
  font-size: 1.3rem;
  text-decoration: none;
  white-space: nowrap;
}

.brand img {
  height: 40px;
}

.navigation {
  display: none;
  align-self: stretch;
  gap: 2px;
}

.navigation-link {
  height: 100%;
  border-radius: 0;
  color: var(--muted);
}

.navigation-link.active {
  color: var(--primary-text);
  box-shadow: inset 0 -2px 0 var(--primary-text);
}

.tools {
  display: flex;
  flex: 1;
  align-items: center;
  justify-content: flex-end;
  gap: 6px;
}

@media (min-width: 800px) {
  .navigation {
    display: flex;
  }

  .menu-button {
    display: none;
  }
}
</style>
