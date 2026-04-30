import { client, fetchAll, upsert } from "./client.js"

const path = "/chefs"

export const list = () => fetchAll(`${path}/`)
export const get = id => client.get(`${path}/${id}/`).then(r => r.data)
export const save = chef => upsert(path, chef)
