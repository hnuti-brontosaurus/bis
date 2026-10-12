import { client } from "./client.js"

/**
 * Per-row photo uploads, served by the dedicated /recipe_steps/{id}/ and
 * /recipe_ingredients/{id}/ endpoints. We can't PATCH the recipe with a
 * partial rows array — its serializer is WritableNested and would delete
 * the rows that aren't included.
 */
const uploadRowPhoto = endpoint => (rowId, base64data, onUploadProgress) =>
  client
    .patch(`/${endpoint}/${rowId}/`, { photo: base64data }, { onUploadProgress })
    .then(r => r.data)

export const uploadStepPhoto = uploadRowPhoto("recipe_steps")
export const uploadIngredientPhoto = uploadRowPhoto("recipe_ingredients")
