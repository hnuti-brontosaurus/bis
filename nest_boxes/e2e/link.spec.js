import { expect, test } from "@playwright/test"

const CLOSED_LINK = "/budky/d/00000000-0000-4000-8000-000000000002/"
// Fixed by backend/nest_boxes/e2e_seed.py, which global-setup.js runs once
const OPEN_TOKEN = "00000000-0000-4000-8000-000000000001"
const OPEN_LINK = `/budky/d/${OPEN_TOKEN}/`
const BOX_IDS = [
  "00000000-0000-4000-8000-000000000011",
  "00000000-0000-4000-8000-000000000012",
]

const checkEmpty = async (page, boxName) => {
  await page
    .getByTestId("box-list")
    .locator(".item", { hasText: boxName })
    .getByRole("button", { name: "Zkontrolovat" })
    .click()
  await expect(page.getByRole("banner").getByText(`Budka ${boxName}`)).toBeVisible()
  await page.getByRole("radio", { name: "Prázdná" }).click()
  await page.getByRole("button", { name: "Uložit kontrolu" }).click()
  await expect(page.getByTestId("box-list")).toBeVisible()
}

test.describe("a volunteer's batch link", () => {
  // One project only: both would check the same seeded boxes
  test.skip(({ isMobile }) => !isMobile, "volunteers are on phones")

  test("takes checks online and offline and sends them when the signal is back", async ({
    page,
    context,
    request,
  }) => {
    await page.goto(OPEN_LINK)
    await expect(
      page.getByRole("heading", { name: "Díky, že jdeš čistit budky" }),
    ).toBeVisible()
    await page.getByLabel("Přezdívka").fill("Sýkorka")
    await page.getByLabel("E-mail").fill("sykorka@example.com")
    await page.getByRole("button", { name: "Pokračovat na mapu" }).click()

    await expect(page.getByTestId("remaining")).toHaveText("zbývá 3 z 3")
    await checkEmpty(page, "1")
    await expect(page.getByTestId("remaining")).toHaveText("zbývá 2 z 3")
    await expect(page.getByText(/čeká|čekají/)).toBeHidden()

    await context.setOffline(true)
    await checkEmpty(page, "2")
    await expect(page.getByText("1 čeká")).toBeVisible()
    await expect(page.getByTestId("remaining")).toHaveText("zbývá 1 z 3")

    await context.setOffline(false)
    await expect(page.getByText("1 čeká")).toBeHidden()

    const payload = await (
      await request.get(`/api/nest_boxes/links/${OPEN_TOKEN}/`)
    ).json()
    expect(payload.checks.map(check => check.box_id).sort()).toEqual(BOX_IDS)
    expect(payload.checks.every(check => check.volunteer_nickname === "Sýkorka")).toBe(
      true,
    )
  })

  test("says when the batch is closed", async ({ page }) => {
    await page.goto(CLOSED_LINK)
    await expect(page.getByRole("heading", { name: "Dávka je uzavřená" })).toBeVisible()
  })
})
