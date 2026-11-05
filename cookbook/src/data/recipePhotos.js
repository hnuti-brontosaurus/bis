import { client } from "./client.js"
import { toDataUri } from "@/contrib/composables/helpers.js"

/**
 * Adds one photo to a gallery. A recipe save only keeps, reorders and
 * deletes photos; new ones are sent one by one through these endpoints, so
 * no single request carries more than one photo's worth of base64.
 */
const uploadPhoto = endpoint => (parentId, order, base64data, onUploadProgress) =>
  client
    .post(
      `/${endpoint}/`,
      { parent_id: parentId, order, photo: base64data },
      { onUploadProgress },
    )
    .then(r => r.data)

export const uploadRecipePhoto = uploadPhoto("recipe_photos")
export const uploadIngredientPhoto = uploadPhoto("recipe_ingredient_photos")
export const uploadStepPhoto = uploadPhoto("recipe_step_photos")
export const uploadTipPhoto = uploadPhoto("recipe_tip_photos")
export const uploadCommentPhoto = uploadPhoto("recipe_comment_photos")
export const uploadNotePhoto = uploadPhoto("recipe_note_photos")

// A gallery entry is `{ id, order, photo }` once saved, or `{ photo }` with
// the n-upload file info as `photo` until it is uploaded.
const isSaved = entry => entry.id != null

export const keptPhotos = gallery =>
  gallery.map((entry, order) => ({ id: entry.id, order })).filter(isSaved)

export const uploadNewPhotos = async (upload, parentId, gallery) => {
  for (const [order, entry] of gallery.entries())
    if (!isSaved(entry))
      await upload(parentId, order, await toDataUri(entry.photo.file))
}
