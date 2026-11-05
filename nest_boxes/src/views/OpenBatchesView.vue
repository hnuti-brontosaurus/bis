<script setup>
import { RouterLink } from "vue-router"
import { NButton, NPopconfirm, useMessage } from "naive-ui"

import BatchLink from "@/components/batch/BatchLink.vue"
import BatchProgress from "@/components/batch/BatchProgress.vue"
import { useLoad } from "@/composables/useLoad.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { closeBatch, listOpenBatches } from "@/data/manage.js"

const message = useMessage()
const auth = useAuthStore()
const { data: batches, reload } = useLoad(listOpenBatches)

const close = async batch => {
  try {
    await closeBatch(batch.id)
    message.success(`Obchůzka ${batch.name} je uzavřená.`)
    await reload()
    auth.refresh()
  } catch (error) {
    reportError(error)
  }
}
</script>

<template>
  <main class="page batches-page">
    <div>
      <p class="eyebrow">Moje oblasti</p>
      <h1>Otevřené obchůzky</h1>
      <p class="muted lead">
        Obchůzky otevřené déle než týden ti každé pondělí připomeneme e-mailem. Samy se
        nezavírají.
      </p>
    </div>
    <p v-if="!batches" class="muted">Načítám…</p>
    <p v-else-if="!batches.length" class="muted">Žádná obchůzka není otevřená.</p>
    <div v-else class="stack">
      <article
        v-for="batch in batches"
        :key="batch.id"
        class="card batch-card"
        data-testid="open-batch"
      >
        <div class="stack info">
          <div>
            <h3>
              <RouterLink :to="{ name: 'link', params: { token: batch.token } }">{{
                batch.name
              }}</RouterLink>
            </h3>
            <RouterLink
              class="small"
              :to="{
                name: 'area',
                params: { id: batch.area_id },
              }"
            >
              {{ batch.area_name }}
            </RouterLink>
          </div>
          <BatchLink :token="batch.token" />
        </div>
        <BatchProgress :batch="batch" />
        <div class="row">
          <RouterLink
            v-slot="{ navigate }"
            :to="{ name: 'batch', params: { id: batch.id } }"
            custom
          >
            <n-button type="primary" size="small" @click="navigate">Otevřít</n-button>
          </RouterLink>
          <n-popconfirm @positive-click="close(batch)">
            <template #trigger>
              <n-button size="small">Uzavřít</n-button>
            </template>
            Uzavřít bez potvrzení? Čekající kontroly zůstanou nepotvrzené.
          </n-popconfirm>
        </div>
      </article>
    </div>
  </main>
</template>

<style scoped>
.batches-page {
  max-width: 980px;
}

.lead {
  margin-top: 8px;
}

h1 {
  margin-top: 6px;
}

.batch-card {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(0, 1fr) auto;
  gap: 20px;
  align-items: center;
}

.info {
  gap: 8px;
}

@media (max-width: 720px) {
  .batch-card {
    grid-template-columns: minmax(0, 1fr);
    gap: 14px;
  }
}
</style>
