import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { VitePWA } from "vite-plugin-pwa"

import { APP_PATH, DEM_TILES_URL, MAP_STYLE_URL } from "./src/config.js"

const escapeRegExp = text => text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")

const MAP_ORIGINS = [
  ...new Set([MAP_STYLE_URL, DEM_TILES_URL].map(url => new URL(url).origin)),
]
  .map(escapeRegExp)
  .join("|")

// Tiles, glyphs and sprites are files at versioned paths, so they never change
// once fetched. The style and its TileJSON have no extension and name the
// current tile version, so they go to the network first.
const MAP_FILE = new RegExp(`^(${MAP_ORIGINS})/.*\\.\\w+$`)
const MAP_DOCUMENT = new RegExp(`^(${MAP_ORIGINS})/`)

export default defineConfig({
  base: `${APP_PATH}/`,
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      pwaAssets: { image: "public/logo.svg", overrideManifestIcons: true },
      manifest: {
        name: "Budky · Hnutí Brontosaurus",
        short_name: "Budky",
        lang: "cs",
        theme_color: "#118a2c",
        background_color: "#f0f4f1",
        display: "standalone",
        scope: `${APP_PATH}/`,
        start_url: `${APP_PATH}/`,
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,png,ico,woff2}"],
        navigateFallback: `${APP_PATH}/index.html`,
        navigateFallbackAllowlist: [new RegExp(`^${APP_PATH}/`)],
        runtimeCaching: [
          {
            urlPattern: MAP_FILE,
            handler: "CacheFirst",
            options: {
              cacheName: "nest_boxes_map",
              cacheableResponse: { statuses: [200] },
            },
          },
          {
            urlPattern: MAP_DOCUMENT,
            handler: "NetworkFirst",
            options: {
              cacheName: "nest_boxes_map_documents",
              networkTimeoutSeconds: 5,
              cacheableResponse: { statuses: [200] },
            },
          },
          {
            urlPattern: ({ url, sameOrigin }) =>
              sameOrigin && url.pathname.startsWith("/media/"),
            handler: "CacheFirst",
            options: {
              cacheName: "nest_boxes_media",
              cacheableResponse: { statuses: [200] },
            },
          },
        ],
      },
    }),
  ],
  worker: { format: "es" },
  build: {
    chunkSizeWarningLimit: 1500,
    outDir: "./dist",
    emptyOutDir: true,
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },
  server: {
    allowedHosts: ["nest_boxes", "nginx"],
    host: "0.0.0.0",
    port: 3003,
  },
})
