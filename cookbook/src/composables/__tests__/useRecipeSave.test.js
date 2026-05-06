import { describe, it, expect, beforeEach, vi } from "vitest"

const recipesStore = {
  byId: {},
  save: vi.fn(),
  fetchOne: vi.fn(),
}

vi.mock("@/data/recipes.js", () => ({
  useRecipesStore: () => recipesStore,
  uploadRecipePhoto: vi.fn(),
}))

vi.mock("@/data/recipeSteps.js", () => ({
  uploadStepPhoto: vi.fn(),
}))

import { useRecipeSave } from "../useRecipeSave.js"
import { uploadRecipePhoto } from "@/data/recipes.js"
import { uploadStepPhoto } from "@/data/recipeSteps.js"

const wrapper = (base = "data:image/png;filename=x.png;base64,xxx", file = {}) => ({
  base64data: base,
  file,
  type: "image/png",
  name: "x.png",
})

const buildRecipe = ({ id, isPublic = false, photo = null, steps = [] } = {}) => ({
  ...(id != null ? { id } : {}),
  is_public: isPublic,
  photo,
  steps,
  ingredients: [],
  tips: [],
})

beforeEach(() => {
  recipesStore.byId = {}
  recipesStore.save.mockReset()
  recipesStore.fetchOne.mockReset()
  uploadRecipePhoto.mockReset()
  uploadStepPhoto.mockReset()
})

describe("useRecipeSave", () => {
  it("saves text without uploads when no new photos", async () => {
    recipesStore.save.mockResolvedValue({ id: 7, steps: [] })
    const { state, run } = useRecipeSave()

    const saved = await run(buildRecipe({ id: 7 }))

    expect(state.uploads).toEqual([])
    expect(state.phase).toBe("done")
    expect(saved.id).toBe(7)
    expect(recipesStore.save).toHaveBeenCalledTimes(1)
    expect(uploadRecipePhoto).not.toHaveBeenCalled()
    expect(uploadStepPhoto).not.toHaveBeenCalled()
  })

  it("strips new uploads from the initial save and uploads them after", async () => {
    recipesStore.save.mockResolvedValue({
      id: 9,
      is_public: false,
      steps: [{ id: 100, name: "boil", order: 0 }],
    })
    recipesStore.fetchOne.mockResolvedValue({ id: 9 })
    uploadRecipePhoto.mockResolvedValue({})
    uploadStepPhoto.mockResolvedValue({})

    const recipe = buildRecipe({
      id: 9,
      isPublic: false,
      photo: wrapper("data:image/png;filename=r.png;base64,RR"),
      steps: [
        {
          id: 100,
          name: "boil",
          order: 0,
          photo: wrapper("data:image/png;filename=s.png;base64,SS"),
        },
      ],
    })

    const { state, run } = useRecipeSave()
    await run(recipe)

    const sent = recipesStore.save.mock.calls[0][0]
    expect(sent.photo).toBe(null)
    expect(sent.steps[0].photo).toBe(null)

    expect(uploadRecipePhoto).toHaveBeenCalledWith(
      9,
      "data:image/png;filename=r.png;base64,RR",
      expect.any(Function),
    )
    expect(uploadStepPhoto).toHaveBeenCalledWith(
      100,
      "data:image/png;filename=s.png;base64,SS",
      expect.any(Function),
    )
    expect(state.phase).toBe("done")
  })

  it("preserves existing server photos for steps that aren't being re-uploaded", async () => {
    recipesStore.byId = {
      5: {
        id: 5,
        steps: [
          { id: 50, photo: { medium: "/old.png" } },
          { id: 51, photo: null },
        ],
      },
    }
    recipesStore.save.mockResolvedValue({
      id: 5,
      steps: [{ id: 50 }, { id: 51 }],
    })
    recipesStore.fetchOne.mockResolvedValue({ id: 5 })
    uploadStepPhoto.mockResolvedValue({})

    const recipe = buildRecipe({
      id: 5,
      steps: [
        { id: 50, photo: wrapper() },
        { id: 51, photo: { medium: "/keep.png" } },
      ],
    })

    const { run } = useRecipeSave()
    await run(recipe)

    const sent = recipesStore.save.mock.calls[0][0]
    expect(sent.steps[0].photo).toEqual({ medium: "/old.png" })
    expect(sent.steps[1].photo).toEqual({ medium: "/keep.png" })
  })

  it("forces is_public=false when uploading the main photo on a public recipe", async () => {
    recipesStore.save.mockResolvedValueOnce({ id: 1, is_public: false, steps: [] })
    recipesStore.save.mockResolvedValueOnce({ id: 1, is_public: true, steps: [] })
    recipesStore.fetchOne.mockResolvedValue({ id: 1 })
    uploadRecipePhoto.mockResolvedValue({})

    const { run, state } = useRecipeSave()
    await run(buildRecipe({ id: 1, isPublic: true, photo: wrapper() }))

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
    await run(buildRecipe({ id: 2, isPublic: true, photo: wrapper() }))

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
      .mockResolvedValueOnce({}) // first step ok
      .mockRejectedValueOnce(new Error("flaky")) // second step fails
      .mockResolvedValueOnce({}) // retry succeeds

    const recipe = buildRecipe({
      id: 3,
      steps: [
        { id: 30, photo: wrapper("data:image/png;filename=a;base64,A") },
        { id: 31, photo: wrapper("data:image/png;filename=b;base64,B") },
      ],
    })

    const { run, retryFailed, state } = useRecipeSave()
    await run(recipe)

    expect(state.phase).toBe("partial")
    expect(state.uploads.map(u => u.status)).toEqual(["done", "failed"])

    await retryFailed()

    expect(uploadStepPhoto).toHaveBeenCalledTimes(3)
    expect(state.phase).toBe("done")
    expect(state.uploads.map(u => u.status)).toEqual(["done", "done"])
  })

  it("propagates text-save failure (caller handles it)", async () => {
    const err = Object.assign(new Error("400"), { response: { status: 400 } })
    recipesStore.save.mockRejectedValue(err)
    const { run } = useRecipeSave()

    await expect(run(buildRecipe({ photo: wrapper() }))).rejects.toBe(err)
    expect(uploadRecipePhoto).not.toHaveBeenCalled()
  })
})
