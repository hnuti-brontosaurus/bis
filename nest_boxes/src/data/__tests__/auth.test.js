import { beforeEach, describe, expect, it, vi } from "vitest"
import { createPinia, setActivePinia } from "pinia"

const whoami = vi.fn()
vi.mock("@/data/client.js", () => ({ client: { get: () => whoami() } }))
vi.mock("@/data/errors.js", () => ({ reportError: vi.fn() }))

const { loginUrl, logoutUrl } = await import("@/data/auth.js")
const { requireLogin } = await import("@/router.js")

const managerPage = { fullPath: "/obchuzky/?a=1", meta: { requiresLogin: true } }

describe("login", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.stubGlobal("location", { assign: vi.fn() })
    whoami.mockReset()
  })

  it("goes through the BIS logout and login, back to the same page", () => {
    const url = new URL(loginUrl("/obchuzky/?a=1"), "http://localhost")
    expect(url.pathname).toBe("/logout")
    const login = new URL(url.searchParams.get("next"), "http://localhost")
    expect(login.pathname).toBe("/login")
    expect(login.searchParams.get("next")).toBe("/budky/obchuzky/?a=1")
    expect(logoutUrl("/")).toBe("/logout?next=%2Fbudky%2F")
  })

  it("sends an anonymous visitor of a manager page to the login", async () => {
    whoami.mockResolvedValue({ data: { is_authenticated: false } })
    expect(await requireLogin(managerPage)).toBe(false)
    expect(window.location.assign).toHaveBeenCalledWith(loginUrl("/obchuzky/?a=1"))
  })

  it("lets a signed-in user through", async () => {
    whoami.mockResolvedValue({ data: { is_authenticated: true, managed_area_ids: [] } })
    expect(await requireLogin(managerPage)).toBeUndefined()
    expect(window.location.assign).not.toHaveBeenCalled()
  })

  it("does not redirect when whoami failed, since nobody knows who it is", async () => {
    whoami.mockRejectedValue(new Error("offline"))
    expect(await requireLogin(managerPage)).toBeUndefined()
    expect(window.location.assign).not.toHaveBeenCalled()
  })

  it("leaves public pages alone", async () => {
    expect(await requireLogin({ meta: {} })).toBeUndefined()
    expect(whoami).not.toHaveBeenCalled()
  })
})
