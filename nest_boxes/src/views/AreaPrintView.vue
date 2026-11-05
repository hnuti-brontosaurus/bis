<script setup>
import { computed } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { NButton } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import { splitByBatch } from "@/composables/areaBoxes.js"
import { holeLabel, typeName } from "@/composables/boxes.js"
import { boxCountLabel, currentSeason, formatDate } from "@/composables/czech.js"
import { filterBoxes, parseFilters } from "@/composables/filters.js"
import { byId, OPENING_LABELS, STATUS_LABELS } from "@/composables/labels.js"
import { useLoad } from "@/composables/useLoad.js"
import { getArea, getBatch, getCategories } from "@/data/manage.js"

const route = useRoute()
const season = currentSeason()

const { data } = useLoad(async () => {
  const [area, categories, batch] = await Promise.all([
    getArea(route.params.id),
    getCategories(),
    route.query.batch ? getBatch(route.query.batch) : null,
  ])
  return { area, categories, batch }
})

const print = () => window.print()

const filters = parseFilters(route.query)

const typesById = computed(() => byId(data.value?.categories.types ?? []))
const boxes = computed(() => {
  const shown = filterBoxes(data.value.area.boxes, filters, season)
  const { inBatch, outside } = splitByBatch(shown, data.value.batch)
  return data.value.batch ? inBatch : outside
})
</script>

<template>
  <main v-if="data" class="print-page">
    <div class="row no-print">
      <RouterLink
        :to="{
          name: 'area',
          params: { id: data.area.id },
          query: { batch: data.batch?.id },
        }"
      >
        <AppIcon name="back" /> Zpět na oblast
      </RouterLink>
      <span class="spacer" />
      <n-button type="primary" @click="print">
        <template #icon><AppIcon name="print" /></template>
        Vytisknout
      </n-button>
    </div>
    <header class="sheet-head">
      <div>
        <p class="eyebrow">{{ data.area.administration_unit.name }}</p>
        <h1>
          {{ data.area.name
          }}<template v-if="data.batch"> · {{ data.batch.name }}</template>
        </h1>
      </div>
      <div class="blanks">
        <span>Datum: ______________</span>
        <span>Kdo: ________________________</span>
      </div>
    </header>
    <table class="sheet" data-testid="print-table">
      <thead>
        <tr>
          <th>Označení</th>
          <th>Typ a otvor</th>
          <th>Poloha</th>
          <th>Naposledy</th>
          <th class="write">Nalezena</th>
          <th class="write">Vyčištěno</th>
          <th class="write wide">Uvnitř, kdo</th>
          <th class="write">Stav budky</th>
          <th class="write wide">Poznámka</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="box in boxes" :key="box.id">
          <td>
            <b>{{ box.name }}</b>
          </td>
          <td>
            {{ typeName(typesById, box.type_id) }}
            <div class="small">
              {{
                [holeLabel(box), OPENING_LABELS[box.opening]]
                  .filter(Boolean)
                  .join(" · ")
              }}
            </div>
            <div v-if="box.status !== 'in_use'" class="small">
              {{ STATUS_LABELS[box.status] }}
            </div>
          </td>
          <td class="num small">
            {{ box.location.coordinates[1].toFixed(5) }}<br />{{
              box.location.coordinates[0].toFixed(5)
            }}
          </td>
          <td class="small">{{ formatDate(box.last_checked_on) }}</td>
          <td class="write">ano · ne</td>
          <td class="write">ano · ne</td>
          <td class="write" />
          <td class="write" />
          <td class="write" />
        </tr>
      </tbody>
    </table>
    <p class="small">
      Uvnitř: prázdná / hnízdo (kdo) / jiné zvíře / nevím. Stav: v pořádku, potřebuje
      opravu, potřebuje vyměnit, sundaná. Celkem {{ boxCountLabel(boxes.length) }}.
    </p>
  </main>
  <main v-else class="page"><p class="muted">Načítám…</p></main>
</template>

<style scoped>
.print-page {
  padding: 24px 32px;
  display: grid;
  gap: 16px;
  background: var(--surface);
}

.print-page a {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-weight: 700;
}

.sheet-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
}

.sheet-head h1 {
  font-size: 24px;
}

.blanks {
  display: flex;
  gap: 24px;
}

.sheet {
  width: 100%;
  border-collapse: collapse;
  font-size: 12.5px;
}

.sheet th,
.sheet td {
  border: 1px solid var(--line-strong);
  padding: 6px 7px;
  text-align: left;
  vertical-align: top;
}

.sheet th {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  background: var(--surface-2);
}

.sheet td.write {
  color: var(--muted);
  min-width: 70px;
  height: 46px;
}

.sheet th.wide {
  width: 18%;
}

@media print {
  @page {
    size: A4 landscape;
    margin: 10mm;
  }

  .print-page {
    padding: 0;
  }

  .sheet th,
  .sheet td {
    border-color: #555;
  }

  .sheet tr {
    break-inside: avoid;
  }
}
</style>
