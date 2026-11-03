import { database } from "@/data/offline.js"

/**
 * @typedef {Object} OutboxItem
 * @property {number} key the order it was saved in, which is the order it is sent in
 * @property {string} token the batch link it goes through
 * @property {"box" | "check" | "photo"} kind
 * @property {string} id the client's id of what it carries; a newer save of
 *   the same thing replaces the queued one in its place
 * @property {Object} payload the request body
 * @property {Object} [rejected] the server's 400 answer; left for the
 *   volunteer to see and skipped by later sends
 */

/** @returns {Promise<OutboxItem[]>} */
export const outboxItems = async () => (await database).getAll("outbox")

const isNewer = (item, queued) =>
  item.kind !== "check" || item.payload.made_at > queued.payload.made_at

export const enqueue = async item => {
  const transaction = (await database).transaction("outbox", "readwrite")
  const queued = (await transaction.store.getAll()).find(
    other => other.kind === item.kind && other.id === item.id,
  )
  if (!queued) await transaction.store.add(item)
  else if (isNewer(item, queued))
    await transaction.store.put({ ...item, key: queued.key })
  await transaction.done
}

const removeWhere = async predicate => {
  const transaction = (await database).transaction("outbox", "readwrite")
  for (const item of await transaction.store.getAll())
    if (predicate(item)) await transaction.store.delete(item.key)
  await transaction.done
}

export const dropToken = token => removeWhere(item => item.token === token)

/**
 * Sends the outbox in order. A request that gets no answer, or a 5xx, stops the run, so
 * nothing overtakes it and it is tried again on the next run; the ids are the
 * client's, so a resend of something the server did store is harmless.
 *
 * - 410: the batch is closed. Everything for its link is dropped.
 * - another error answer: the item is marked rejected and the rest go on.
 * - a check the server did not take, because a check made later won: its
 *   queued photos are dropped, since they have nothing to attach to.
 *
 * @param {Object<string, (token: string, payload: Object) => Promise<Object>>} send by kind
 * @returns {Promise<boolean>} whether the run got through the whole outbox
 */
export const flushOutbox = async (send, { onSent, onClosed, onRejected }) => {
  const closed = new Set()
  const lostChecks = new Set()
  const isSkipped = item =>
    item.rejected ||
    closed.has(item.token) ||
    (item.kind === "photo" && lostChecks.has(item.payload.parent_id))
  for (const item of await outboxItems()) {
    if (isSkipped(item)) continue
    let result
    try {
      result = await send[item.kind](item.token, item.payload)
    } catch (error) {
      if (!error.response || error.response.status >= 500) return false
      if (error.response.status === 410) {
        closed.add(item.token)
        await dropToken(item.token)
        await onClosed(item.token)
      } else {
        const rejected = error.response.data
        await (await database).put("outbox", { ...item, rejected })
        await onRejected({ ...item, rejected })
      }
      continue
    }
    await (await database).delete("outbox", item.key)
    if (item.kind === "check" && !result.accepted) {
      lostChecks.add(item.payload.id)
      await removeWhere(
        other => other.kind === "photo" && other.payload.parent_id === item.payload.id,
      )
    }
    await onSent(item, result)
  }
  return true
}
