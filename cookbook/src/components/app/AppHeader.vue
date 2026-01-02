<script setup>
import {NButton, NButtonGroup, NDropdown, NFlex, NGrid, NGridItem, NImage, useThemeVars} from "naive-ui"
import {useRender} from "@/contrib/composables/render.js";
import {faUser} from "@fortawesome/free-regular-svg-icons";
import {faBars} from "@fortawesome/free-solid-svg-icons";
import {useRouter} from "vue-router";

const {icon} = useRender()
const router = useRouter()
const vars = useThemeVars()


const menuOptions = [
  {
    label: "Kuchařka",
    key: "cookbook",
    children: [
      {label: "Recepty", key: "recipes"},
      {label: "Jídleníčky", key: "menus"},
      {label: "Kuchařstvo", key: "chefs"},
      {label: "Ingredience", key: "ingredients"},
    ]
  },
  {
    label: "Proč vegan?",
    key: "vegan",
    children: [
      {label: "Manifest? :D", key: "manifest"},
      {label: "Jak začít", key: "how_to"},
      {label: "Zdravotní rizika", key: "risks"},
      {label: "Kam dál?", key: "where_to_go"},
    ]
  },
  {
    label: "Tipy a triky",
    key: "tips",
    children: [
      {label: "FAQ", key: "faq"},
      {label: "Vaření na Bronto akci", key: "bronto"},
      {label: "Jak na dumpsterdiving", key: "dumpsterdiving"},
      {label: "Zero waste", key: "zero_waste"},
    ]
  },
  {
    label: "Přidej se",
    key: "join_us"
  }
];

const userOptions = [
  {label: "Přihlášení", key: "login"},
  {label: "Registrace", key: "register"},
  {label: "Moje recepty", key: "my_recipes"},
  {label: "Moje nastevení", key: "settings"},

]

const select = (value) => {
  router.push({name: value})
}

</script>

<template>
  <n-flex :wrap="false" align="center" justify="center" style="position: relative; height: 100%; padding: 1rem">
    <router-link to="/" style="position: absolute; left: 1rem">
      <n-button quaternary>
        <template #icon>
          <n-image :height="vars.heightMedium" preview-disabled src="/cookbook/logo.png" style="justify-content: center; align-items: center"></n-image>
        </template>
      </n-button>
    </router-link>

    <n-grid cols="0 m:1" responsive="screen" style="width: unset">
      <n-grid-item span="0 m:1">
        <n-button-group>
          <n-dropdown v-for="item in menuOptions" :key="item.key" :options="item.children" @select="select">
            <n-button quaternary>{{ item.label }}</n-button>
          </n-dropdown>
        </n-button-group>
      </n-grid-item>
    </n-grid>


    <n-button-group style="position: absolute; right: 1rem">
      <n-dropdown :options="userOptions" placement="bottom-end">
        <n-button :render-icon="icon(faUser)" quaternary/>
      </n-dropdown>
      <n-dropdown :options="menuOptions" placement="bottom-end">
        <n-button :render-icon="icon(faBars)" quaternary/>
      </n-dropdown>
    </n-button-group>
  </n-flex>
</template>

<style scoped>
</style>
