<script setup>
import { computed } from "vue"
import { useRouter } from "vue-router"
import { NButton, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import { linkRoute } from "@/data/manage.js"

const props = defineProps({
  token: { type: String, required: true },
  areaName: { type: String, required: true },
})

const message = useMessage()
const router = useRouter()
const url = computed(
  () =>
    window.location.origin +
    router.resolve(linkRoute(props.token, props.areaName)).href,
)

const copy = async () => {
  await navigator.clipboard.writeText(url.value)
  message.success("Odkaz je zkopírovaný, pošli ho dobrovolníkům.")
}
</script>

<template>
  <n-button size="small" data-testid="batch-link" :data-url="url" @click="copy">
    <template #icon><AppIcon name="link" /></template>
    Odkaz pro dobrovolníky
  </n-button>
</template>
