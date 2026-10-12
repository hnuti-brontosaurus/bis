import { client } from "./client.js"

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
