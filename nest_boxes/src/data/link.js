import { defineStore } from "pinia"
import { computed, reactive, ref, shallowRef } from "vue"
import { useLocalStorage } from "@vueuse/core"

import { fetchAll, PARALLEL_REQUESTS, prefetchMap } from "@/components/map/prefetch.js"
import { reportedState } from "@/composables/boxes.js"
import { boxLocation, latestChecks } from "@/composables/linkBoxes.js"
import { client } from "@/data/client.js"
import { reportError, reportRejected } from "@/data/errors.js"
import { forgetLink, savedLink, saveLink } from "@/data/offline.js"
import { dropToken, enqueue, flushOutbox, outboxItems } from "@/data/outbox.js"

const RETRY_INTERVAL = 30_000

const post = path => (token, payload) =>
  client.post(`/links/${token}/${path}/`, payload).then(({ data }) => data)

const SEND = { box: post("boxes"), check: post("checks"), photo: post("check_photos") }

const withSent = (payload, item, result) => {
  if (item.kind === "check")
    return {
      ...payload,
      boxes: payload.boxes.map(box =>
        box.id === result.check.box_id
          ? { ...box, season_state: result.season_state }
          : box,
      ),
      checks: [
        ...payload.checks.filter(check => check.box_id !== result.check.box_id),
        result.check,
      ],
    }
  if (item.kind === "box") {
    const { warnings: _warnings, check, ...box } = result
    return {
      ...payload,
      boxes: [...payload.boxes.filter(({ id }) => id !== box.id), box],
      checks: [...payload.checks.filter(({ id }) => id !== check.id), check],
    }
  }
  return {
    ...payload,
    checks: payload.checks.map(check =>
      check.id === item.payload.parent_id
        ? {
            ...check,
            // The server replaces a photo resent with the same order
            photos: [
              ...check.photos.filter(photo => photo.order !== result.order),
              result,
            ],
          }
        : check,
    ),
  }
}

const imageSources = articles =>
  articles.flatMap(article =>
    [...new DOMParser().parseFromString(article.content, "text/html").images].map(
      image => image.src,
    ),
  )

// What goes into IndexedDB has to be cloneable, which Vue's proxies are not
const plain = value => JSON.parse(JSON.stringify(value))

/**
 * The batch link being worked on: its payload, kept on the phone for offline
 * use, with what the volunteer saved and has not sent yet laid over it.
 */
export const useLinkStore = defineStore("link", () => {
  const token = ref(null)
  // loading | ready | closed | missing | offline (no signal and nothing saved)
  const status = ref("loading")
  const payload = shallowRef(null)
  const outbox = shallowRef([])
  // How many unsent things the closed batch took with it
  const droppedOnClose = ref(0)
  const prefetch = reactive({ done: 0, total: 0, state: "idle" })
  const profile = useLocalStorage("nest_boxes_volunteer", { nickname: "", email: "" })
  const prefetched = new Set()

  const queued = computed(() => outbox.value.filter(item => item.token === token.value))
  const pending = computed(() => queued.value.length)
  const rejected = computed(() => queued.value.filter(item => item.rejected))

  const boxes = computed(() => {
    const byId = new Map(payload.value.boxes.map(box => [box.id, box]))
    for (const item of queued.value)
      if (item.kind === "box")
        // As the server answers it: planned, hung by its pending check
        byId.set(item.id, {
          status: "planned",
          season_state: "done",
          is_new: true,
          is_verified: false,
          ...item.payload,
        })
    return [...byId.values()]
  })

  const queuedChecks = computed(() =>
    queued.value.filter(item => item.kind === "check").map(item => item.payload),
  )

  const checks = computed(() =>
    latestChecks([...payload.value.checks, ...queuedChecks.value]),
  )

  // The boxes as the map and the list show them: where they hang now and how far
  // along. The server's season state does not know the checks still on the phone.
  const rows = computed(() => {
    const unsent = new Set(queuedChecks.value)
    return boxes.value.map(box => {
      const check = checks.value.get(box.id)
      const state = (unsent.has(check) && reportedState(check)) || box.season_state
      return { ...box, location: boxLocation(box, check), check, state }
    })
  })

  const queuedPhotos = checkId =>
    queued.value.filter(
      item => item.kind === "photo" && item.payload.parent_id === checkId,
    )

  const refreshOutbox = async () => {
    outbox.value = await outboxItems()
  }

  const close = async closedToken => {
    const dropped = outbox.value.filter(item => item.token === closedToken).length
    await dropToken(closedToken)
    await forgetLink(closedToken)
    if (closedToken === token.value) {
      droppedOnClose.value = dropped
      status.value = "closed"
    }
    await refreshOutbox()
  }

  const applySent = async (item, result) => {
    const current = item.token === token.value
    const updated = withSent(
      current ? payload.value : await savedLink(item.token),
      item,
      result,
    )
    await saveLink(item.token, updated)
    if (current) payload.value = updated
    await refreshOutbox()
  }

  const onRejected = async item => {
    reportRejected()
    console.error(item.rejected)
    await refreshOutbox()
  }

  let flushing = null

  const flush = () => {
    flushing ??= flushOutbox(SEND, { onSent: applySent, onClosed: close, onRejected })
      .then(async complete => {
        flushing = null
        await refreshOutbox()
        if (complete && outbox.value.some(item => !item.rejected)) flush()
      })
      .catch(reportError)
    return flushing
  }

  window.addEventListener("online", flush)
  setInterval(() => outbox.value.length && flush(), RETRY_INTERVAL)

  const startPrefetch = async () => {
    if (prefetched.has(token.value)) return
    prefetched.add(token.value)
    const points = payload.value.boxes.map(box => box.location)
    Object.assign(prefetch, { done: 0, total: 0, state: "running" })
    const onProgress = (done, total) => Object.assign(prefetch, { done, total })
    const failed = await Promise.all([
      points.length ? prefetchMap(points, onProgress) : 0,
      fetchAll(imageSources(payload.value.help_articles), {
        parallel: PARALLEL_REQUESTS,
        onProgress: () => {},
      }),
    ]).then(
      counts => counts.some(Boolean),
      () => true,
    )
    prefetch.state = failed ? "partial" : "ready"
  }

  const open = async value => {
    if (token.value === value && status.value === "ready") return
    token.value = value
    status.value = "loading"
    payload.value = null
    await refreshOutbox()
    try {
      const { data } = await client.get(`/links/${value}/`)
      await saveLink(value, data)
      payload.value = data
    } catch (error) {
      if (error.response?.status === 410) return close(value)
      if (error.response?.status === 404) {
        status.value = "missing"
        return
      }
      if (error.response?.status < 500) throw error
      payload.value = await savedLink(value)
      if (!payload.value) {
        status.value = "offline"
        return
      }
    }
    status.value = "ready"
    flush()
    startPrefetch()
  }

  // After a manager changed which boxes the batch has
  const refresh = async () => {
    const { data } = await client.get(`/links/${token.value}/`)
    await saveLink(token.value, data)
    payload.value = data
    // A box added from elsewhere in the area may lie outside the cached tiles
    prefetched.delete(token.value)
    startPrefetch()
  }

  const save = async (kind, id, body) => {
    await enqueue({ token: token.value, kind, id, payload: plain(body) })
    await refreshOutbox()
    flush()
  }

  const saveCheck = check =>
    save("check", check.id, {
      ...check,
      volunteer_nickname: profile.value.nickname,
      volunteer_email: profile.value.email,
    })

  const saveBox = box => save("box", box.id, box)

  const savePhoto = photo => save("photo", `${photo.parent_id}:${photo.order}`, photo)

  return {
    refresh,
    token,
    status,
    payload,
    profile,
    prefetch,
    droppedOnClose,
    pending,
    rejected,
    boxes,
    checks,
    rows,
    queuedPhotos,
    open,
    flush,
    saveCheck,
    saveBox,
    savePhoto,
  }
})
