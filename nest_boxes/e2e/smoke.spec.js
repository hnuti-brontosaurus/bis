import { expect, test } from "@playwright/test"

test("the landing page leads to the map and the form", async ({ page, isMobile }) => {
  await page.goto("/budky/")
  await expect(page.getByRole("heading", { level: 1 })).toContainText(
    "ptačích budek po celém Česku",
  )

  await page.getByRole("button", { name: "Otevřít mapu budek" }).click()
  await expect(page).toHaveURL(/\/budky\/mapa\/$/)
  await expect(page.getByTestId("map").locator("canvas")).toBeVisible()
  await expect(page.getByTestId("panel")).toBeVisible()

  if (isMobile) {
    await page.getByRole("button", { name: "Menu" }).click()
    await page
      .getByRole("dialog")
      .getByRole("link", { name: "Chci vyvěsit budky" })
      .click()
  } else {
    await page
      .getByRole("navigation")
      .getByRole("link", { name: "Chci vyvěsit budky" })
      .click()
  }
  await expect(
    page.getByRole("heading", { name: "Pověsíme budky spolu" }),
  ).toBeVisible()
})

test("the want to hang form asks for what it needs", async ({ page }) => {
  await page.goto("/budky/chci-vyvesit/")
  await page.getByRole("button", { name: "Odeslat" }).click()
  await expect(page.getByText("Bez e-mailu se ti neozveme.")).toBeVisible()
  await expect(page.getByText("Napiš aspoň obec.")).toBeVisible()
})

test("the theme toggle switches and remembers the theme", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" })
  await page.goto("/budky/")
  const background = () =>
    page.evaluate(() => getComputedStyle(document.body).backgroundColor)
  expect(await background()).toBe("rgb(240, 244, 241)")
  await page.getByRole("button", { name: "Přepnout světlý a tmavý režim" }).click()
  expect(await background()).toBe("rgb(16, 22, 19)")
  await page.reload()
  expect(await background()).toBe("rgb(16, 22, 19)")
})
