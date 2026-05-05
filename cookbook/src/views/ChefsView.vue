<script setup>
import { NFlex, NPageHeader, NGrid, NGridItem, NCard } from "naive-ui"
import { onMounted } from "vue"
import { useChefsStore } from "@/data/chefs.js"
import { _ } from "@/composables/translations.js"

const chefsStore = useChefsStore()
onMounted(() => chefsStore.fetchAll())
</script>

<template>
  <n-flex vertical>
    <n-page-header :title="_.chefs.title"></n-page-header>

    <n-grid cols="1 s:2 m:3" x-gap="32" y-gap="32" responsive="screen">
      <n-grid-item v-for="chef in chefsStore.list" :key="chef.id">
        <n-card :title="chef.name" embedded hoverable>
          <template #cover>
            <img
              :src="chef.photo.medium"
              :alt="chef.name"
              style="object-fit: cover; height: 200px"
            />
          </template>
          {{ chef.name }}
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-flex>
</template>

<style scoped></style>
