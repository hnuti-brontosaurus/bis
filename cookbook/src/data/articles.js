import { client } from "./client.js"

export const getArticle = slug => client.get(`/articles/${slug}/`).then(r => r.data)

export const saveArticle = ({ slug, content }) =>
  client.patch(`/articles/${slug}/`, { content }).then(r => r.data)

export const uploadArticleImage = (slug, image) =>
  client.post("/article_images/", { article: slug, image }).then(r => r.data.src)
