<script setup>
import { NH1, NText } from "naive-ui"
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome"
import {
  faArrowRight,
  faBookOpen,
  faCalendarDays,
  faCampground,
  faCarrot,
  faCircleQuestion,
  faDumpster,
  faHandshake,
  faHeartPulse,
  faRecycle,
  faSeedling,
  faShoePrints,
  faSignsPost,
  faUsers,
} from "@fortawesome/free-solid-svg-icons"
import { _ } from "@/composables/translations.js"

// The header menu's groups; the first tile of each is the one most used.
// Tile keys are route names and menu keys.
const sections = [
  {
    key: "cookbook",
    tiles: [
      { key: "recipes", icon: faBookOpen },
      { key: "menus", icon: faCalendarDays },
      { key: "chefs", icon: faUsers },
      { key: "ingredients", icon: faCarrot },
    ],
  },
  {
    key: "vegan",
    tiles: [
      { key: "manifest", icon: faSeedling },
      { key: "how_to", icon: faShoePrints },
      { key: "risks", icon: faHeartPulse },
      { key: "where_to_go", icon: faSignsPost },
    ],
  },
  {
    key: "tips",
    tiles: [
      { key: "bronto", icon: faCampground },
      { key: "faq", icon: faCircleQuestion },
      { key: "dumpster_diving", icon: faDumpster },
      { key: "zero_waste", icon: faRecycle },
    ],
  },
]

const joinUs = { key: "join_us", icon: faHandshake }
</script>

<template>
  <div class="home">
    <header class="intro">
      <n-h1 class="title">{{ _.home.title }}</n-h1>
      <n-text depth="3">{{ _.home.subtitle }}</n-text>
    </header>

    <section v-for="section in sections" :key="section.key" class="section">
      <h2 class="section-heading">{{ _.menu[section.key] }}</h2>
      <div class="section-tiles">
        <router-link
          :to="{ name: section.tiles[0].key }"
          class="tile main-tile"
          :class="`main-tile-${section.key}`"
        >
          <span class="main-icon">
            <font-awesome-icon :icon="section.tiles[0].icon" />
          </span>
          <span class="tile-title display-font">{{
            _.menu[section.tiles[0].key]
          }}</span>
          <span class="tile-text">{{ _.home[section.tiles[0].key] }}</span>
          <span class="more">
            {{ _.home.open }} <font-awesome-icon :icon="faArrowRight" />
          </span>
        </router-link>
        <div class="side-tiles">
          <router-link
            v-for="tile in section.tiles.slice(1)"
            :key="tile.key"
            :to="{ name: tile.key }"
            class="tile side-tile"
          >
            <span class="side-icon"><font-awesome-icon :icon="tile.icon" /></span>
            <span>
              <span class="tile-title display-font">{{ _.menu[tile.key] }}</span>
              <span class="tile-text">{{ _.home[tile.key] }}</span>
            </span>
          </router-link>
        </div>
      </div>
    </section>

    <router-link :to="{ name: joinUs.key }" class="tile join-tile">
      <span class="main-icon"><font-awesome-icon :icon="joinUs.icon" /></span>
      <span>
        <span class="tile-title display-font">{{ _.menu[joinUs.key] }}</span>
        <span class="tile-text">{{ _.home[joinUs.key] }}</span>
      </span>
      <font-awesome-icon :icon="faArrowRight" class="join-arrow" />
    </router-link>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 36px;
}

.intro {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.intro .title {
  margin: 0;
  color: var(--primary-text);
}

.section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section .section-heading {
  margin: 0;
}

.section-tiles {
  display: grid;
  gap: 14px;
}

.tile {
  display: flex;
  border: 1px solid var(--line);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text);
  text-decoration: none;
  transition:
    box-shadow 0.2s,
    transform 0.2s;
}

.tile:hover,
.tile:focus-visible {
  box-shadow: var(--hover-shadow);
  transform: translateY(-2px);
}

.tile-title {
  display: block;
  font-size: 1.15em;
  font-weight: 700;
}

.tile-text {
  display: block;
  color: var(--muted);
}

.main-tile {
  flex-direction: column;
  gap: 10px;
  padding: 28px;
  border: 0;
  background: var(--primary-soft);
}

.main-tile .tile-title {
  font-size: 1.7em;
}

.main-tile .tile-text {
  max-width: 40ch;
  color: var(--text);
}

.main-icon {
  display: grid;
  flex: none;
  place-items: center;
  width: 64px;
  height: 64px;
  margin-bottom: 6px;
  border-radius: 50%;
  background: var(--primary);
  color: var(--primary-ink);
  font-size: 28px;
}

.main-tile-tips {
  background: var(--accent-soft);
}

.main-tile-tips .main-icon {
  background: var(--accent);
  color: var(--accent-ink);
}

.more {
  margin-top: auto;
  padding-top: 8px;
  color: var(--primary-text);
  font-weight: 600;
}

.main-tile-tips .more {
  color: var(--accent-text);
}

.side-tiles {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.side-tile {
  flex: 1;
  gap: 16px;
  align-items: center;
  padding: 16px 18px;
}

.side-icon {
  display: grid;
  flex: none;
  place-items: center;
  width: 46px;
  height: 46px;
  border-radius: 6px;
  background: var(--surface-muted);
  color: var(--primary-text);
  font-size: 20px;
}

.join-tile {
  gap: 20px;
  align-items: center;
  padding: 24px 28px;
  border: 0;
  background: var(--primary-soft);
}

.join-tile .main-icon {
  margin: 0;
}

.join-arrow {
  margin-left: auto;
  color: var(--primary-text);
  font-size: 1.4em;
}

@media (min-width: 720px) {
  .section-tiles {
    grid-template-columns: 1fr 1fr;
  }

  .section:nth-of-type(even) .main-tile {
    order: 2;
  }
}
</style>
