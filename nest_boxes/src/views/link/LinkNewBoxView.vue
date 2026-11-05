<script setup>
import { computed, ref } from "vue"
import { useRoute, useRouter } from "vue-router"
import { NButton, NInput, useMessage } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import VolunteerHeader from "@/components/app/VolunteerHeader.vue"
import BoxFields from "@/components/box/BoxFields.vue"
import { boxValues } from "@/components/check/checkForm.js"
import BoxMarkers from "@/components/map/BoxMarkers.vue"
import { distance } from "@/components/map/geometry.js"
import { typeName } from "@/composables/boxes.js"
import { formatDistance, isoDate } from "@/composables/czech.js"
import { byId, MEASURED_HOLE_SHAPES } from "@/composables/labels.js"
import {
  duplicateNames,
  SPACING_HINT,
  spacingWarnings,
} from "@/composables/linkBoxes.js"
import { uuid } from "@/composables/uuid.js"
import { CZECHIA_BOUNDS } from "@/config.js"
import { useLinkStore } from "@/data/link.js"

const REQUIRED = {
  name: "Napiš, co je na budce napsané.",
  location: "Klepni do mapy, kde budka visí, nebo použij svoji polohu.",
  hole_shape: "Vyber tvar otvoru.",
  type: "Vyber typ budky.",
  opening: "Vyber, jak se budka otevírá.",
}

const route = useRoute()
const router = useRouter()
const message = useMessage()
const link = useLinkStore()

const editing = link.boxes.find(box => box.id === route.query.budka)
const id = editing?.id ?? uuid()
// The check that hangs the box; a resend with the same ids updates both
const checkId = editing?.check?.id ?? link.checks.get(id)?.id ?? uuid()
const values = ref(
  editing
    ? boxValues(editing)
    : {
        name: "",
        hole_shape: null,
        hole_size: null,
        type: null,
        opening: null,
        material: null,
        location: null,
        installed_on: isoDate(),
      },
)
const note = ref(editing?.note ?? "")
const errors = ref({})

const typesById = computed(() => byId(link.payload.categories.types))
const [[west, south], [east, north]] = CZECHIA_BOUNDS
const center = link.payload.boxes[0]?.location ?? {
  type: "Point",
  coordinates: [(west + east) / 2, (south + north) / 2],
}
const others = computed(() =>
  link.rows.filter(row => row.id !== id && row.state !== "planned"),
)

const spacing = computed(() =>
  values.value.location
    ? spacingWarnings(link.boxes, values.value.location, values.value.type, id)
    : [],
)
const duplicateNote = computed(() => {
  const [other] = duplicateNames(link.boxes, values.value.name, id)
  if (!other) return ""
  const away = values.value.location
    ? `, ${formatDistance(distance(values.value.location, other.location))} odsud`
    : ""
  return `Budka s tímto označením už v oblasti ${link.payload.area.name} je${away}.`
})

const validate = () => {
  const found = Object.fromEntries(
    Object.entries(REQUIRED).filter(([field]) => !values.value[field]),
  )
  if (MEASURED_HOLE_SHAPES.includes(values.value.hole_shape) && !values.value.hole_size)
    found.hole_size = "Změř nejužší místo otvoru."
  errors.value = found
  return !Object.keys(found).length
}

const save = async () => {
  if (!validate()) return
  const { type, ...fields } = values.value
  await link.saveBox({
    ...fields,
    id,
    type_id: type,
    material: fields.material ?? "",
    note: note.value,
    check: {
      id: checkId,
      date: fields.installed_on,
      made_at: new Date().toISOString(),
      volunteer_nickname: link.profile.nickname,
      volunteer_email: link.profile.email,
    },
  })
  message.success("Budka je uložená. Potvrdí ji správce oblasti.")
  router.push({ name: "link" })
}
</script>

<template>
  <VolunteerHeader
    :title="editing ? `Budka ${editing.name}` : 'Nová budka'"
    :subtitle="`${link.payload.area.name} · čeká na potvrzení správcem`"
    :back="{ name: 'link' }"
    :pending="link.pending"
  />
  <main class="page new-box">
    <div class="card stack">
      <BoxFields
        v-model="values"
        :types="link.payload.categories.types"
        :center="center"
        :errors="errors"
        :locate-on-open="!editing"
      >
        <template #map>
          <BoxMarkers :boxes="others" passive />
        </template>
      </BoxFields>
      <div v-for="warning in spacing" :key="warning.box.id" class="note warn">
        <AppIcon name="warn" />
        <div>
          <b>{{
            warning.shouldBeMoved ? "Příliš blízko jiné budky" : "Blízko jiné budky"
          }}</b>
          {{ warning.box.name }} ({{ typeName(typesById, warning.box.type_id) }}) visí
          {{ formatDistance(warning.distance) }} odsud. {{ SPACING_HINT }} Opravdu ji
          chceš pověsit tady?
        </div>
      </div>
      <div v-if="duplicateNote" class="note warn">
        <AppIcon name="warn" />
        <div>{{ duplicateNote }}</div>
      </div>
      <div class="field">
        <label for="box-note">Poznámka pro dobrovolníky</label>
        <n-input
          id="box-note"
          v-model:value="note"
          placeholder="Kde přesně visí, jak se k ní dostat…"
          type="textarea"
          :autosize="{ minRows: 2 }"
        />
      </div>
      <n-button type="primary" size="large" block @click="save">
        <template #icon><AppIcon name="check" /></template>
        Uložit budku
      </n-button>
      <p class="small muted">Uloží se do telefonu. Odešle se, až bude signál.</p>
    </div>
  </main>
</template>

<style scoped>
.new-box {
  max-width: 720px;
}
</style>
