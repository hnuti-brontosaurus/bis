<script setup>
import { NModal, NCard, NFlex, NText, NButton } from "naive-ui"
import { computed } from "vue"
import { storeToRefs } from "pinia"
import { useCartStore } from "@/data/cart.js"
import { _ } from "@/composables/translations.js"

const cartStore = useCartStore()
const { conflict } = storeToRefs(cartStore)

const counts = computed(() =>
  conflict.value
    ? {
        local: conflict.value.local.length,
        server: conflict.value.server.length,
      }
    : { local: 0, server: 0 },
)
</script>

<template>
  <n-modal :show="!!conflict" :mask-closable="false" :close-on-esc="false">
    <n-card
      :title="_.cart.conflict_title"
      style="max-width: 520px; width: 90vw"
      :bordered="false"
      role="dialog"
    >
      <n-flex vertical>
        <n-text>{{ _.cart.conflict_intro }}</n-text>
        <n-text depth="3">
          {{ _.cart.conflict_local }}: {{ counts.local }} ·
          {{ _.cart.conflict_server }}: {{ counts.server }}
        </n-text>
      </n-flex>
      <template #action>
        <n-flex justify="end">
          <n-button @click="cartStore.resolveConflict('keep_server')">
            {{ _.cart.keep_server }}
          </n-button>
          <n-button @click="cartStore.resolveConflict('use_local')">
            {{ _.cart.use_local }}
          </n-button>
          <n-button type="primary" @click="cartStore.resolveConflict('merge')">
            {{ _.cart.merge }}
          </n-button>
        </n-flex>
      </template>
    </n-card>
  </n-modal>
</template>
