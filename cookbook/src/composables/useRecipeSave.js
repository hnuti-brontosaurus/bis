import { reactive } from "vue"
import { useRecipesStore } from "@/data/recipes.js"
import {
  uploadIngredientPhoto,
  uploadRecipePhoto,
  uploadStepPhoto,
} from "@/data/recipePhotos.js"

// A gallery entry is `{ id, order, photo }` once saved, or `{ photo }` with
// the n-upload file info as `photo` until it is uploaded.
const isNewUpload = entry => entry.photo?.file instanceof File

const GALLERIES = [
  { kind: "recipe", upload: uploadRecipePhoto, parents: recipe => [recipe] },
  {
    kind: "ingredient",
    upload: uploadIngredientPhoto,
    parents: recipe => recipe.ingredients ?? [],
  },
  { kind: "step", upload: uploadStepPhoto, parents: recipe => recipe.steps ?? [] },
]
const uploaders = Object.fromEntries(
  GALLERIES.map(({ kind, upload }) => [kind, upload]),
)

const eachGallery = (recipe, callback) =>
  GALLERIES.forEach(gallery =>
    gallery
      .parents(recipe)
      .forEach((parent, index) => callback(parent, gallery, index)),
  )

// Read here rather than when the file is picked: a collapsed step or
// ingredient row unmounts its form, so nothing there is sure to run.
const toDataUri = file =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const [, base64] = reader.result.split(",")
      resolve(`data:${file.type};filename=${file.name};base64,${base64}`)
    }
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })

/**
 * Multi-step recipe save: first PATCH/POST the recipe text with only the
 * already saved photos, then upload each new photo on its own with
 * progress reporting.
 *
 * Why split: a single recipe save with N base64 photos in one JSON body
 * is megabytes per photo and dies on the 30s nginx timeout under slow
 * networks. Per-photo POSTs are bounded so even if one is slow, the
 * others (and the recipe itself) still land. Failed photos can be
 * retried without re-saving anything else.
 *
 * Public recipes need a photo to validate. If we're uploading recipe
 * photos, we save private and PATCH `is_public=true` after they land.
 * The user's intent is preserved and no dummy file is needed.
 */
export function useRecipeSave() {
  const state = reactive({
    phase: "idle",
    uploads: [],
    overallProgress: 0,
    recipeId: null,
  })

  const recipesStore = useRecipesStore()

  let originalIsPublic = false
  let savedRecipe = null

  const collectUploads = recipe => {
    const items = []
    eachGallery(recipe, (parent, { kind }, index) =>
      (parent.photos ?? []).forEach((entry, order) => {
        entry.order = order
        if (isNewUpload(entry)) {
          items.push({ kind, index, parent, entry, status: "pending", progress: 0 })
        }
      }),
    )
    return items
  }

  // The recipe serializer deletes the saved photos missing from a gallery
  // and leaves the file of a listed one alone, so this keeps, reorders and
  // deletes the saved photos without sending any image data.
  const withoutUploads = recipe => {
    const out = JSON.parse(JSON.stringify(recipe))
    eachGallery(recipe, (parent, gallery, index) => {
      gallery.parents(out)[index].photos = (parent.photos ?? [])
        .filter(entry => !isNewUpload(entry))
        .map(({ id, order }) => ({ id, order }))
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
      const base64 = await toDataUri(upload.entry.photo.file)
      const saved = await uploaders[upload.kind](
        upload.parent.id,
        upload.entry.order,
        base64,
        onProgress,
      )
      // Saving the form again must keep this photo, not upload it twice.
      Object.assign(upload.entry, saved)
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
    originalIsPublic = !!recipe.is_public

    state.uploads = collectUploads(recipe)
    state.overallProgress = 0
    state.recipeId = null

    state.phase = "saving-text"
    const stripped = withoutUploads(recipe)
    if (state.uploads.some(u => u.kind === "recipe") && stripped.is_public) {
      // Validator requires a recipe photo when public; we'll flip it back
      // on after the photo upload.
      stripped.is_public = false
    }
    savedRecipe = await recipesStore.save(stripped)
    state.recipeId = savedRecipe.id

    // The uploads target the working recipe's rows, so give them the
    // server-assigned ids; a retry or a second save then hits the same rows.
    GALLERIES.forEach(({ parents }) => {
      const workingRows = parents(recipe)
      parents(savedRecipe).forEach((row, i) => {
        if (workingRows[i]) workingRows[i].id = row.id
      })
    })

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
