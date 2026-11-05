import { client, fetchAll, upsert } from "./client.js"
import {
  keptPhotos,
  uploadCommentPhoto,
  uploadNewPhotos,
  uploadNotePhoto,
} from "./recipePhotos.js"

export const recipeCommentsApi = {
  list: recipeId => fetchAll(`/recipe_comments/?recipe=${recipeId}`),
  create: async ({ photos, ...comment }) => {
    const { data } = await client.post("/recipe_comments/", comment)
    await uploadNewPhotos(uploadCommentPhoto, data.id, photos)
    return data
  },
  remove: id => client.delete(`/recipe_comments/${id}/`),
}

// One note per user and recipe; saving it empty deletes it.
export const recipeNotesApi = {
  get: async recipeId =>
    (await fetchAll(`/recipe_notes/?recipe=${recipeId}`))[0] ?? null,
  save: async ({ photos, ...note }) => {
    if (!note.note && !photos.length) {
      if (note.id) await client.delete(`/recipe_notes/${note.id}/`)
      return null
    }
    const saved = await upsert("/recipe_notes", { ...note, photos: keptPhotos(photos) })
    await uploadNewPhotos(uploadNotePhoto, saved.id, photos)
    return saved
  },
}
