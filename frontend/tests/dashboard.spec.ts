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

test("shows unresolved distance reason and checkpoint retry", async ({
  page,
}) => {
  await page.unroute("http://127.0.0.1:8000/api/v1/**")
  await page.route("http://127.0.0.1:8000/api/v1/**", async (route) => {
    const path = new URL(route.request().url()).pathname.replace("/api/v1", "")
    if (path === "/jobs") {
      await route.fulfill({
        json: [
          {
            id: "job-1",
            source: "lever:example",
            external_id: "public-1",
            title: "AI Intern",
            company: "example",
            location_text: "Hong Kong",
            distance_km: null,
            distance_status: "location_unresolved",
            distance_reason:
              "公开职位来源未提供可验证坐标；职位已保留，未伪造距离",
            url: "https://jobs.lever.co/example/public-1",
            job_type: "Internship",
            summary: "Public fixture",
            published_at: null,
            observed_at: new Date().toISOString(),
          },
        ],
      })
      return
    }
    if (path === "/agent-runs") {
      await route.fulfill({
        json: [
          {
            id: "run-1",
            graph_name: "job_discovery",
            execution_mode: "demo",
            trigger: "manual",
            status: "failed",
            current_node: "stopped",
            message:
              "RuntimeError: 运行已安全停止；可修复原因后从 checkpoint 重试。",
            result_json: { error_type: "RuntimeError" },
            retry_count: 0,
            error_history: [],
            started_at: new Date().toISOString(),
            finished_at: new Date().toISOString(),
          },
        ],
      })
      return
    }
    if (path === "/agent-runs/run-1/retry") {
      await route.fulfill({
        json: {
          id: "run-1",
          graph_name: "job_discovery",
          execution_mode: "demo",
          trigger: "manual",
          status: "succeeded",
          current_node: "complete",
          message: "运行完成",
          result_json: { persisted: 3 },
          retry_count: 1,
          error_history: [],
          started_at: new Date().toISOString(),
          finished_at: new Date().toISOString(),
        },
      })
      return
    }
    if (path === "/overview") {
      await route.fulfill({
        json: {
          execution_mode: "demo",
          provider_mode: "demo",
          live_job_search_enabled: false,
          location_configured: true,
          landmark_count: 2,
          job_count: 1,
          fact_count: 0,
          resume_version: null,
          work_entry_count: 0,
          report_count: 0,
          pending_approvals: 0,
          recent_runs: [],
        },
      })
      return
    }
    await route.fulfill({ json: [] })
  })

  await page.goto("/")
  await page.getByRole("button", { name: /岗位信号/ }).click()
  await expect(page.getByText(/职位已保留，未伪造距离/)).toBeVisible()
  await page.getByRole("button", { name: /Agent 运行/ }).click()
  await expect(page.getByRole("button", { name: /从检查点重试/ })).toBeVisible()
})
