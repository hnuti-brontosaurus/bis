<script setup>
import { computed, shallowRef } from "vue"
import { RouterLink, useRoute } from "vue-router"
import { NButton } from "naive-ui"

import AppIcon from "@/components/app/AppIcon.vue"
import BaseMap from "@/components/map/BaseMap.vue"
import RegionBubbles from "@/components/map/RegionBubbles.vue"
import { formatNumber, seasonLabel } from "@/composables/czech.js"
import { describeFigures } from "@/composables/statistics.js"
import { usePublicData } from "@/composables/usePublicData.js"
import { loginUrl, useAuthStore } from "@/data/auth.js"
import { reportError } from "@/data/errors.js"
import { listPublicRegions } from "@/data/public.js"

const MATERIALS = [
  {
    title: "Ptačí budky",
    description: "Kam a jak je věšet",
    icon: "house",
    tone: "primary",
    href: "https://mozek.brontosaurus.cz/attachments/article/1180/ptaci-budky-Brontosaurus.pdf",
  },
  {
    title: "Výroba ptačích budek",
    description: "Rozměry a otvory",
    icon: "tool",
    tone: "accent",
    href: "https://mozek.brontosaurus.cz/attachments/article/1180/Vy%CC%81roba-ptac%CC%8Ci%CC%81ch-budek.pdf",
  },
  {
    title: "Úkryty pro živočichy",
    description: "Netopýři, hmyz, ježci",
    icon: "bird",
    tone: "strong",
    href: "https://mozek.brontosaurus.cz/attachments/article/1180/HB_Ukryty-pro-zivocichy.pdf",
  },
  {
    title: "Co v budce bydlelo?",
    description: "Jak poznat hnízdo",
    icon: "help",
    tone: "lime",
    to: { name: "help_article", params: { slug: "occupants" } },
  },
]

const route = useRoute()
const auth = useAuthStore()
const { season, areas, statistics } = usePublicData()
const regions = shallowRef([])

listPublicRegions().then(result => (regions.value = result), reportError)

const boxCount = computed(() =>
  areas.value?.reduce((sum, area) => sum + area.box_count, 0),
)
const total = computed(() => statistics.value?.total)
const figures = computed(() => total.value && describeFigures(total.value))
</script>

<template>
  <main class="landing">
    <section class="hero">
      <div>
        <p class="eyebrow">Databáze ptačích budek</p>
        <h1>
          Staráme se o
          <span class="num" data-testid="box-count">{{
            boxCount === undefined ? "…" : formatNumber(boxCount)
          }}</span>
          ptačích budek po celém Česku
        </h1>
        <p class="lead">
          Budky věší a čistí dobrovolníci z Hnutí Brontosaurus. Podívej se, kde jsou a v
          kolika se letos hnízdilo.
        </p>
        <div class="cta">
          <RouterLink v-slot="{ navigate }" :to="{ name: 'areas' }" custom>
            <n-button type="primary" size="large" @click="navigate">
              <template #icon><AppIcon name="map" /></template>
              Otevřít mapu budek
            </n-button>
          </RouterLink>
          <RouterLink v-slot="{ navigate }" :to="{ name: 'want_to_hang' }" custom>
            <n-button size="large" @click="navigate">Chci vyvěsit budky</n-button>
          </RouterLink>
        </div>
      </div>
      <RouterLink class="hero-map" :to="{ name: 'areas' }" aria-label="Mapa budek">
        <BaseMap :interactive="false">
          <RegionBubbles :regions="regions" />
        </BaseMap>
      </RouterLink>
    </section>

    <section v-if="total" class="stats" data-testid="headline-stats">
      <div class="stat wide">
        <span>Sezóna {{ seasonLabel(season) }} · vyčištěno</span>
        <b class="num">
          {{ formatNumber(total.cleaned) }}
          <small class="muted">z {{ formatNumber(total.boxes) }} budek</small>
        </b>
        <div class="prog">
          <i :style="{ width: `${(figures.coverage ?? 0) * 100}%` }" />
        </div>
      </div>
      <div class="stat">
        <span>Obsazených z vyčištěných</span>
        <b class="num">{{ figures.occupancyLabel }}</b>
        <span>loni {{ figures.previousOccupancyLabel }}</span>
      </div>
      <div class="stat">
        <span>Oblastí</span>
        <b class="num">{{ areas ? areas.length : "…" }}</b>
        <span>od Krušných hor po Bílé Karpaty</span>
      </div>
    </section>

    <section class="materials">
      <h2>Jak na budky</h2>
      <div class="material-grid">
        <component
          :is="material.to ? RouterLink : 'a'"
          v-for="material in MATERIALS"
          :key="material.title"
          class="material"
          :class="material.tone"
          v-bind="
            material.to
              ? { to: material.to }
              : { href: material.href, target: '_blank' }
          "
        >
          <AppIcon :name="material.icon" />
          <b>{{ material.title }}</b>
          <span>{{ material.description }}</span>
        </component>
      </div>
    </section>

    <section class="band">
      <div>
        <h2>Máš kde vyvěsit budky?</h2>
        <p>Pomůžeme s výběrem místa, s budkami i s prvním podzimním čištěním.</p>
      </div>
      <RouterLink class="band-button" :to="{ name: 'want_to_hang' }">
        Chci vyvěsit budky
      </RouterLink>
    </section>

    <footer class="footer">
      <span>Hnutí Brontosaurus · hnuti@brontosaurus.cz</span>
      <a v-if="auth.isAnonymous" :href="loginUrl(route.fullPath)"
        >Přihlášení pro správce</a
      >
    </footer>
  </main>
</template>

<style scoped>
.landing {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr);
  gap: 36px;
  align-items: center;
  padding: 36px 40px 44px;
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
}

.hero h1 {
  margin-top: 10px;
}

.lead {
  font-size: 18px;
  color: var(--muted);
  max-width: 46ch;
  margin-top: 14px;
}

.cta {
  margin-top: 24px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-map {
  display: block;
  height: 380px;
  border-radius: var(--r);
  overflow: hidden;
  border: 1px solid var(--line);
  box-shadow: var(--card-shadow);
}

.stats {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  gap: 16px;
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
  padding: 0 40px;
}

.stat {
  display: grid;
  gap: 6px;
  align-content: start;
}

.stat b {
  font-size: 36px;
  font-weight: 800;
  line-height: 1;
}

.stat b small {
  font-size: 0.5em;
}

.stat span {
  color: var(--muted);
  font-size: 14px;
}

.materials {
  max-width: 1180px;
  margin: 0 auto;
  width: 100%;
  padding: 44px 40px 10px;
  display: grid;
  gap: 18px;
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.material {
  min-height: 150px;
  padding: 16px;
  border-radius: calc(var(--r) * 0.6);
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-decoration: none;
  box-shadow: var(--card-shadow);
}

.material .icon {
  width: 34px;
  height: 34px;
  stroke-width: 1.6;
  margin-bottom: auto;
}

.material b {
  margin-top: 14px;
  font-size: 17px;
  font-weight: 800;
  line-height: 1.15;
}

.material span {
  font-size: 13.5px;
  opacity: 0.85;
}

.material.primary {
  background: var(--primary);
  color: var(--primary-ink);
}

.material.accent {
  background: var(--accent);
  color: var(--accent-ink);
}

.material.strong {
  background: var(--primary-strong);
  color: var(--surface);
}

.material.lime {
  background: var(--lime);
  color: var(--lime-ink);
}

.band {
  max-width: 1180px;
  margin: 30px auto 0;
  width: calc(100% - 80px);
  padding: 30px 32px;
  border-radius: var(--r);
  background: var(--primary);
  color: var(--primary-ink);
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.band p {
  opacity: 0.9;
  margin-top: 6px;
}

.band-button {
  margin-left: auto;
  padding: 14px 26px;
  border-radius: var(--r-btn);
  background: var(--accent);
  color: var(--accent-ink);
  font-size: 17px;
  font-weight: 700;
  text-decoration: none;
}

.footer {
  margin-top: 40px;
  padding: 28px 40px;
  color: var(--muted);
  font-size: 13.5px;
  display: flex;
  gap: 10px 24px;
  flex-wrap: wrap;
  justify-content: center;
  text-align: center;
  border-top: 1px solid var(--line);
}

@media (max-width: 720px) {
  .hero {
    grid-template-columns: minmax(0, 1fr);
    padding: 26px 16px;
    gap: 22px;
  }

  .hero-map {
    height: 260px;
  }

  .stats {
    grid-template-columns: 1fr 1fr;
    padding: 0 16px;
  }

  .stat.wide {
    grid-column: 1 / -1;
  }

  .materials {
    padding: 30px 16px 0;
  }

  .material-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .band {
    width: calc(100% - 32px);
    padding: 22px;
  }

  .band-button {
    margin-left: 0;
  }

  .footer {
    padding: 22px 16px;
  }
}
</style>
