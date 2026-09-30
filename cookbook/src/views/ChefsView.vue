<script setup>
import { NFlex, NPageHeader, NCard } from "naive-ui"
import { onMounted } from "vue"
import { useChefsStore } from "@/data/chefs.js"
import { _ } from "@/composables/translations.js"

const chefsStore = useChefsStore()
onMounted(() => chefsStore.fetchAll())
</script>

<template>
  <n-flex vertical :size="22">
    <n-page-header :title="_.chefs.title"></n-page-header>

    <div class="card-grid">
      <n-card
        v-for="chef in chefsStore.list"
        :key="chef.id"
        :title="chef.name"
        hoverable
      >
        <template #cover>
          <div class="card-cover">
            <img :src="chef.photo.medium" :alt="chef.name" />
          </div>
        </template>
      </n-card>
    </div>
  </n-flex>
</template>

<style scoped></style>
