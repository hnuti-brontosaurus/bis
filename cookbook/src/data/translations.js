import { client } from "./client.js"

export const translationsApi = {
  fetch: () => client.get("/extras/translations/").then(r => r.data),
}
