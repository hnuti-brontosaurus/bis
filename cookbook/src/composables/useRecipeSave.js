import { reactive } from "vue"
import { uploadRecipePhoto, useRecipesStore } from "@/data/recipes.js"
import { uploadIngredientPhoto, uploadStepPhoto } from "@/data/recipeRowPhotos.js"

const isNewUpload = photo => photo && typeof photo === "object" && "base64data" in photo

const ROWS = [
  { kind: "ingredient", key: "ingredients", upload: uploadIngredientPhoto },
  { kind: "step", key: "steps", upload: uploadStepPhoto },
]
const uploaders = {
  recipe: uploadRecipePhoto,
  ...Object.fromEntries(ROWS.map(({ kind, upload }) => [kind, upload])),
}

/**
 * Multi-step recipe save: first PATCH/POST the recipe text without new
 * photos, then upload each photo individually with progress reporting.
 *
 * Why split: a single recipe save with N base64 photos in one JSON body
 * is megabytes per photo and dies on the 30s nginx timeout under slow
 * networks. Per-photo PATCHes are bounded so even if one is slow, the
 * others (and the recipe itself) still land. Failed photos can be
 * retried without re-saving anything else.
 *
 * Public recipes need recipe.photo to validate. If we're uploading the
 * main photo, we save private and PATCH `is_public=true` after the photo
 * lands. The user's intent is preserved and no dummy file is needed.
 */
export function useRecipeSave() {
  const state = reactive({
    phase: "idle",
    uploads: [],
    overallProgress: 0,
    recipeId: null,
  })

  const recipesStore = useRecipesStore()

  let workingRecipe = null
  let originalIsPublic = false
  let savedRecipe = null

  const collectUploads = recipe => {
    const items = []
    if (isNewUpload(recipe.photo)) {
      items.push({
        kind: "recipe",
        index: -1,
        name: recipe.photo.name,
        base64: recipe.photo.base64data,
        status: "pending",
        progress: 0,
      })
    }
    ROWS.forEach(({ kind, key }) =>
      (recipe[key] ?? []).forEach((row, index) => {
        if (isNewUpload(row.photo)) {
          items.push({
            kind,
            key,
            index,
            row,
            name: row.photo.name,
            base64: row.photo.base64data,
            status: "pending",
            progress: 0,
          })
        }
      }),
    )
    return items
  }

  // Replace each new-upload wrapper with whatever the server currently
  // has (the original photo for an existing row, or null for a brand-new
  // one). The Base64FieldMixin treats dicts as SkipField, so existing
  // photos pass through unchanged on the initial save.
  const stripUploads = (recipe, originalRecipe) => {
    const out = JSON.parse(JSON.stringify(recipe))
    if (isNewUpload(out.photo)) {
      out.photo = originalRecipe?.photo ?? null
    }
    ROWS.forEach(({ key }) => {
      out[key] = (out[key] ?? []).map(row => {
        if (!isNewUpload(row.photo)) return row
        const orig = originalRecipe?.[key]?.find(r => r.id === row.id)
        return { ...row, photo: orig?.photo ?? null }
      })
    })
    return out
  }

  const computeOverallProgress = () => {
    if (!state.uploads.length) return 100
    const total = state.uploads.reduce((sum, u) => sum + (u.progress || 0), 0)
    return Math.round(total / state.uploads.length)
  }

  const runUpload = async upload => {
    upload.status = "uploading"
    upload.progress = 0
    upload.error = undefined
    const onProgress = e => {
      const total = e.total || e.loaded
      upload.progress = total ? Math.round((e.loaded / total) * 100) : 0
      state.overallProgress = computeOverallProgress()
    }
    try {
      await uploaders[upload.kind](upload.targetId, upload.base64, onProgress)
      upload.status = "done"
      upload.progress = 100
    } catch (e) {
      upload.status = "failed"
      upload.error = e
    } finally {
      state.overallProgress = computeOverallProgress()
    }
  }

  const runSequentially = async items => {
    for (const upload of items) {
      await runUpload(upload)
    }
  }

  const finalize = async () => {
    const allDone = state.uploads.every(u => u.status === "done")
    if (allDone && originalIsPublic && !savedRecipe.is_public) {
      state.phase = "publishing"
      savedRecipe = await recipesStore.save({
        id: savedRecipe.id,
        is_public: true,
      })
    } else if (state.uploads.length) {
      // Refresh the cache so the new photos show up on the recipe page.
      savedRecipe = await recipesStore.fetchOne(savedRecipe.id)
    }
    state.phase = allDone ? "done" : "partial"
  }

  const run = async recipe => {
    workingRecipe = recipe
    originalIsPublic = !!recipe.is_public
    const originalRecipe = recipe.id ? recipesStore.byId[recipe.id] : null

    state.uploads = collectUploads(recipe)
    state.overallProgress = 0
    state.recipeId = null

    state.phase = "saving-text"
    const stripped = stripUploads(recipe, originalRecipe)
    if (state.uploads.some(u => u.kind === "recipe") && stripped.is_public) {
      // Validator requires recipe.photo when public; we'll flip it back
      // on after the photo upload.
      stripped.is_public = false
    }
    savedRecipe = await recipesStore.save(stripped)
    state.recipeId = savedRecipe.id

    // Sync server-assigned IDs back so a retry hits the right rows even
    // if savedRecipe gets overwritten by a later fetchOne (which only
    // populates the cache, not the upload targets).
    workingRecipe.id = savedRecipe.id
    ROWS.forEach(({ key }) =>
      (savedRecipe[key] ?? []).forEach((r, i) => {
        if (workingRecipe[key]?.[i]) workingRecipe[key][i].id = r.id
      }),
    )
    for (const upload of state.uploads) {
      upload.targetId =
        upload.kind === "recipe"
          ? savedRecipe.id
          : savedRecipe[upload.key]?.[upload.index]?.id
    }

    if (!state.uploads.length) {
      state.phase = "done"
      return savedRecipe
    }

    state.phase = "uploading"
    await runSequentially(state.uploads)
    await finalize()
    return savedRecipe
  }

  const retryFailed = async () => {
    const failed = state.uploads.filter(u => u.status === "failed")
    if (!failed.length) return
    state.phase = "uploading"
    state.overallProgress = computeOverallProgress()
    await runSequentially(failed)
    await finalize()
  }

  return { state, run, retryFailed }
}
