import { setWorkerUrl } from "maplibre-gl"
import workerUrl from "maplibre-gl/dist/maplibre-gl-worker.mjs?worker&url"

// maplibre finds its worker next to its own module, which neither Vite's
// dependency pre-bundling nor the build keeps; hand it the bundled one.
setWorkerUrl(workerUrl)
