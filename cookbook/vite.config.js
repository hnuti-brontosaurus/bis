import { fileURLToPath, URL } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue()
  ],
  build: {
    chunkSizeWarningLimit: 1000,
    minify: false,
    outDir: "./dist",
    emptyOutDir: true
  },
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    }
  },
  server: {
    allowedHosts: ["cookbook"],
    host: "0.0.0.0",
    port: 3001
  },
  base: "/cookbook/",
  publicDir: "./public"
})
