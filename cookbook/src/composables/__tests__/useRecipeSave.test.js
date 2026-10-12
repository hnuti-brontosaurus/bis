import { describe, it, expect, beforeEach, vi } from "vitest"

const recipesStore = {
  byId: {},
  save: vi.fn(),
  fetchOne: vi.fn(),
}

vi.mock("@/data/recipes.js", () => ({
  useRecipesStore: () => recipesStore,
}))

vi.mock("@/data/recipePhotos.js", () => ({
  uploadRecipePhoto: vi.fn(),
  uploadIngredientPhoto: vi.fn(),
  uploadStepPhoto: vi.fn(),
}))

import { useRecipeSave } from "../useRecipeSave.js"
import {
  uploadIngredientPhoto,
  uploadRecipePhoto,
  uploadStepPhoto,
} from "@/data/recipePhotos.js"

const picked = (name = "x.png") => ({
  photo: { id: name, name, file: new File(["x"], name, { type: "image/png" }) },
})
const saved = id => ({ id, order: 0, photo: { small: `/${id}.png` } })
const dataUri = name => `data:image/png;filename=${name};base64,eA==`

const buildRecipe = ({
  id,
  isPublic = false,
  photos = [],
  steps = [],
  ingredients = [],
}) => ({
  ...(id != null ? { id } : {}),
  is_public: isPublic,
  photos,
  steps,
  ingredients,
  tips: [],
})

beforeEach(() => {
  recipesStore.byId = {}
  recipesStore.save.mockReset()
  recipesStore.fetchOne.mockReset()
  uploadRecipePhoto.mockReset()
  uploadIngredientPhoto.mockReset()
  uploadStepPhoto.mockReset()
})

describe("useRecipeSave", () => {
  it("saves text without uploads when no new photos", async () => {
    recipesStore.save.mockResolvedValue({ id: 7, steps: [] })
    const { state, run } = useRecipeSave()

    const result = await run(buildRecipe({ id: 7, photos: [saved(1)] }))

    expect(state.uploads).toEqual([])
    expect(state.phase).toBe("done")
    expect(result.id).toBe(7)
    expect(recipesStore.save).toHaveBeenCalledTimes(1)
    expect(recipesStore.save.mock.calls[0][0].photos).toEqual([{ id: 1, order: 0 }])
    expect(uploadRecipePhoto).not.toHaveBeenCalled()
  })

  it("saves the kept photos in gallery order and uploads the new ones after", async () => {
    recipesStore.save.mockResolvedValue({
      id: 9,
      is_public: false,
      steps: [{ id: 100 }],
    })
    recipesStore.fetchOne.mockResolvedValue({ id: 9 })
    uploadRecipePhoto.mockResolvedValue(saved(2))
    uploadStepPhoto.mockResolvedValue(saved(3))

    const recipe = buildRecipe({
      id: 9,
      photos: [picked("r.png"), saved(1)],
      steps: [{ name: "boil", photos: [picked("s.png")] }],
    })

    const { state, run } = useRecipeSave()
    await run(recipe)

    const sent = recipesStore.save.mock.calls[0][0]
    expect(sent.photos).toEqual([{ id: 1, order: 1 }])
    expect(sent.steps[0].photos).toEqual([])

    expect(uploadRecipePhoto).toHaveBeenCalledWith(
      9,
      0,
      dataUri("r.png"),
      expect.any(Function),
    )
    expect(uploadStepPhoto).toHaveBeenCalledWith(
      100,
      0,
      dataUri("s.png"),
      expect.any(Function),
    )
    expect(state.phase).toBe("done")
  })

  it("uploads ingredient photos to the ingredient rows", async () => {
    recipesStore.save.mockResolvedValue({
      id: 4,
      ingredients: [{ id: 40 }, { id: 41 }],
    })
    recipesStore.fetchOne.mockResolvedValue({ id: 4 })
    uploadIngredientPhoto.mockResolvedValue(saved(5))

    const recipe = buildRecipe({
      ingredients: [{}, { photos: [picked("a.png"), picked("b.png")] }],
    })

    const { run, state } = useRecipeSave()
    await run(recipe)

    expect(recipesStore.save.mock.calls[0][0].ingredients[1].photos).toEqual([])
    expect(uploadIngredientPhoto.mock.calls.map(call => call.slice(0, 3))).toEqual([
      [41, 0, dataUri("a.png")],
      [41, 1, dataUri("b.png")],
    ])
    expect(uploadStepPhoto).not.toHaveBeenCalled()
    expect(recipe.ingredients.map(row => row.id)).toEqual([40, 41])
    expect(state.phase).toBe("done")
  })

  it("turns an uploaded photo into a saved one, so saving again keeps it", async () => {
    recipesStore.save.mockResolvedValue({ id: 6 })
    recipesStore.fetchOne.mockResolvedValue({ id: 6 })
    uploadRecipePhoto.mockResolvedValue({ id: 60, order: 0, photo: { small: "/60" } })

    const recipe = buildRecipe({ id: 6, photos: [picked()] })
    const { run } = useRecipeSave()
    await run(recipe)
    await run(recipe)

    expect(uploadRecipePhoto).toHaveBeenCalledTimes(1)
    expect(recipesStore.save.mock.calls[1][0].photos).toEqual([{ id: 60, order: 0 }])
  })

  it("forces is_public=false when uploading a recipe photo on a public recipe", async () => {
    recipesStore.save.mockResolvedValueOnce({ id: 1, is_public: false, steps: [] })
    recipesStore.save.mockResolvedValueOnce({ id: 1, is_public: true, steps: [] })
    recipesStore.fetchOne.mockResolvedValue({ id: 1 })
    uploadRecipePhoto.mockResolvedValue(saved(10))

    const { run, state } = useRecipeSave()
    await run(buildRecipe({ id: 1, isPublic: true, photos: [picked()] }))

    expect(recipesStore.save).toHaveBeenCalledTimes(2)
    expect(recipesStore.save.mock.calls[0][0].is_public).toBe(false)
    expect(recipesStore.save.mock.calls[1][0]).toEqual({ id: 1, is_public: true })
    expect(state.phase).toBe("done")
  })

  it("does not flip is_public when an upload fails", async () => {
    recipesStore.save.mockResolvedValueOnce({ id: 2, is_public: false, steps: [] })
    recipesStore.fetchOne.mockResolvedValue({ id: 2 })
    uploadRecipePhoto.mockRejectedValue(new Error("network down"))

    const { run, state } = useRecipeSave()
    await run(buildRecipe({ id: 2, isPublic: true, photos: [picked()] }))

    expect(recipesStore.save).toHaveBeenCalledTimes(1)
    expect(state.phase).toBe("partial")
    expect(state.uploads[0].status).toBe("failed")
  })

  it("retryFailed only re-runs failed uploads and resolves to done on success", async () => {
    recipesStore.save.mockResolvedValueOnce({
      id: 3,
      is_public: false,
      steps: [{ id: 30 }, { id: 31 }],
    })
    recipesStore.fetchOne.mockResolvedValue({ id: 3 })
    uploadStepPhoto
      .mockResolvedValueOnce(saved(1)) // first step ok
      .mockRejectedValueOnce(new Error("flaky")) // second step fails
      .mockResolvedValueOnce(saved(2)) // retry succeeds

    const recipe = buildRecipe({
      id: 3,
      steps: [
        { id: 30, photos: [picked("a.png")] },
        { id: 31, photos: [picked("b.png")] },
      ],
    })

    const { run, retryFailed, state } = useRecipeSave()
    await run(recipe)

    expect(state.phase).toBe("partial")
    expect(state.uploads.map(u => u.status)).toEqual(["done", "failed"])

    await retryFailed()

    expect(uploadStepPhoto).toHaveBeenCalledTimes(3)
    expect(uploadStepPhoto.mock.calls[2][0]).toBe(31)
    expect(state.phase).toBe("done")
    expect(state.uploads.map(u => u.status)).toEqual(["done", "done"])
  })

  it("propagates text-save failure (caller handles it)", async () => {
    const err = Object.assign(new Error("400"), { response: { status: 400 } })
    recipesStore.save.mockRejectedValue(err)
    const { run } = useRecipeSave()

    await expect(run(buildRecipe({ photos: [picked()] }))).rejects.toBe(err)
    expect(uploadRecipePhoto).not.toHaveBeenCalled()
  })
})
