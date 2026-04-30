<script setup>
import {
  NFlex,
  NButtonGroup,
  NPageHeader,
  NButton,
  NGrid,
  NGridItem,
  NCard,
} from "naive-ui"
import { computed, onMounted } from "vue"
import { useRouter } from "vue-router"
import { useRecipesStore } from "@/data/recipes.js"
import { useChefsStore } from "@/data/chefs.js"
import { _ } from "@/composables/translations.js"

const recipesStore = useRecipesStore()
const chefsStore = useChefsStore()
onMounted(() => {
  recipesStore.fetchAll()
  chefsStore.fetchAll()
})

const router = useRouter()

const onClick = id => router.push({ name: "recipe", params: { id } })

const chefNameFor = chef_id => computed(() => chefsStore.byId[chef_id]?.name ?? "")
</script>

<template>
  <n-flex vertical>
    <n-page-header :title="_.Recipe.plural">
      <template #extra>
        <n-button-group>
          <n-button @click="router.push({ name: 'create_recipe' })">{{
            _.recipes.create
          }}</n-button>
          <n-button>{{ _.common.filters }}</n-button>
        </n-button-group>
      </template>
    </n-page-header>

    <n-grid cols="1 s:2 m:3" x-gap="32" y-gap="32" responsive="screen">
      <n-grid-item v-for="recipe in recipesStore.list" :key="recipe.id">
        <router-link :to="{ name: 'recipe', params: { id: recipe.id } }" custom>
          <n-card
            :title="recipe.name"
            embedded
            hoverable
            style="cursor: pointer"
            @click="onClick(recipe.id)"
          >
            <template #cover>
              <img
                :src="recipe.photo.medium"
                :alt="recipe.name"
                style="object-fit: cover; height: 200px"
              />
            </template>
            {{ chefNameFor(recipe.chef_id).value }}
          </n-card>
        </router-link>
      </n-grid-item>
    </n-grid>
  </n-flex>
</template>

<style scoped></style>
