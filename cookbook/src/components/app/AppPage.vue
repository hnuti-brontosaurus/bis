<script setup>
import { NButton, NH1, NFlex, useMessage, NButtonGroup } from "naive-ui"
import { useRender } from "@/contrib/composables/render.js"
import {faChevronLeft, faGear} from "@fortawesome/free-solid-svg-icons"
import { useAppSettings } from "@/composables/app_settings.js"

const { icon } = useRender()
const { settings } = useAppSettings()
const message = useMessage()

defineProps(["title"])

</script>

<template>
  <n-flex vertical>
    <n-flex justify="space-between" align="start">
      <n-flex :wrap="false"  align="baseline">
        <n-button :render-icon="icon(faChevronLeft)" quaternary @click="$router.back"/>
        <n-h1>{{ title }}</n-h1>
      </n-flex>
      <n-button-group style="margin-left: auto">
        <slot name="actions"/>
      </n-button-group>
    </n-flex>
    <n-flex>
      <slot name="extra"/>
    </n-flex>
    <slot/>
  </n-flex>
</template>

<style scoped></style>
