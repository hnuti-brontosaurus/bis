<script setup>
import {
  NButton,
  NButtonGroup,
  NDropdown,
  NFlex,
  NGrid,
  NGridItem,
  NImage,
} from "naive-ui"
import { useRender } from "@/contrib/composables/render.js"
import { faUser } from "@fortawesome/free-regular-svg-icons"
import { faBars, faCartShopping } from "@fortawesome/free-solid-svg-icons"
import { useRouter } from "vue-router"
import { theme } from "@/composables/theme.js"
import { translatedKey } from "@/composables/translations.js"
import { useAuthStore } from "@/data/auth.js"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { useCartSummed } from "@/composables/cartSummed.js"
import { NBadge } from "naive-ui"
import { computed } from "vue"
import { storeToRefs } from "pinia"

const { icon } = useRender()
const router = useRouter()
const authStore = useAuthStore()
const { isChef, isAuthenticated } = storeToRefs(authStore)

const translatedMenuKey = translatedKey("menu")

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
  <n-flex
    :wrap="false"
    align="center"
    justify="center"
    style="position: relative; height: 100%; padding: 1rem"
  >
    <router-link to="/" style="position: absolute; left: 1rem">
      <n-button quaternary>
        <template #icon>
          <n-image
            :height="theme.common.heightMedium"
            preview-disabled
            src="/cookbook/logo.png"
            style="justify-content: center; align-items: center"
          ></n-image>
        </template>
      </n-button>
    </router-link>

    <n-grid cols="0 m:1" responsive="screen" style="width: unset">
      <n-grid-item span="0 m:1">
        <n-button-group>
          <n-dropdown
            v-for="item in menuOptions"
            :key="item.key"
            :options="item.children"
            @select="select"
          >
            <n-button quaternary>{{ item.label }}</n-button>
          </n-dropdown>
        </n-button-group>
      </n-grid-item>
    </n-grid>

    <n-button-group style="position: absolute; right: 1rem">
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
      <n-dropdown :options="menuOptions" placement="bottom-end" @select="select">
        <n-button :render-icon="icon(faBars)" quaternary />
      </n-dropdown>
    </n-button-group>
  </n-flex>
</template>

<style scoped></style>
