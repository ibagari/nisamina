import { test, expect } from "@playwright/test";

/** D-070 Playwright e2e smoke for D-069 UI surface. */

test.describe("onboarding wizard", () => {
  test("renders title + step 1", async ({ page }) => {
    await page.goto("/onboarding");
    await expect(page.getByRole("heading", { name: /Welcome.*let.*find where you are/i })).toBeVisible();
    await expect(page.getByText(/Who in your life speaks Garifuna/i)).toBeVisible();
  });

  test("step 1 next disabled until answer", async ({ page }) => {
    await page.goto("/onboarding");
    const next = page.getByRole("button", { name: "Next" });
    await expect(next).toBeDisabled();
    await page.getByLabel(/A family member speaks it fluently/i).check();
    await expect(next).toBeEnabled();
  });

  test("4-step navigation works", async ({ page }) => {
    await page.goto("/onboarding");
    await page.getByLabel(/A family member speaks it fluently/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/I speak Garifuna comfortably/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/^Belize$/).check();
    await page.getByRole("button", { name: "Next" }).click();
    await expect(page.getByText(/Your path/i)).toBeVisible();
    await expect(page.getByRole("button", { name: "Begin learning" })).toBeVisible();
  });

  test("resolves l1_maintainer for fluent + family", async ({ page }) => {
    await page.goto("/onboarding");
    await page.getByLabel(/A family member speaks it fluently/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/I speak Garifuna comfortably/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/^Belize$/).check();
    await page.getByRole("button", { name: "Next" }).click();
    await expect(page.getByText(/L1-maintainer path/i)).toBeVisible();
  });

  test("resolves heritage for family + low proficiency", async ({ page }) => {
    await page.goto("/onboarding");
    await page.getByLabel(/A family member speaks some/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/I understand some when others speak/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/^Belize$/).check();
    await page.getByRole("button", { name: "Next" }).click();
    await expect(page.getByText(/Heritage path/i)).toBeVisible();
  });

  test("resolves novice for no family + no proficiency", async ({ page }) => {
    await page.goto("/onboarding");
    await page.getByLabel(/I'm learning fresh/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/I don't know any Garifuna yet/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await page.getByLabel(/I'm in the diaspora/i).check();
    await page.getByRole("button", { name: "Next" }).click();
    await expect(page.getByText(/Novice path/i)).toBeVisible();
  });
});

test.describe("a11y panel", () => {
  test("renders + saves prefs", async ({ page }) => {
    await page.goto("/a11y");
    await expect(page.getByRole("heading", { name: "Accessibility preferences" })).toBeVisible();
    await page.getByLabel("Reduce motion").check();
    await page.getByRole("button", { name: "Save preferences" }).click();
    await expect(page.getByText("✓ Saved")).toBeVisible({ timeout: 3000 });
  });

  test("bandwidth mode + text spacing", async ({ page }) => {
    await page.goto("/a11y");
    await page.getByRole("button", { name: /Audio \+ text only/i }).click();
    await page.getByRole("button", { name: "Loose (1.5×)" }).click();
    await page.getByRole("button", { name: "Save preferences" }).click();
    await expect(page.getByText("✓ Saved")).toBeVisible({ timeout: 3000 });
  });
});

test.describe("lexicon", () => {
  test("displays catalog summary", async ({ page }) => {
    await page.goto("/lexicon");
    await expect(page.getByRole("heading", { name: /Lexicon \+ Learning Charts/i })).toBeVisible();
    await expect(page.getByText(/40 charts/i)).toBeVisible();
    await expect(page.getByText(/29 \/ 29 subjects/i)).toBeVisible();
  });

  test("elder-gated note visible", async ({ page }) => {
    await page.goto("/lexicon");
    await expect(page.getByText(/Elder-gated content/i)).toBeVisible();
    await expect(page.getByText(/Labayayahoun Ibagari/)).toBeVisible();
  });
});

test.describe("badges", () => {
  test("renders heading + sample assertion", async ({ page }) => {
    await page.goto("/badges");
    await expect(page.getByRole("heading", { name: "My Badges" })).toBeVisible();
    await expect(page.getByText(/Verifiable digital credentials/i)).toBeVisible();
    await expect(page.getByText(/Day 1 — Greetings/i)).toBeVisible();
  });
});

test.describe("tutor", () => {
  test("renders initial turn", async ({ page }) => {
    await page.goto("/tutor");
    await expect(page.getByRole("heading", { name: "Socratic Tutor" })).toBeVisible();
    await expect(page.getByText(/Think about your family or community/i)).toBeVisible();
  });

  test("submit shows learner message", async ({ page }) => {
    await page.goto("/tutor");
    await page.getByPlaceholder("Type your response...").fill("thank you");
    await page.getByRole("button", { name: "Submit" }).click();
    await expect(page.locator("text=LEARNER").first()).toBeVisible({ timeout: 3000 });
  });
});

test.describe("home", () => {
  test("renders platform + cultural protocol", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByText(/Buguya nuani/)).toBeVisible();
    await expect(page.getByText(/Labayayahoun Ibagari/)).toBeVisible();
  });
});
