<script setup>
import { NTabs, NTabPane, NSwitch } from "naive-ui"
import { ref } from "vue"
import AppPage from "@/components/app/AppPage.vue"
import ShoppingList from "@/components/cart/ShoppingList.vue"
import EditCart from "@/components/cart/EditCart.vue"
import { useIngredientsStore } from "@/data/ingredients.js"
import { useUnitsStore } from "@/data/units.js"
import { _ } from "@/composables/translations.js"

useIngredientsStore().fetchAll()
useUnitsStore().fetchAll()

const activeTab = ref("shopping")
const focusedGroupId = ref(null)
const hideBought = ref(true)

const onJumpToEdit = groupId => {
  focusedGroupId.value = groupId
  activeTab.value = "edit"
}
</script>

<template>
  <AppPage :title="_.cart.title">
    <n-tabs v-model:value="activeTab" type="line">
      <n-tab-pane name="shopping" :tab="_.cart.shopping">
        <ShoppingList v-model:hide-bought="hideBought" @jump-to-edit="onJumpToEdit" />
      </n-tab-pane>
      <n-tab-pane name="edit" :tab="_.cart.edit">
        <EditCart v-model:focused-group-id="focusedGroupId" />
      </n-tab-pane>
      <template #suffix>
        <n-switch
          v-if="activeTab === 'shopping'"
          v-model:value="hideBought"
          :round="false"
        >
          <template #checked>{{ _.cart.hide_bought }}</template>
          <template #unchecked>{{ _.cart.hide_bought }}</template>
        </n-switch>
      </template>
    </n-tabs>
  </AppPage>
</template>
