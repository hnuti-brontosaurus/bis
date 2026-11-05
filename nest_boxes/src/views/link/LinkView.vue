<script setup>
import { computed, ref, watch } from "vue"
import { RouterView, useRoute } from "vue-router"

import AppIcon from "@/components/app/AppIcon.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import VolunteerWelcome from "@/components/link/VolunteerWelcome.vue"
import { plural } from "@/composables/czech.js"
import { useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { useLinkStore } from "@/data/link.js"

const STATUSES = {
  loading: { title: "Načítám odkaz…", text: "" },
  closed: {
    title: "Obchůzka je uzavřená",
    text: "Správce oblasti už tuhle obchůzku uzavřel, takže odkaz nic dalšího nepřijme. Díky za pomoc!",
  },
  missing: {
    title: "Odkaz neexistuje",
    text: "Zkontroluj, že máš celý odkaz, nebo si o nový řekni správci oblasti.",
  },
  offline: {
    title: "Chybí signál",
    text: "Odkaz se do telefonu ještě nestáhl. Otevři ho znovu, až budeš mít signál.",
  },
}

const route = useRoute()
const link = useLinkStore()

// A signed-in person is known already; a volunteer says who they are once.
// Offline whoami would only fail into noise, so the volunteer is asked then.
const auth = !link.profile.nickname && navigator.onLine ? useAuthStore() : null
const knowsWho = ref(!auth)
auth?.loaded.finally(() => (knowsWho.value = true))
const asksWho = computed(() => !link.profile.nickname && !auth?.isAuthenticated)

watch(
  () => route.params.token,
  token => link.open(token).catch(reportError),
  { immediate: true },
)

const droppedLabel = count =>
  `${count} ${plural(count, "neodeslaný záznam", "neodeslané záznamy", "neodeslaných záznamů")}`
</script>

<template>
  <template v-if="link.status === 'ready'">
    <template v-if="knowsWho">
      <VolunteerWelcome v-if="asksWho" />
      <RouterView v-else />
    </template>
  </template>
  <template v-else>
    <VolunteerHeader title="Čištění budek" />
    <main class="page narrow" data-testid="link-status">
      <div class="stack">
        <h1>{{ STATUSES[link.status].title }}</h1>
        <p v-if="STATUSES[link.status].text" class="muted lead">
          {{ STATUSES[link.status].text }}
        </p>
        <div v-if="link.droppedOnClose" class="note warn">
          <AppIcon name="warn" />
          <div>
            {{ droppedLabel(link.droppedOnClose) }} z telefonu už neodešle. Kdyby šlo o
            něco důležitého, napiš to správci oblasti.
          </div>
        </div>
      </div>
    </main>
  </template>
</template>

<style scoped>
.narrow {
  max-width: 640px;
}

.lead {
  margin-top: 10px;
  font-size: 17px;
}
</style>
