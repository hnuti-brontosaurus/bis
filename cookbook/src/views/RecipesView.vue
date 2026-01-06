<script setup>
import {
  NFlex,
  NH1,
  NText,
  NButtonGroup,
  NPageHeader,
  NButton,
  NGrid,
  NGridItem,
  NCard,
} from "naive-ui"
import { rand } from "@vueuse/core"
import { recipes, useConnector } from "@/composables/connector.js"
import { useRouter } from "vue-router"
import { onMounted } from "vue"
import { _ } from "@/composables/translations.js"

useConnector("recipes")

const router = useRouter()

const onClick = value => router.push({ name: "recipe", params: { id: value } })
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
      <n-grid-item v-for="(recipe, id) in recipes" :key="id">
        <router-link :to="{ name: 'recipe', params: { id } }" custom>
          <n-card
            :title="recipe.name"
            embedded
            hoverable
            style="cursor: pointer"
            @click="onClick(id)"
          >
            <template #cover>
              <img
                :src="recipe.photo.medium"
                :alt="recipe.name"
                style="object-fit: cover; height: 200px"
              />
            </template>
            {{ recipe.chef.name }}
          </n-card>
        </router-link>
      </n-grid-item>
    </n-grid>
  </n-flex>
</template>

<style scoped></style>
