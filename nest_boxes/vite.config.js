import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"
import { VitePWA } from "vite-plugin-pwa"

import { APP_PATH } from "./src/config.js"

export default defineConfig({
  base: `${APP_PATH}/`,
  plugins: [
    vue(),
    VitePWA({
      registerType: "autoUpdate",
      manifest: {
        name: "Budky · Hnutí Brontosaurus",
        short_name: "Budky",
        lang: "cs",
        theme_color: "#118a2c",
        background_color: "#f0f4f1",
        display: "standalone",
        icons: [{ src: "logo.svg", sizes: "any", type: "image/svg+xml" }],
      },
      workbox: {
        globPatterns: ["**/*.{js,css,html,svg,woff2}"],
        navigateFallback: `${APP_PATH}/index.html`,
        navigateFallbackAllowlist: [new RegExp(`^${APP_PATH}/`)],
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
