<script setup>
import { computed } from "vue"
import { useRoute, useRouter } from "vue-router"
import { useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import CheckForm from "@/components/check/CheckForm.vue"
import { boxSummary } from "@/composables/boxes.js"
import { byId } from "@/composables/labels.js"
import { useLinkStore } from "@/data/link.js"

const route = useRoute()
const router = useRouter()
const message = useMessage()
const link = useLinkStore()

const box = computed(() => link.boxes.find(item => item.id === route.params.boxId))
const typesById = computed(() => byId(link.payload.categories.types))

// Photos already sent can't be removed through a link, so the form only adds
const initial = computed(() => {
  const check = link.checks.get(route.params.boxId)
  return check ? { ...check, photos: [] } : null
})

const submit = async (check, photos) => {
  const sent = link.payload.checks.find(item => item.id === check.id)
  const firstOrder = (sent?.photos.length ?? 0) + link.queuedPhotos(check.id).length
  await link.saveCheck(check)
  for (const [index, photo] of photos.added.entries())
    await link.savePhoto({ parent_id: check.id, photo, order: firstOrder + index })
  message.success(
    box.value.status === "planned" ? "Pověšení je uložené." : "Kontrola je uložená.",
  )
  router.push({ name: "link" })
}
</script>

<template>
  <VolunteerHeader
    :title="`Budka ${box.name}`"
    :subtitle="`${boxSummary(box, typesById)} · ${link.payload.area.name}`"
    :back="{ name: 'link' }"
    :pending="link.pending"
  />
  <main class="page check-page">
    <div v-if="box.note" class="note warn" data-testid="volunteer-note">
      <AppIcon name="warn" />
      <div>
        <b>Poznámka pro dobrovolníky</b>
        {{ box.note }}
      </div>
    </div>
    <CheckForm
      :key="initial?.id ?? 'new'"
      :box="box"
      :initial="initial"
      :categories="link.payload.categories"
      :help-articles="link.payload.help_articles"
      :submit="submit"
      :save-label="box.status === 'planned' ? 'Uložit pověšení' : 'Uložit kontrolu'"
      save-hint="Uloží se do telefonu. Odešle se, až bude signál."
      :help-linked="false"
    />
  </main>
</template>

<style scoped>
.check-page {
  max-width: 1080px;
  gap: 18px;
  padding-bottom: 0;
}
</style>
