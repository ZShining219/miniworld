import { expect, test } from "@playwright/test"

const emptyLists = [
  "/jobs",
  "/imports",
  "/profile-facts",
  "/resume-drafts",
  "/work-entries",
  "/reports",
  "/agent-runs",
  "/landmarks",
]

test.beforeEach(async ({ page }) => {
  await page.route("http://127.0.0.1:8000/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname.replace("/api/v1", "")
    if (path === "/overview") {
      await route.fulfill({
        json: {
          execution_mode: "demo",
          provider_mode: "demo",
          live_job_search_enabled: false,
          location_configured: true,
          landmark_count: 2,
          job_count: 3,
          fact_count: 4,
          resume_version: 1,
          work_entry_count: 2,
          report_count: 1,
          pending_approvals: 0,
          recent_runs: [],
        },
      })
      return
    }
    if (path === "/location") {
      await route.fulfill({
        json: {
          configured: true,
          masked_address: "••••••（仅保存在本机）",
          is_demo: true,
          updated_at: null,
        },
      })
      return
    }
    if (path === "/schedule") {
      await route.fulfill({
        json: {
          job_discovery_enabled: true,
          interval_minutes: 720,
          last_triggered_at: null,
        },
      })
      return
    }
    if (emptyLists.includes(path)) {
      await route.fulfill({ json: [] })
      return
    }
    await route.fulfill({ status: 404, json: { detail: "mock not found" } })
  })
})

test("shows the three independent product modules", async ({ page }) => {
  await page.goto("/")
  await expect(page.getByText("个人机会雷达")).toBeVisible()
  await expect(page.getByRole("button", { name: /岗位信号/ })).toBeVisible()
  await expect(page.getByRole("button", { name: /个人档案/ })).toBeVisible()
  await expect(page.getByRole("button", { name: /工作沉淀/ })).toBeVisible()
  await expect(page.getByText("精确地址不离开本机")).toBeVisible()
})

test("navigates to settings without displaying exact coordinates", async ({
  page,
}) => {
  await page.goto("/")
  await page.getByRole("button", { name: /本地设置/ }).click()
  await expect(page.getByText("精确住址与坐标")).toBeVisible()
  await expect(page.getByText("••••••（仅保存在本机）")).toBeVisible()
  await expect(page.getByLabel("纬度")).toHaveValue("")
  await expect(page.getByLabel("经度")).toHaveValue("")
})
