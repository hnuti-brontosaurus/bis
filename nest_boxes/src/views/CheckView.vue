<script setup>
import { computed } from "vue"
import { RouterLink, useRoute, useRouter } from "vue-router"
import { NButton, NPopconfirm, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import CheckForm from "@/components/check/CheckForm.vue"
import { boxSummary } from "@/composables/boxes.js"
import { currentSeason, formatDate, seasonLabel } from "@/composables/czech.js"
import { byId } from "@/composables/labels.js"
import { useLoad } from "@/composables/useLoad.js"
import {
  confirmCheck,
  createCheck,
  deleteCheck,
  getArea,
  getBox,
  getCategories,
  listChecks,
  listHelpArticles,
  saveCheckPhotos,
  updateCheck,
} from "@/data/manage.js"
import { reportError } from "@/data/errors.js"

const route = useRoute()
const router = useRouter()
const message = useMessage()

// ?check= edits that check, otherwise the season's check is edited if there is one
const { data } = useLoad(async () => {
  const [box, categories, helpArticles] = await Promise.all([
    getBox(route.params.id),
    getCategories(),
    listHelpArticles(),
  ])
  const [area, checks] = await Promise.all([
    getArea(box.area_id),
    route.query.check
      ? listChecks({ box: box.id }).then(all =>
          all.filter(check => check.id === route.query.check),
        )
      : listChecks({ box: box.id, season: currentSeason() }),
  ])
  return { box, area, categories, helpArticles, check: checks[0] ?? null }
})

const typesById = computed(() => byId(data.value?.categories.types ?? []))

const toBox = () => router.push({ name: "box", params: { id: route.params.id } })

const submit = async (values, photos) => {
  const existing = data.value.check
  const check = existing
    ? await updateCheck(existing.id, values)
    : await createCheck(values)
  await saveCheckPhotos(check, photos)
  message.success(
    existing ? "Kontrola je upravená." : "Kontrola je uložená a potvrzená.",
  )
  toBox()
}

const remove = async () => {
  try {
    await deleteCheck(data.value.check.id)
    message.success("Kontrola je smazaná.")
    toBox()
  } catch (error) {
    reportError(error)
  }
}

const confirm = async () => {
  try {
    await confirmCheck(data.value.check.id)
    message.success("Kontrola je potvrzená.")
    toBox()
  } catch (error) {
    reportError(error)
  }
}
</script>

<template>
  <main class="page check-page">
    <template v-if="data">
      <div class="crumb">
        <RouterLink :to="{ name: 'areas' }">Mapa</RouterLink>
        <AppIcon name="chev" />
        <RouterLink :to="{ name: 'area', params: { id: data.area.id } }">
          {{ data.area.name }}
        </RouterLink>
        <AppIcon name="chev" />
        <RouterLink :to="{ name: 'box', params: { id: data.box.id } }">
          {{ data.box.name }}
        </RouterLink>
        <AppIcon name="chev" />
        <span>Kontrola</span>
      </div>
      <div>
        <p class="eyebrow">{{ boxSummary(data.box, typesById) }}</p>
        <h1>
          {{ data.check ? "Úprava kontroly" : "Kontrola" }} budky {{ data.box.name }}
        </h1>
      </div>
      <div v-if="data.check" class="note">
        <AppIcon name="edit" />
        <div>
          <b>
            Kontrola z {{ formatDate(data.check.date) }}, sezóna
            {{ seasonLabel(data.check.season) }}
          </b>
          {{
            data.check.is_confirmed
              ? "Je potvrzená. Když je to poslední kontrola budky, úprava změní i budku."
              : "Čeká na potvrzení. Potvrzením se zapíše do budky."
          }}
          Budka má v sezóně jen jednu kontrolu, takže se upravuje tahle.
        </div>
      </div>
      <CheckForm
        :key="data.check?.id ?? 'new'"
        :box="data.box"
        :initial="data.check"
        :categories="data.categories"
        :help-articles="data.helpArticles"
        :submit="submit"
        editable-date
        :save-hint="
          data.check || data.box.status === 'planned'
            ? ''
            : 'Kontrola od správce se potvrdí hned a zapíše se do budky.'
        "
      >
        <template #actions>
          <n-button v-if="data.check && !data.check.is_confirmed" @click="confirm">
            <template #icon><AppIcon name="check" /></template>
            Potvrdit
          </n-button>
          <n-popconfirm v-if="data.check" @positive-click="remove">
            <template #trigger>
              <n-button type="error" ghost>
                <template #icon><AppIcon name="trash" /></template>
                Smazat
              </n-button>
            </template>
            Smazat tuhle kontrolu? Budka zůstane, jak je.
          </n-popconfirm>
        </template>
      </CheckForm>
    </template>
    <p v-else class="muted">Načítám…</p>
  </main>
</template>

<style scoped>
.check-page {
  max-width: 1080px;
  gap: 18px;
  padding-bottom: 0;
}
</style>
