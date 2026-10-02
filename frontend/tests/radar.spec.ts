import { readFileSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import { expect, type Page, test } from "@playwright/test"

const apiOrigin = "http://127.0.0.1:8000"
const mapUrl = `${apiOrigin}/api/v1/radar/maps/demo-firenze.pmtiles`
const mapPath = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../runtime-data/maps/demo-firenze.pmtiles",
)
const captureDir = resolve(
  dirname(fileURLToPath(import.meta.url)),
  "../../output/playwright/radar-qa",
)

type SceneOverrides = {
  features?: unknown[][]
  unresolved?: Array<Record<string, unknown>>
  lastRun?: Record<string, unknown> | null
}

function buildScene({
  features,
  unresolved = [],
  lastRun = {
    finished_at: "2026-10-02T08:55:00Z",
    status: "succeeded",
    trigger: "scheduler",
    execution_mode: "demo",
    new_count: 2,
    updated_count: 1,
    failed_count: 0,
  },
}: SceneOverrides = {}) {
  const rows = features ?? [
    [
      "signal-01",
      "AI 产品实习生",
      "Arno Research",
      0.7,
      11.2604,
      43.7708,
      true,
    ],
    ["signal-02", "前端工程实习生", "Studio Nodo", 1.1, 11.2478, 43.7639, true],
    ["signal-03", "数据分析助理", "Campo Labs", 1.4, 11.2659, 43.7631, false],
    ["signal-04", "研究工程师", "Forma Systems", 1.8, 11.242, 43.7752, false],
  ]
  return {
    mode: "fictional_demo",
    center: [11.2543435, 43.7672134],
    jobs: {
      type: "FeatureCollection",
      features: rows.map(
        ([id, title, company, distance_km, longitude, latitude, is_new]) => ({
          type: "Feature",
          id,
          geometry: { type: "Point", coordinates: [longitude, latitude] },
          properties: {
            id,
            title,
            company,
            distance_km,
            source: "fictional-demo",
            url: "https://example.com/jobs/" + String(id),
            location_text: "Firenze Centro",
            salary_text: "EUR 1200–1600/月",
            job_type: "intern",
            summary: "公开岗位摘要",
            ai_summary: "AI 摘要：公开岗位要点",
            geocode_source: "gazetteer:firenze",
            interview_role_id: "frontend",
            interview_level: "intern",
            is_new: Boolean(is_new),
            published_at: "2026-10-02T08:00:00Z",
            observed_at: "2026-10-02T08:55:00Z",
          },
        }),
      ),
    },
    unresolved_count: unresolved.length,
    total_count: rows.length + unresolved.length,
    pending_jobs: unresolved,
    generated_at: "2026-10-02T09:00:00Z",
    last_run: lastRun,
    map_name: "demo-firenze.pmtiles",
    map_available: true,
  }
}

async function routeRadarScene(
  page: Page,
  scene: Record<string, unknown> | ((call: number) => Record<string, unknown>),
): Promise<void> {
  let calls = 0
  await page.route(`${apiOrigin}/api/v1/radar/scene`, async (route) => {
    calls += 1
    await route.fulfill({
      json: typeof scene === "function" ? scene(calls) : scene,
      headers: { "Cache-Control": "no-store" },
    })
  })
}

function projectToViewport(
  coordinates: [number, number],
  center: [number, number],
  zoom: number,
): { x: number; y: number } {
  const worldSize = 512 * 2 ** zoom
  const project = ([longitude, latitude]: [number, number]) => {
    const radians = (latitude * Math.PI) / 180
    return {
      x: ((longitude + 180) / 360) * worldSize,
      y:
        ((1 - Math.log(Math.tan(radians) + 1 / Math.cos(radians)) / Math.PI) /
          2) *
        worldSize,
    }
  }
  const point = project(coordinates)
  const origin = project(center)
  return { x: point.x - origin.x, y: point.y - origin.y }
}

async function routeLocalMap(page: Page, missing = false): Promise<void> {
  const mapBytes = missing ? null : readFileSync(mapPath)

  await page.route(`${mapUrl}*`, async (route) => {
    if (!mapBytes) {
      await route.fulfill({ status: 404, body: "Radar map not found" })
      return
    }

    const range = route.request().headers().range
    const match = range?.match(/^bytes=(\d+)-(\d+)?$/)
    const start = match ? Number(match[1]) : 0
    const requestedEnd = match?.[2] ? Number(match[2]) : mapBytes.length - 1
    const end = Math.min(requestedEnd, mapBytes.length - 1)
    const body = mapBytes.subarray(start, end + 1)

    await route.fulfill({
      status: range ? 206 : 200,
      body,
      headers: {
        "Accept-Ranges": "bytes",
        "Cache-Control": "private, max-age=86400",
        "Content-Length": String(body.length),
        "Content-Range": `bytes ${start}-${end}/${mapBytes.length}`,
        "Content-Type": "application/vnd.pmtiles",
      },
    })
  })
}

test("renders a centered HOME, new-job badges and opens the job drawer", async ({
  page,
}) => {
  const outsideRequests: string[] = []
  page.on("request", (request) => {
    const url = new URL(request.url())
    if (!["http://127.0.0.1:4173", apiOrigin].includes(url.origin)) {
      outsideRequests.push(request.url())
    }
  })
  await routeRadarScene(page, buildScene())
  await routeLocalMap(page)

  for (const viewport of [
    { width: 320, height: 320 },
    { width: 420, height: 420 },
    { width: 900, height: 700 },
  ]) {
    await page.setViewportSize(viewport)
    if (page.url() === "about:blank") await page.goto("/radar")

    const radar = page.locator(".radar-window")
    await expect(radar).toHaveAttribute("data-radar-status", "ready")
    await expect(radar).toHaveAttribute("data-signal-count", "4")
    await expect(page.getByTestId("radar-map").locator("canvas")).toBeVisible()
    await expect(page.getByText("04 SIGNALS")).toBeVisible()
    await expect(page.getByTestId("radar-new-tag")).toContainText("+2 NEW")
    await expect(page.getByTestId("radar-last-run")).toContainText("上次抓取")
    await expect(page.getByTestId("radar-update-time")).toContainText("更新")
    await expect(page.locator("body")).not.toContainText("11.2543435")
    await expect(page.locator("body")).not.toContainText("43.7672134")

    const home = page.getByRole("img", { name: "用户本地位置，地图中心" })
    const stage = page.locator(".radar-stage")
    const [homeBox, stageBox] = await Promise.all([
      home.boundingBox(),
      stage.boundingBox(),
    ])
    expect(homeBox).not.toBeNull()
    expect(stageBox).not.toBeNull()
    expect(homeBox!.x + homeBox!.width / 2).toBeCloseTo(
      stageBox!.x + stageBox!.width / 2,
      0,
    )
    expect(homeBox!.y + homeBox!.height / 2).toBeCloseTo(
      stageBox!.y + stageBox!.height / 2,
      0,
    )

    if (process.env.RADAR_CAPTURE === "1") {
      await page.screenshot({
        path: resolve(
          captureDir,
          `radar-${viewport.width}x${viewport.height}.png`,
        ),
      })
    }
  }

  const stageBox = await page.locator(".radar-stage").boundingBox()
  expect(stageBox).not.toBeNull()
  const signal = projectToViewport(
    [11.2659, 43.7631],
    [11.2543435, 43.7672134],
    14.3,
  )
  await page.mouse.click(
    stageBox!.x + stageBox!.width / 2 + signal.x,
    stageBox!.y + stageBox!.height / 2 + signal.y,
  )

  const drawer = page.locator(".ant-drawer-open .ant-drawer-content")
  await expect(drawer).toBeVisible()
  await expect(drawer).toContainText("数据分析助理")
  await expect(drawer).toContainText("Campo Labs")
  await expect(drawer).toContainText("1.4 km")
  await expect(drawer).toContainText("EUR 1200–1600/月")
  await expect(drawer).toContainText("fictional-demo")
  await expect(drawer.getByRole("button", { name: "去练面试" })).toBeVisible()
  if (process.env.RADAR_CAPTURE === "1") {
    await page.screenshot({
      path: resolve(captureDir, "radar-drawer.png"),
    })
  }
  await expect(page.locator("body")).not.toContainText("11.2543435")
  expect(outsideRequests).toEqual([])
})

test("refresh picks up scene changes from scheduled fetches", async ({
  page,
}) => {
  await routeRadarScene(page, buildScene())
  await routeLocalMap(page)
  await page.goto("/radar")

  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "ready",
  )
  await expect(page.getByTestId("radar-last-run")).toContainText("+2/改1/败0")

  await routeRadarScene(
    page,
    buildScene({
      features: [
        [
          "signal-01",
          "AI 产品实习生",
          "Arno Research",
          0.7,
          11.2604,
          43.7708,
          false,
        ],
        [
          "signal-02",
          "前端工程实习生",
          "Studio Nodo",
          1.1,
          11.2478,
          43.7639,
          false,
        ],
        [
          "signal-03",
          "数据分析助理",
          "Campo Labs",
          1.4,
          11.2659,
          43.7631,
          false,
        ],
        [
          "signal-04",
          "研究工程师",
          "Forma Systems",
          1.8,
          11.242,
          43.7752,
          false,
        ],
      ],
      lastRun: {
        finished_at: "2026-10-02T09:30:00Z",
        status: "succeeded",
        trigger: "scheduler",
        execution_mode: "demo",
        new_count: 0,
        updated_count: 4,
        failed_count: 0,
      },
    }),
  )
  await page.getByTestId("radar-refresh").click()
  await expect(page.getByTestId("radar-last-run")).toContainText("+0/改4/败0")
  await expect(page.getByTestId("radar-new-tag")).toHaveCount(0)
})

test("handoff pushes a job to the interview project pending queue", async ({
  page,
}) => {
  let pushedBody: Record<string, unknown> | null = null
  await page.route(
    `${apiOrigin}/api/v1/jobs/signal-01/interview-handoff`,
    async (route) => {
      pushedBody = route.request().postDataJSON()
      await route.fulfill({
        json: {
          job_id: "signal-01",
          role_id: "frontend",
          level: "intern",
          pushed: true,
          push_channel: "admin_api",
          file: "/tmp/handoff.json",
          document_external_id: "jd-lever-signal-01",
          detail: null,
          push_response: { imported: 1 },
        },
      })
    },
  )
  await routeRadarScene(page, buildScene())
  await routeLocalMap(page)
  await page.goto("/radar")

  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "ready",
  )
  await page.getByTestId("radar-jobs-button").click()
  const drawer = page.locator(".ant-drawer-open .ant-drawer-content")
  await expect(drawer).toBeVisible()
  await drawer.getByRole("list").getByText("AI 产品实习生").click()
  await drawer.getByRole("button", { name: "去练面试" }).click()
  await page.locator(".ant-popconfirm .ant-btn-primary").click()
  await expect(drawer).toContainText("已通过 admin_api 推送为 pending 语料")
  expect(pushedBody).toEqual({
    push: true,
    role_id: "frontend",
    level: "intern",
  })
})

test("keeps unresolved jobs out of the spatial layer and shows an empty state", async ({
  page,
}) => {
  await routeRadarScene(
    page,
    buildScene({
      features: [],
      unresolved: [
        {
          id: "pending-1",
          title: "远程算法实习",
          company: "Remote Co",
          location_text: "Remote",
          source: "lever:remote",
        },
      ],
    }),
  )
  await routeLocalMap(page)
  await page.goto("/radar")

  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "ready",
  )
  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-signal-count",
    "0",
  )
  await expect(page.getByRole("status")).toContainText("NO MAPPED SIGNALS")
  await expect(page.getByRole("status")).toContainText("1 个岗位地点仍待解析")
  await expect(page.getByRole("button", { name: "返回岗位列表" })).toBeVisible()
  await expect(page.getByText("00 SIGNALS")).toBeVisible()
  await page.getByTestId("radar-pending-button").click()
  const drawer = page.locator(".ant-drawer-open .ant-drawer-content")
  await expect(drawer).toContainText("远程算法实习")
  await expect(drawer).toContainText("不在地图上伪造坐标")
})

test("shows a local error instead of crashing when WebGL is unavailable", async ({
  page,
}) => {
  await page.addInitScript(() => {
    Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
      configurable: true,
      value: () => null,
    })
  })
  await routeRadarScene(page, buildScene())
  await routeLocalMap(page)
  await page.goto("/radar")

  await expect(page.getByRole("alert")).toContainText("WEBGL UNAVAILABLE")
  await expect(page.getByRole("alert")).toContainText(
    "当前设备无法创建 WebGL2 街道地图",
  )
  await expect(page.getByRole("alert").locator("code")).toHaveCount(0)
  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "error",
  )
})

test("shows local startup guidance when the scene API is unavailable", async ({
  page,
}) => {
  await page.route(`${apiOrigin}/api/v1/radar/scene`, async (route) => {
    await route.fulfill({ status: 503, body: "Local API unavailable" })
  })
  await page.goto("/radar")

  const alert = page.getByRole("alert")
  await expect(alert).toContainText("LOCAL API UNAVAILABLE")
  await expect(alert).toContainText(
    "本地 API 未连接。请先启动 FastAPI 或 Docker Compose",
  )
  await expect(alert).toContainText("docker-compose up -d")
  await expect(alert).not.toContainText("HTTP 503")
  await expect(alert.getByRole("button", { name: "重新连接" })).toBeVisible()
  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "error",
  )
})

test("native surface exposes only the approved floating-window controls", async ({
  page,
}) => {
  await page.addInitScript(() => {
    const calls: Array<{ cmd: string; args: unknown }> = []
    Object.assign(globalThis, {
      isTauri: true,
      __TAURI_CALLS__: calls,
      __TAURI_INTERNALS__: {
        metadata: { currentWindow: { label: "main" } },
        invoke: async (cmd: string, args: unknown) => {
          calls.push({ cmd, args })
          if (cmd === "plugin:window|is_always_on_top") return true
          return null
        },
      },
    })
  })
  await routeRadarScene(page, buildScene())
  await routeLocalMap(page)
  await page.goto("/?surface=radar")
  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "ready",
  )

  await page.getByRole("button", { name: "窗口居中" }).click()
  await page.getByRole("button", { name: "取消置顶" }).click()
  await page
    .getByRole("toolbar", { name: "岗位雷达窗口控制" })
    .dispatchEvent("mousedown", { button: 0 })
  await page.getByRole("button", { name: "返回主看板" }).click()

  const commands = await page.evaluate(() =>
    (
      globalThis as typeof globalThis & {
        __TAURI_CALLS__: Array<{ cmd: string }>
      }
    ).__TAURI_CALLS__.map((call) => call.cmd),
  )
  expect(commands).toContain("plugin:window|is_always_on_top")
  expect(commands).toContain("plugin:window|center")
  expect(commands).toContain("plugin:window|set_always_on_top")
  expect(commands).toContain("plugin:window|start_dragging")
  expect(commands).toContain("plugin:window|close")
})

test("shows an actionable local-only state when the map package is missing", async ({
  page,
}) => {
  await routeRadarScene(page, buildScene())
  await routeLocalMap(page, true)
  await page.goto("/radar")

  await expect(page.getByRole("alert")).toContainText("LOCAL MAP UNAVAILABLE")
  await expect(page.getByRole("alert")).toContainText(
    "./scripts/fetch-radar-demo-map.sh",
  )
  await expect(page.locator(".radar-window")).toHaveAttribute(
    "data-radar-status",
    "error",
  )
})
