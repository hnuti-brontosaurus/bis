<script setup>
import { computed } from "vue"
import { NButton, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import { linkUrl } from "@/data/manage.js"

const props = defineProps({ token: { type: String, required: true } })

const message = useMessage()
const url = computed(() => linkUrl(props.token))

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
