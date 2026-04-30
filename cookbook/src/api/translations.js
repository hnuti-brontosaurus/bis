import { client } from "./client.js"

export const fetch = () => client.get("/extras/translations/").then(r => r.data)
