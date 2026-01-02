<script setup>
import {NFlex, NH1, NText, NPageHeader, NButton, NGrid, NGridItem, NCard} from "naive-ui"
import {rand} from "@vueuse/core";
import {useConnector} from "@/composables/connector.js";

const {chefs, refresh} = useConnector("chefs");

</script>

<template>
  <n-flex vertical>
    <n-page-header title="Kuchařstvo"></n-page-header>

    <n-grid cols="1 s:2 m:3" x-gap="32" y-gap="32" responsive="screen">
      <n-grid-item v-for="(chef, id) in chefs" :key="id">
        <n-card :title="chef.name" embedded hoverable>
          <template #cover>
            <img :src="chef.photo.medium" :alt="chef.name" style="object-fit: cover; height: 200px"/>
          </template>
          {{ chef.name }}
        </n-card>
      </n-grid-item>
    </n-grid>
  </n-flex>
</template>

<style scoped></style>
