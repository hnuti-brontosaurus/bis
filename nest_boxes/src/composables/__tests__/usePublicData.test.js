import { describe, expect, it, vi } from "vitest"
import { flushPromises } from "@vue/test-utils"
import { ref } from "vue"

const getStatistics = vi.fn(season =>
  Promise.resolve({ season: season ?? 2025, seasons: [2026, 2025] }),
)
vi.mock("@/data/public.js", () => ({
  getStatistics,
  listPublicAreas: () => Promise.resolve([]),
}))
vi.mock("@/data/errors.js", () => ({ reportError: vi.fn() }))

const { usePublicData } = await import("@/composables/usePublicData.js")

describe("usePublicData", () => {
  it("shows the server's default season until another is picked", async () => {
    const { season, statistics } = usePublicData()
    await flushPromises()
    expect(getStatistics.mock.calls).toEqual([[undefined, []]])
    expect(season.value).toBe(2025)

    season.value = 2026
    await flushPromises()
    expect(getStatistics.mock.calls).toEqual([
      [undefined, []],
      [2026, []],
    ])
    expect(statistics.value.season).toBe(2026)
  })

  it("reloads the shown season for other box types", async () => {
    getStatistics.mockClear()
    const types = ref([])
    const { season } = usePublicData(() => types.value)
    await flushPromises()
    season.value = 2026
    await flushPromises()

    types.value = [3]
    await flushPromises()
    expect(getStatistics.mock.calls.at(-1)).toEqual([2026, [3]])
    expect(season.value).toBe(2026)
  })
})
