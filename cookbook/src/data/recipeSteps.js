import { client } from "./client.js"

/**
 * Per-step photo upload, served by the dedicated /recipe_steps/{id}/
 * endpoint. We can't PATCH the recipe with a partial steps array — its
 * serializer is WritableNested and would delete the steps that aren't
 * included.
 */
export const uploadStepPhoto = (stepId, base64data, onUploadProgress) =>
  client
    .patch(`/recipe_steps/${stepId}/`, { photo: base64data }, { onUploadProgress })
    .then(r => r.data)
