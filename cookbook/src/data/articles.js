import { client } from "./client.js"

export const getArticle = slug => client.get(`/articles/${slug}/`).then(r => r.data)

export const saveArticle = ({ slug, content }) =>
  client.patch(`/articles/${slug}/`, { content }).then(r => r.data)
