<script setup>
import {NFlex, NH1, NText, NPageHeader, NButton, NGrid, NGridItem, NCard} from "naive-ui"
import {rand} from "@vueuse/core";
import {useConnector} from "@/composables/connector.js";
import {useRouter} from "vue-router";
import {onMounted} from "vue";

const {recipes, fetch} = useConnector("recipes");
const router = useRouter()

onMounted(fetch)

const onClick = value => router.push({name: 'recipe', params: {id: value}})

</script>

<template>
  <n-flex vertical>
    <n-page-header title="Recepty">
      <template #extra>
      <n-flex>
        <n-button>Filtry</n-button>
      </n-flex>
    </template>
    </n-page-header>

    <n-grid cols="1 s:2 m:3" x-gap="32" y-gap="32" responsive="screen">
      <n-grid-item v-for="(recipe, id) in recipes" :key="id">
        <router-link :to="{name: 'recipe', params: {id}}" custom>
        <n-card :title="recipe.name" embedded hoverable style="cursor: pointer" @click="onClick(id)">
          <template #cover>
            <img :src="recipe.photo.medium" :alt="recipe.name" style="object-fit: cover; height: 200px"/>
          </template>
          {{ recipe.chef.name }}
        </n-card>
          </router-link>
      </n-grid-item>
    </n-grid>
  </n-flex>
</template>

<style scoped></style>
