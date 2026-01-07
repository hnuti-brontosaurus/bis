<script setup>
import {
  NButton,
  NButtonGroup,
  NDropdown,
  NFlex,
  NGrid,
  NGridItem,
  NImage,
  useThemeVars,
} from "naive-ui"
import { useRender } from "@/contrib/composables/render.js"
import { faUser } from "@fortawesome/free-regular-svg-icons"
import { faBars } from "@fortawesome/free-solid-svg-icons"
import { useRouter } from "vue-router"
import { theme } from "@/composables/theme.js"
import { _, translatedKey } from "@/composables/translations.js"
import { me } from "@/composables/auth.js"
import { computed } from "vue"

const { icon } = useRender()
const router = useRouter()

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
  if (me.value.is_chef)
    return [
      translatedMenuKey("my_recipes"),
      translatedMenuKey("settings"),
      translatedMenuKey("logout"),
    ]
  if (me.value.is_authenticated)
    return [translatedMenuKey("create_profile"), translatedMenuKey("logout")]

  return [translatedMenuKey("login"), translatedMenuKey("register")]
})

const select = value => {
  if (value === "logout") {
    me.value = {}
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
