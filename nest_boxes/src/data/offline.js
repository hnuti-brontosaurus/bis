import { openDB } from "idb"

// The link payloads by token, and the outbox of what is not sent yet
export const database = openDB("nest_boxes", 1, {
  upgrade(db) {
    db.createObjectStore("links")
    db.createObjectStore("outbox", { keyPath: "key", autoIncrement: true })
  },
})

export const savedLink = async token => (await database).get("links", token)

export const saveLink = async (token, payload) =>
  (await database).put("links", payload, token)

export const forgetLink = async token => (await database).delete("links", token)
