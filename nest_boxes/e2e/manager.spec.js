import { choose, expect, test } from "./support/manager.js"

// The manager pages are a desktop tool; the phone runs the check form only
const desktopOnly = () =>
  test.skip(({ isMobile }) => isMobile, "the manager pages are for a desktop")

const row = (page, box) => page.locator(`[data-box-row="${box.id}"]`)

test.describe("the area page", () => {
  desktopOnly()

  test("creates a batch with the suggested boxes and moves one out", async ({
    page,
    area,
  }) => {
    await page.goto(`/budky/oblast/${area.id}/`)
    await expect(page.getByRole("heading", { name: area.name })).toBeVisible()
    await expect(page.getByText("Žádná otevřená dávka kontrol.")).toBeVisible()

    await page.getByRole("button", { name: "Vytvořit dávku" }).click()
    await expect(page.getByText("Navržených budek: 3")).toBeVisible()
    await page.getByLabel("Název").fill("Podzim E2E manažer")
    await page
      .getByRole("dialog")
      .getByRole("button", { name: "Vytvořit dávku" })
      .click()

    const batch = page.getByTestId("batch-section")
    await expect(batch.getByText("0 z 3")).toBeVisible()
    await expect(batch.getByTestId("batch-link")).toContainText("/budky/d/")
    await expect(page.getByText("V této dávce · 3")).toBeVisible()

    await page.getByRole("button", { name: "Vyřadit z dávky 3" }).click()
    await expect(page.getByText("V této dávce · 2")).toBeVisible()
    await expect(page.getByText("Mimo dávku · 1")).toBeVisible()
    await expect(batch.getByText("0 z 2")).toBeVisible()
  })

  test("filters the boxes and plans a new one", async ({ page, area }) => {
    await page.goto(`/budky/oblast/${area.id}/`)
    await page.getByPlaceholder("Hledat označení").fill("2")
    await expect(page.getByText("Budky · 1")).toBeVisible()
    await page.getByPlaceholder("Hledat označení").fill("")

    await page.getByRole("button", { name: "Naplánovat budku" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByLabel("Označení", { exact: true }).fill("P9")
    await dialog.getByTestId("map").click()
    await expect(dialog.getByTestId("coordinates")).toBeVisible()
    await dialog.getByRole("button", { name: "Naplánovat" }).click()
    await expect(page.getByText("Budka P9 je naplánovaná.")).toBeVisible()
    await expect(page.locator("[data-box-row]", { hasText: "P9" })).toContainText(
      "plánovaná",
    )
  })
})

test.describe("a manager's check", () => {
  desktopOnly()

  test("is entered, edited and deleted", async ({ page, area }) => {
    await page.goto(`/budky/oblast/${area.id}/`)
    await row(page, area.boxes["1"])
      .getByRole("button", { name: "Zkontrolovat" })
      .click()
    await expect(page.getByRole("heading", { name: "Kontrola budky 1" })).toBeVisible()

    await page.getByRole("button", { name: "Uložit kontrolu" }).click()
    await expect(page.getByText("Vyber, co bylo uvnitř.")).toBeVisible()
    await page.getByRole("radio", { name: "Prázdná" }).click()
    await page.getByRole("button", { name: "Uložit kontrolu" }).click()

    const history = page.getByTestId("check-history")
    await expect(history).toContainText("vyčištěno · prázdná")
    await expect(history).toContainText("potvrzeno")

    await history.getByRole("link", { name: /Upravit kontrolu/ }).click()
    await expect(
      page.getByRole("heading", { name: "Úprava kontroly budky 1" }),
    ).toBeVisible()
    await page.getByRole("radio", { name: "Obsazená" }).click()
    await page.getByRole("checkbox", { name: "sýkora koňadra" }).click()
    await page.getByRole("button", { name: "Uložit kontrolu" }).click()
    await expect(history).toContainText("vyčištěno · sýkora koňadra")

    await history.getByRole("link", { name: /Upravit kontrolu/ }).click()
    await page.getByRole("button", { name: "Smazat" }).click()
    await page.getByRole("button", { name: "Potvrdit" }).click()
    await expect(page.getByText("Budka zatím nemá žádnou kontrolu.")).toBeVisible()
  })
})

test.describe("the batch page", () => {
  desktopOnly()

  test("takes checks from paper, edits one in place and confirms the batch", async ({
    page,
    api,
    area,
  }) => {
    const batch = await api.post("/batches/", {
      area_id: area.id,
      name: "Papír E2E",
      box_ids: [area.boxes["1"].id, area.boxes["2"].id],
    })
    await page.goto(`/budky/davka/${batch.id}/`)
    await expect(page.getByRole("heading", { name: "Papír E2E" })).toBeVisible()

    const add = page.getByTestId("add-check")
    await choose(page, add.getByLabel("Budka nové kontroly"), "1")
    await add.getByRole("radio", { name: "Prázdná" }).click()
    await add.getByRole("button", { name: "Zapsat kontrolu" }).click()
    await expect(page.getByText("Kontrola budky 1 je zapsaná.")).toBeVisible()

    await choose(page, add.getByLabel("Budka nové kontroly"), "2")
    await add.getByRole("switch", { name: "Budka nalezena" }).click()
    await add.getByRole("button", { name: "Zapsat kontrolu" }).click()

    const checks = page.getByTestId("batch-checks")
    await expect(checks.locator("[data-check-row]")).toHaveCount(2)
    await expect(page.getByText("Na co se podívat")).toBeVisible()
    await expect(page.locator(".highlight", { hasText: "Nenalezena" })).toBeVisible()

    await checks.getByRole("button", { name: "Upravit kontrolu 1" }).click()
    const form = checks.getByTestId("check-form")
    await form.getByRole("radio", { name: "Obsazená" }).click()
    await form.getByRole("checkbox", { name: "vosy" }).click()
    await form.getByRole("button", { name: "Uložit úpravu" }).click()
    await expect(checks.locator('[data-check-row="1"]')).toContainText("vosy")

    await page.getByRole("button", { name: "Potvrdit a uzavřít" }).click()
    await page.getByRole("button", { name: "Potvrdit", exact: true }).click()
    await expect(page.getByText(/potvrzená \d/)).toBeVisible()
    await expect(checks.locator('[data-check-row="1"]')).toContainText("potvrzeno")

    await page.goto(`/budky/budka/${area.boxes["2"].id}/`)
    await expect(page.getByText("nenalezená", { exact: true })).toBeVisible()
  })
})

test.describe("the box page", () => {
  desktopOnly()

  test("ends a box", async ({ page, area }) => {
    await page.goto(`/budky/budka/${area.boxes["3"].id}/`)
    await expect(page.getByRole("heading", { name: "3", exact: true })).toBeVisible()
    await page.getByRole("button", { name: "Ukončit budku" }).click()
    const dialog = page.getByRole("dialog")
    await dialog.getByRole("radio", { name: "dosloužila nebo je zničená" }).click()
    await dialog.getByRole("button", { name: "Ukončit budku" }).click()
    await expect(page.getByText("Budka je ukončená.")).toBeVisible()
    await expect(page.getByText("zaniklá", { exact: true })).toBeVisible()
    await expect(page.getByRole("button", { name: "Zadat kontrolu" })).toBeHidden()
  })
})

test("the header leads to the open batches", async ({ page, api, area }) => {
  await api.post("/batches/", { area_id: area.id, name: "Počítaná" })
  await page.goto("/budky/")
  await expect(page.getByTestId("open-batches").locator("b")).toHaveText(/^[1-9]\d*$/)
  await page.getByTestId("open-batches").click()
  await expect(page.getByRole("heading", { name: "Otevřené dávky" })).toBeVisible()
  await expect(
    page
      .getByTestId("open-batch")
      .filter({ hasText: "Počítaná" })
      .filter({ hasText: area.name }),
  ).toBeVisible()
})

test.describe("the map of areas", () => {
  desktopOnly()

  test("counts the season states per area and filters them", async ({
    page,
    api,
    area,
  }) => {
    const check = (box, values) =>
      api.post("/checks/", {
        box_id: box.id,
        date: new Date().toISOString().slice(0, 10),
        found: "found",
        cleaning: "cleaned",
        contents: ["nothing"],
        ...values,
      })
    await check(area.boxes["1"], {})
    await check(area.boxes["2"], { found: "not_found", cleaning: "", contents: [] })

    await page.goto("/budky/mapa/")
    const states = page.getByTestId("season-states")
    const areaRow = states.locator("tr", { hasText: area.name })
    await expect(areaRow.locator("td.num")).toHaveText(["1", "1", "1", "0"])

    await choose(page, page.getByRole("button", { name: "Stav" }), "Pozornost")
    await expect(areaRow.locator("td.num")).toHaveText(["0", "1", "0", "0"])

    await page.getByRole("radio", { name: "Statistiky" }).click()
    await expect(page.getByTestId("statistics")).toBeVisible()
  })
})
