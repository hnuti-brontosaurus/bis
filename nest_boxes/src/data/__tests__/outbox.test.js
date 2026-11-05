import "fake-indexeddb/auto"

import { beforeEach, describe, expect, it, vi } from "vitest"

import { database } from "@/data/offline.js"
import { enqueue, flushOutbox, outboxItems } from "@/data/outbox.js"

const check = (id, madeAt, extra = {}) => ({
  token: "open",
  kind: "check",
  id,
  payload: { id, box_id: `box-${id}`, made_at: madeAt, ...extra },
})

const photo = (checkId, order) => ({
  token: "open",
  kind: "photo",
  id: `${checkId}:${order}`,
  payload: { parent_id: checkId, order, photo: "data:" },
})

const answered = (status, data = {}) =>
  Object.assign(new Error(), { response: { status, data } })

const handlers = () => ({ onSent: vi.fn(), onClosed: vi.fn(), onRejected: vi.fn() })

const sender = (respond = () => ({ accepted: true })) => {
  const sent = []
  const send = Object.fromEntries(
    ["box", "check", "photo"].map(kind => [
      kind,
      async (token, payload) => {
        sent.push([kind, payload.id ?? payload.parent_id])
        return respond(kind, token, payload)
      },
    ]),
  )
  return { send, sent }
}

beforeEach(async () => (await database).clear("outbox"))

describe("outbox", () => {
  it("sends in the order things were saved", async () => {
    await enqueue({ token: "open", kind: "box", id: "b", payload: { id: "b" } })
    await enqueue(check("c", "2026-11-03T10:00:00Z"))
    await enqueue(photo("c", 0))
    const { send, sent } = sender()

    expect(await flushOutbox(send, handlers())).toBe(true)

    expect(sent).toEqual([
      ["box", "b"],
      ["check", "c"],
      ["photo", "c"],
    ])
    expect(await outboxItems()).toEqual([])
  })

  it("keeps the check made later when the same check is saved again", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z", { note: "first" }))
    await enqueue(check("d", "2026-11-03T10:30:00Z"))
    await enqueue(check("c", "2026-11-03T11:00:00Z", { note: "edited" }))
    await enqueue(check("c", "2026-11-03T09:00:00Z", { note: "stale" }))

    const items = await outboxItems()
    expect(items.map(item => item.id)).toEqual(["c", "d"])
    expect(items[0].payload.note).toBe("edited")
  })

  it("keeps the edit of a queued check, which keeps its made_at", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z", { note: "first" }))
    await enqueue(check("c", "2026-11-03T10:00:00Z", { note: "edited" }))

    const [item] = await outboxItems()
    expect(item.payload.note).toBe("edited")
  })

  it("keeps what was saved again while it was being sent", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z", { note: "first" }))
    const { send, sent } = sender(async () => {
      await enqueue(check("c", "2026-11-03T10:00:00Z", { note: "edited" }))
      return { accepted: true }
    })

    await flushOutbox(send, handlers())

    const [item] = await outboxItems()
    expect(item.payload.note).toBe("edited")
    expect(sent).toEqual([["check", "c"]])
  })

  it("stops without signal and sends the rest on the next run", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z"))
    await enqueue(check("d", "2026-11-03T10:30:00Z"))
    let online = false
    const { send, sent } = sender(() => {
      if (!online) throw new Error("Network Error")
      return { accepted: true }
    })

    expect(await flushOutbox(send, handlers())).toBe(false)
    expect((await outboxItems()).map(item => item.id)).toEqual(["c", "d"])

    online = true
    expect(await flushOutbox(send, handlers())).toBe(true)
    expect(sent).toEqual([
      ["check", "c"],
      ["check", "c"],
      ["check", "d"],
    ])
    expect(await outboxItems()).toEqual([])
  })

  it("retries after a server error", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z"))
    const { send } = sender(() => {
      throw answered(502)
    })

    expect(await flushOutbox(send, handlers())).toBe(false)
    expect(await outboxItems()).toHaveLength(1)
  })

  it("drops everything of a closed batch and goes on with other links", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z"))
    await enqueue({ ...check("e", "2026-11-03T10:10:00Z"), token: "other" })
    await enqueue(photo("c", 0))
    const { send, sent } = sender((kind, token) => {
      if (token === "open") throw answered(410)
      return { accepted: true }
    })
    const callbacks = handlers()

    await flushOutbox(send, callbacks)

    expect(callbacks.onClosed).toHaveBeenCalledOnce()
    expect(callbacks.onClosed).toHaveBeenCalledWith("open")
    expect(sent).toEqual([
      ["check", "c"],
      ["check", "e"],
    ])
    expect(await outboxItems()).toEqual([])
  })

  it("keeps a rejected item aside and sends the rest", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z"))
    await enqueue(check("d", "2026-11-03T10:30:00Z"))
    const { send, sent } = sender((kind, token, payload) => {
      if (payload.id === "c") throw answered(400, { found: ["Neplatná volba."] })
      return { accepted: true }
    })
    const callbacks = handlers()

    expect(await flushOutbox(send, callbacks)).toBe(true)
    await flushOutbox(send, callbacks)

    const [left] = await outboxItems()
    expect(left.id).toBe("c")
    expect(left.rejected).toEqual({ found: ["Neplatná volba."] })
    expect(sent).toEqual([
      ["check", "c"],
      ["check", "d"],
    ])
  })

  it("drops the photos of a check that lost to one made later", async () => {
    await enqueue(check("c", "2026-11-03T10:00:00Z"))
    await enqueue(photo("c", 0))
    const { send, sent } = sender(() => ({ accepted: false, check: { id: "winner" } }))
    const callbacks = handlers()

    await flushOutbox(send, callbacks)

    expect(sent).toEqual([["check", "c"]])
    expect(callbacks.onSent).toHaveBeenCalledOnce()
    expect(await outboxItems()).toEqual([])
  })
})
