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
const demoScene = {
  mode: "fictional_demo",
  center: [11.2543435, 43.7672134],
  jobs: {
    type: "FeatureCollection",
    features: [
      ["signal-01", "AI 产品实习生", "Arno Research", 0.7, 11.2604, 43.7708],
      ["signal-02", "前端工程实习生", "Studio Nodo", 1.1, 11.2478, 43.7639],
      ["signal-03", "数据分析助理", "Campo Labs", 1.4, 11.2659, 43.7631],
      ["signal-04", "研究工程师", "Forma Systems", 1.8, 11.242, 43.7752],
    ].map(([id, title, company, distance_km, longitude, latitude]) => ({
      type: "Feature",
      id,
      geometry: { type: "Point", coordinates: [longitude, latitude] },
      properties: {
        id,
        title,
        company,
        distance_km,
        source: "fictional-demo",
        url: "",
      },
    })),
  },
  unresolved_count: 0,
  total_count: 4,
  map_name: "demo-firenze.pmtiles",
  map_available: true,
}

async function routeRadarScene(
  page: Page,
  scene: typeof demoScene = demoScene,
): Promise<void> {
  await page.route(`${apiOrigin}/api/v1/radar/scene`, async (route) => {
    await route.fulfill({
      json: scene,
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

test("renders a centered HOME and yellow local job signals at floating-window sizes", async ({
  page,
}) => {
  const outsideRequests: string[] = []
  page.on("request", (request) => {
    const url = new URL(request.url())
    if (!["http://127.0.0.1:4173", apiOrigin].includes(url.origin)) {
      outsideRequests.push(request.url())
    }
  })
  await routeRadarScene(page)
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

    const signalColor = await page
      .locator(".signal-index i")
      .evaluate((node) => getComputedStyle(node).backgroundColor)
    expect(signalColor).toBe("rgb(255, 225, 79)")

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
    demoScene.center as [number, number],
    14.3,
  )
  await page.mouse.click(
    stageBox!.x + stageBox!.width / 2 + signal.x,
    stageBox!.y + stageBox!.height / 2 + signal.y,
  )
  await expect(
    page.getByRole("heading", { name: "数据分析助理" }),
  ).toBeVisible()
  await expect(page.getByText("Campo Labs · fictional-demo")).toBeVisible()
  await expect(page.getByText("1.4 km")).toBeVisible()

  expect(outsideRequests).toEqual([])
})

test("keeps unresolved jobs out of the spatial layer and shows an empty state", async ({
  page,
}) => {
  await routeRadarScene(page, {
    ...demoScene,
    jobs: { type: "FeatureCollection", features: [] },
    unresolved_count: 3,
    total_count: 3,
  })
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
  await expect(page.getByRole("status")).toContainText("3 个岗位地点仍待解析")
  await expect(page.getByRole("button", { name: "返回岗位列表" })).toBeVisible()
  await expect(page.getByText("00 SIGNALS / 3 PENDING")).toBeVisible()
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
  await routeRadarScene(page)
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
  await routeRadarScene(page)
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
  await routeRadarScene(page)
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
