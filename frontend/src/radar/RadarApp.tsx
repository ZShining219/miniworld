import { isTauri } from "@tauri-apps/api/core"
import { getCurrentWindow } from "@tauri-apps/api/window"
import {
  Badge,
  Button,
  Descriptions,
  Drawer,
  Empty,
  List,
  Space,
  Tabs,
  Tag,
  Tooltip,
  Typography,
} from "antd"
import {
  ArrowLeft,
  BriefcaseBusiness,
  Crosshair,
  ListTodo,
  LocateFixed,
  LockKeyhole,
  Minus,
  Move,
  Pin,
  PinOff,
  Plus,
  RefreshCw,
  RotateCcw,
  X,
} from "lucide-react"
import * as maplibregl from "maplibre-gl"
import { Protocol } from "pmtiles"
import {
  type MouseEvent as ReactMouseEvent,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"
import { API_ROOT, api } from "../api"
import { InterviewHandoffActions } from "../components/InterviewHandoff"
import type { RadarJobProperties, RadarScene } from "../types"
import { createRadarStyle } from "./radar-style"
import "maplibre-gl/dist/maplibre-gl.css"
import "./radar.css"

let pmtilesProtocolInstalled = false

const SCENE_POLL_MS = 20_000

type RadarErrorKind = "api" | "map" | "webgl"

function installPmtilesProtocol(): void {
  if (pmtilesProtocolInstalled) return
  const protocol = new Protocol()
  maplibregl.addProtocol("pmtiles", protocol.tile)
  pmtilesProtocolInstalled = true
}

function formatClock(value: string | null | undefined): string {
  if (!value) return "—"
  return new Intl.DateTimeFormat("zh-CN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value))
}

function runStatusColor(status: string | undefined): string {
  if (status === "succeeded") return "success"
  if (status === "failed" || status === "blocked_by_policy") return "error"
  return "warning"
}

function RadarApp() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const mapReadyRef = useRef(false)
  const sceneRef = useRef<RadarScene | null>(null)
  const [scene, setScene] = useState<RadarScene | null>(null)
  const [mapAvailability, setMapAvailability] = useState<
    "checking" | "available" | "missing"
  >("checking")
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading")
  const [error, setError] = useState("")
  const [errorKind, setErrorKind] = useState<RadarErrorKind | null>(null)
  const [syncError, setSyncError] = useState<string | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)
  const [drawerTab, setDrawerTab] = useState<"jobs" | "pending">("jobs")
  const [retryToken, setRetryToken] = useState(0)
  const nativeWindow = useMemo(
    () => (isTauri() ? getCurrentWindow() : null),
    [],
  )
  const [pinned, setPinned] = useState(true)
  const selectedJob = useMemo<RadarJobProperties | null>(
    () =>
      scene?.jobs.features.find((job) => job.id === selectedId)?.properties ??
      null,
    [scene, selectedId],
  )
  const pendingJobs = scene?.pending_jobs ?? []
  const lastRun = scene?.last_run ?? null
  const newCount = useMemo(
    () =>
      scene?.jobs.features.filter((feature) => feature.properties.is_new)
        .length ?? 0,
    [scene],
  )
  const signalCount = scene?.jobs.features.length ?? 0

  const fetchScene = useCallback(async (silent: boolean) => {
    try {
      const nextScene = await api.radarScene()
      if (!nextScene.center) {
        throw new Error("请先在本地设置用户位置，再打开岗位雷达。")
      }
      sceneRef.current = nextScene
      setScene(nextScene)
      setSyncError(null)
      setSelectedId((current) =>
        current &&
        nextScene.jobs.features.some((feature) => feature.id === current)
          ? current
          : (nextScene.jobs.features[0]?.id ?? null),
      )
      return true
    } catch (reason: unknown) {
      if (silent && sceneRef.current) {
        setSyncError(reason instanceof Error ? reason.message : "同步失败")
        return false
      }
      const message = reason instanceof Error ? reason.message : ""
      setError(
        message.startsWith("请先在本地设置")
          ? message
          : "本地 API 未连接。请先启动 FastAPI 或 Docker Compose，再重新打开岗位雷达。",
      )
      setErrorKind("api")
      setStatus("error")
      return false
    }
  }, [])

  useEffect(() => {
    if (!nativeWindow) return
    void nativeWindow
      .isAlwaysOnTop()
      .then(setPinned)
      .catch(() => undefined)
  }, [nativeWindow])

  const retry = useCallback(() => {
    setError("")
    setErrorKind(null)
    setStatus("loading")
    setMapAvailability("checking")
    setRetryToken((value) => value + 1)
    void fetchScene(false)
  }, [fetchScene])

  useEffect(() => {
    let active = true
    void fetchScene(false)
    const timer = window.setInterval(() => {
      if (!active) return
      void fetchScene(true)
    }, SCENE_POLL_MS)
    return () => {
      active = false
      window.clearInterval(timer)
    }
  }, [fetchScene])

  const mapName = scene?.map_name ?? null
  const mapAvailableFlag = scene?.map_available ?? null
  useEffect(() => {
    void retryToken
    if (!mapName || mapAvailableFlag === null) return
    if (!mapAvailableFlag) {
      setMapAvailability("missing")
      setError("本地街道地图包不存在或无法读取，请先运行资源准备脚本。")
      setErrorKind("map")
      setStatus("error")
      return
    }
    const controller = new AbortController()
    const mapUrl = `${API_ROOT}/radar/maps/${encodeURIComponent(mapName)}`

    void fetch(mapUrl, {
      cache: "no-store",
      headers: { Range: "bytes=0-0" },
      signal: controller.signal,
    })
      .then((response) => {
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        setMapAvailability("available")
      })
      .catch((reason: unknown) => {
        if (reason instanceof DOMException && reason.name === "AbortError")
          return
        setMapAvailability("missing")
        setError("本地街道地图包不存在或无法读取，请先运行资源准备脚本。")
        setErrorKind("map")
        setStatus("error")
      })

    return () => controller.abort()
  }, [mapName, mapAvailableFlag, retryToken])

  useEffect(() => {
    if (mapAvailability !== "available") return
    const container = mapContainer.current
    const currentScene = sceneRef.current
    const center = currentScene?.center
    if (!container || !center) return

    let animationFrame = 0
    let disposed = false
    mapReadyRef.current = false
    const mapUrl = `${API_ROOT}/radar/maps/${encodeURIComponent(currentScene.map_name)}`
    const webglProbe = document.createElement("canvas").getContext("webgl2")
    if (!webglProbe) {
      setError("当前设备无法创建 WebGL2 街道地图，请检查图形加速设置。")
      setErrorKind("webgl")
      setStatus("error")
      return
    }
    let map: maplibregl.Map
    try {
      installPmtilesProtocol()
      map = new maplibregl.Map({
        container,
        style: createRadarStyle(mapUrl),
        center,
        zoom: 14.3,
        minZoom: 12.5,
        maxZoom: 17,
        attributionControl: false,
        dragPan: false,
        dragRotate: false,
        scrollZoom: false,
        boxZoom: false,
        doubleClickZoom: false,
        keyboard: false,
        touchZoomRotate: false,
        pitchWithRotate: false,
      })
    } catch (reason) {
      setError(
        reason instanceof Error
          ? reason.message
          : "当前设备无法创建 WebGL 街道地图。",
      )
      setErrorKind("webgl")
      setStatus("error")
      return
    }
    mapRef.current = map

    map.on("load", () => {
      if (disposed) return
      mapReadyRef.current = true
      map.addSource("radar-jobs", {
        type: "geojson",
        data: sceneRef.current?.jobs ?? {
          type: "FeatureCollection",
          features: [],
        },
      })
      map.addLayer({
        id: "radar-job-glow",
        type: "circle",
        source: "radar-jobs",
        paint: {
          "circle-color": "#ffd84d",
          "circle-radius": 17,
          "circle-opacity": 0.2,
          "circle-blur": 0.7,
        },
      })
      map.addLayer({
        id: "radar-job-points",
        type: "circle",
        source: "radar-jobs",
        paint: {
          "circle-color": "#ffe25c",
          "circle-radius": 4.5,
          "circle-stroke-color": "#fff7a6",
          "circle-stroke-width": 1.5,
          "circle-opacity": 1,
        },
      })
      map.addLayer({
        id: "radar-job-new",
        type: "circle",
        source: "radar-jobs",
        filter: ["==", ["get", "is_new"], true],
        paint: {
          "circle-color": "rgba(0,0,0,0)",
          "circle-radius": 12,
          "circle-stroke-color": "#d5ff4f",
          "circle-stroke-width": 2,
          "circle-opacity": 0.9,
        },
      })

      map.on("click", "radar-job-points", (event) => {
        const feature = event.features?.[0]
        const id = feature?.properties?.id
        if (typeof id === "string") {
          setSelectedId(id)
          setDrawerTab("jobs")
          setDrawerOpen(true)
        }
      })
      map.on("mouseenter", "radar-job-points", () => {
        map.getCanvas().style.cursor = "pointer"
      })
      map.on("mouseleave", "radar-job-points", () => {
        map.getCanvas().style.cursor = "default"
      })

      const reducedMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)",
      ).matches
      const animate = (time: number) => {
        if (disposed) return
        const phase = reducedMotion ? 0.35 : (Math.sin(time / 430) + 1) / 2
        map.setPaintProperty("radar-job-glow", "circle-radius", 12 + phase * 13)
        map.setPaintProperty(
          "radar-job-glow",
          "circle-opacity",
          0.08 + (1 - phase) * 0.24,
        )
        map.setPaintProperty("radar-job-new", "circle-radius", 9 + phase * 10)
        map.setPaintProperty(
          "radar-job-new",
          "circle-opacity",
          0.25 + phase * 0.65,
        )
        animationFrame = window.requestAnimationFrame(animate)
      }
      animationFrame = window.requestAnimationFrame(animate)
      setStatus("ready")
    })

    map.on("error", (event) => {
      if (disposed || mapReadyRef.current) return
      setError(
        event.error?.message ??
          "本地街道地图未载入。请先运行地图资源准备脚本。",
      )
      setErrorKind("map")
      setStatus("error")
    })

    const resizeObserver = new ResizeObserver(() => map.resize())
    resizeObserver.observe(container)

    return () => {
      disposed = true
      resizeObserver.disconnect()
      window.cancelAnimationFrame(animationFrame)
      mapReadyRef.current = false
      mapRef.current = null
      map.remove()
    }
  }, [mapAvailability])

  useEffect(() => {
    const map = mapRef.current
    if (!map || !mapReadyRef.current || !scene) return
    const source = map.getSource("radar-jobs") as
      | maplibregl.GeoJSONSource
      | undefined
    source?.setData(scene.jobs)
  }, [scene])

  const adjustZoom = (amount: number) => {
    const map = mapRef.current
    if (!map) return
    map.easeTo({
      center: scene?.center ?? undefined,
      zoom: Math.min(17, Math.max(12.5, map.getZoom() + amount)),
      duration: 320,
    })
  }

  const recenter = () => {
    const center = scene?.center
    if (!center) return
    mapRef.current?.easeTo({ center, zoom: 14.3, duration: 420 })
  }

  const centerNativeWindow = () => {
    if (!nativeWindow) return
    void nativeWindow.center()
  }

  const togglePinned = () => {
    if (!nativeWindow) return
    const nextPinned = !pinned
    void nativeWindow
      .setAlwaysOnTop(nextPinned)
      .then(() => setPinned(nextPinned))
  }

  const beginWindowDrag = (event: ReactMouseEvent<HTMLElement>) => {
    if (
      !nativeWindow ||
      event.button !== 0 ||
      (event.target as HTMLElement).closest("button, a, .ant-drawer")
    ) {
      return
    }
    void nativeWindow.startDragging()
  }

  const leaveRadar = () => {
    if (nativeWindow) {
      void nativeWindow.close()
      return
    }
    window.close()
    window.setTimeout(() => {
      if (!window.closed) window.location.assign("/")
    }, 80)
  }

  const openJobsDrawer = (tab: "jobs" | "pending") => {
    setDrawerTab(tab)
    setDrawerOpen(true)
  }

  return (
    <div
      className="radar-window"
      data-radar-status={status}
      data-signal-count={status === "ready" ? signalCount : 0}
    >
      <header
        className="radar-toolbar"
        data-tauri-drag-region
        role="toolbar"
        aria-label="岗位雷达窗口控制"
        onMouseDown={beginWindowDrag}
      >
        <button
          className="radar-brand"
          type="button"
          onClick={recenter}
          aria-label="重新居中"
        >
          <span className="radar-brand-mark">
            <Crosshair size={15} />
          </span>
          <span>
            <b>JOB RADAR</b>
            <small>LOCAL FIELD / 01</small>
          </span>
        </button>
        <div className={`radar-runtime ${status}`}>
          <i />
          {status !== "error"
            ? syncError
              ? "SYNC STALE"
              : "OFFLINE"
            : errorKind === "api"
              ? "API OFFLINE"
              : errorKind === "map"
                ? "MAP MISSING"
                : "WEBGL DOWN"}
        </div>
        <button
          className={`radar-tool-button radar-native-control ${nativeWindow ? "active" : ""}`}
          type="button"
          aria-label="窗口居中"
          title="窗口居中"
          onClick={centerNativeWindow}
          disabled={!nativeWindow}
        >
          <Move size={14} />
        </button>
        <button
          className={`radar-tool-button radar-native-control ${nativeWindow ? "active" : ""} ${pinned ? "pinned" : ""}`}
          type="button"
          aria-label={pinned ? "取消置顶" : "窗口置顶"}
          title={pinned ? "取消置顶" : "窗口置顶"}
          onClick={togglePinned}
          disabled={!nativeWindow}
        >
          {pinned ? <Pin size={14} /> : <PinOff size={14} />}
        </button>
        <button
          className="radar-tool-button"
          type="button"
          aria-label="返回主看板"
          onClick={leaveRadar}
        >
          <X size={15} />
        </button>
      </header>

      <main className="radar-stage">
        <div
          className="radar-map"
          ref={mapContainer}
          data-testid="radar-map"
          aria-hidden="true"
        />
        <div className="radar-map-vignette" />
        <div className="radar-coordinate-grid" />
        <div className="radar-sweep" />
        <div className="radar-crosshair horizontal" />
        <div className="radar-crosshair vertical" />
        <div className="radar-range range-near" />
        <div className="radar-range range-far" />

        {scene?.center && (
          <div
            className="radar-home"
            role="img"
            aria-label="用户本地位置，地图中心"
          >
            <span>
              <LocateFixed size={16} />
            </span>
            <b>HOME</b>
          </div>
        )}

        <div className="radar-map-meta top-left">
          <LockKeyhole size={11} />
          <span>中心坐标仅在本机内存</span>
        </div>
        <div className="radar-map-meta top-right">
          <Badge count={newCount} size="small" offset={[-2, 2]}>
            <Button
              size="small"
              icon={<BriefcaseBusiness size={12} />}
              onClick={() => openJobsDrawer("jobs")}
              data-testid="radar-jobs-button"
            >
              {String(signalCount).padStart(2, "0")} SIGNALS
            </Button>
          </Badge>
          {newCount > 0 && (
            <Tag color="lime" data-testid="radar-new-tag">
              +{newCount} NEW
            </Tag>
          )}
          {pendingJobs.length > 0 && (
            <Tooltip title="部分岗位地点尚未解析，不会伪造坐标">
              <Button
                size="small"
                icon={<ListTodo size={12} />}
                onClick={() => openJobsDrawer("pending")}
                data-testid="radar-pending-button"
              >
                {pendingJobs.length} PENDING
              </Button>
            </Tooltip>
          )}
        </div>

        <div className="radar-zoom-controls">
          <button
            type="button"
            onClick={() => adjustZoom(0.7)}
            aria-label="放大"
          >
            <Plus size={14} />
          </button>
          <button
            type="button"
            onClick={() => adjustZoom(-0.7)}
            aria-label="缩小"
          >
            <Minus size={14} />
          </button>
          <button type="button" onClick={recenter} aria-label="重新居中">
            <RotateCcw size={13} />
          </button>
          <button
            type="button"
            onClick={() => void fetchScene(true)}
            aria-label="立即同步岗位数据"
            data-testid="radar-refresh"
          >
            <RefreshCw size={13} />
          </button>
        </div>

        {status === "loading" && (
          <div className="radar-state-card">
            <i />
            <b>LOADING LOCAL FIELD</b>
            <span>正在读取本机街道瓦片</span>
          </div>
        )}
        {status === "error" && (
          <div className="radar-state-card error" role="alert">
            <b>
              {errorKind === "api"
                ? "LOCAL API UNAVAILABLE"
                : errorKind === "map"
                  ? "LOCAL MAP UNAVAILABLE"
                  : "WEBGL UNAVAILABLE"}
            </b>
            <span>{error}</span>
            {errorKind === "api" && <code>docker-compose up -d</code>}
            {errorKind === "map" && (
              <code>./scripts/fetch-radar-demo-map.sh</code>
            )}
            <Button size="small" onClick={retry}>
              重新连接
            </Button>
          </div>
        )}

        {status === "ready" && !selectedJob && (
          <div className="radar-state-card empty" role="status">
            <b>NO MAPPED SIGNALS</b>
            <span>
              {scene?.unresolved_count
                ? `${scene.unresolved_count} 个岗位地点仍待解析，未伪造地图位置。`
                : "当前没有可显示的岗位坐标。"}
            </span>
            <Button
              size="small"
              icon={<ArrowLeft size={11} />}
              onClick={leaveRadar}
            >
              返回岗位列表
            </Button>
          </div>
        )}

        <footer className="radar-map-footer">
          <span>
            {scene?.mode === "fictional_demo"
              ? "FICTIONAL DEMO DATA"
              : "LOCAL PRIVATE SCENE"}
          </span>
          <Space size={8} className="radar-run-meta">
            {lastRun && (
              <Tag
                color={runStatusColor(lastRun.status)}
                data-testid="radar-last-run"
              >
                {`上次抓取 ${formatClock(lastRun.finished_at)} · +${lastRun.new_count}/改${lastRun.updated_count}/败${lastRun.failed_count}`}
              </Tag>
            )}
            {scene?.generated_at && (
              <Tooltip title={`数据生成于 ${scene.generated_at}`}>
                <span data-testid="radar-update-time">
                  更新 {formatClock(scene.generated_at)}
                </span>
              </Tooltip>
            )}
          </Space>
          <a
            href="https://www.openstreetmap.org/copyright"
            target="_blank"
            rel="noreferrer"
          >
            © OpenStreetMap contributors
          </a>
        </footer>
      </main>

      <Button
        className="radar-back-link"
        type="text"
        icon={<ArrowLeft size={13} />}
        onClick={leaveRadar}
      >
        返回主看板
      </Button>

      <Drawer
        title={
          <Space size={8}>
            <BriefcaseBusiness size={15} />
            岗位信号
            {newCount > 0 && <Badge count={newCount} size="small" />}
          </Space>
        }
        placement="right"
        width={360}
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        mask={false}
        rootClassName="radar-jobs-drawer"
      >
        <Tabs
          activeKey={drawerTab}
          onChange={(key) => setDrawerTab(key as "jobs" | "pending")}
          items={[
            {
              key: "jobs",
              label: `已定位 ${signalCount}`,
              children: (
                <>
                  {scene?.jobs.features.length ? (
                    <List
                      size="small"
                      dataSource={scene.jobs.features}
                      renderItem={(feature) => {
                        const job = feature.properties
                        const active = job.id === selectedId
                        return (
                          <List.Item
                            onClick={() => setSelectedId(job.id)}
                            style={{
                              cursor: "pointer",
                              background: active
                                ? "rgba(213,255,79,0.08)"
                                : undefined,
                              borderRadius: 8,
                              paddingInline: 8,
                            }}
                          >
                            <List.Item.Meta
                              title={
                                <Space size={6}>
                                  <span>{job.title}</span>
                                  {job.is_new && (
                                    <Tag color="lime" data-testid="job-new-tag">
                                      NEW
                                    </Tag>
                                  )}
                                </Space>
                              }
                              description={
                                <Space size={4} wrap>
                                  <Typography.Text type="secondary">
                                    {job.company} · {job.location_text || "—"}
                                  </Typography.Text>
                                  {job.salary_text && (
                                    <Tag>{job.salary_text}</Tag>
                                  )}
                                </Space>
                              }
                            />
                            <Typography.Text type="secondary">
                              {job.distance_km === null
                                ? "—"
                                : `${job.distance_km.toFixed(1)}km`}
                            </Typography.Text>
                          </List.Item>
                        )
                      }}
                    />
                  ) : (
                    <Empty description="暂无可定位岗位" />
                  )}
                  {selectedJob && (
                    <>
                      <Descriptions
                        column={1}
                        size="small"
                        bordered
                        style={{ marginTop: 16 }}
                        items={[
                          {
                            key: "title",
                            label: "职位",
                            children: selectedJob.title,
                          },
                          {
                            key: "company",
                            label: "公司",
                            children: selectedJob.company,
                          },
                          {
                            key: "location",
                            label: "地点",
                            children: selectedJob.location_text || "—",
                          },
                          {
                            key: "salary",
                            label: "薪资",
                            children: selectedJob.salary_text ?? "未标注",
                          },
                          {
                            key: "distance",
                            label: "直线距离",
                            children:
                              selectedJob.distance_km === null
                                ? "—"
                                : `${selectedJob.distance_km.toFixed(1)} km`,
                          },
                          {
                            key: "source",
                            label: "来源",
                            children: selectedJob.source,
                          },
                          {
                            key: "geocode",
                            label: "定位方式",
                            children: selectedJob.geocode_source ?? "来源自带",
                          },
                          {
                            key: "interview",
                            label: "面试画像",
                            children:
                              selectedJob.interview_role_id ||
                              selectedJob.interview_level
                                ? `${selectedJob.interview_role_id ?? "?"} · ${selectedJob.interview_level ?? "?"}`
                                : "未判定",
                          },
                          {
                            key: "observed",
                            label: "最近抓取",
                            children: formatClock(
                              selectedJob.observed_at ??
                                scene?.generated_at ??
                                null,
                            ),
                          },
                        ]}
                      />
                      {selectedJob.ai_summary && (
                        <Typography.Paragraph
                          type="secondary"
                          style={{ fontSize: 12, marginTop: 12 }}
                        >
                          {selectedJob.ai_summary}
                        </Typography.Paragraph>
                      )}
                      <Space style={{ marginTop: 12 }} wrap>
                        {selectedJob.url ? (
                          <Button
                            size="small"
                            href={selectedJob.url}
                            target="_blank"
                            rel="noreferrer"
                          >
                            查看原始 JD
                          </Button>
                        ) : null}
                      </Space>
                      <InterviewHandoffActions
                        jobId={selectedJob.id}
                        roleId={selectedJob.interview_role_id}
                        level={selectedJob.interview_level}
                      />
                    </>
                  )}
                </>
              ),
            },
            {
              key: "pending",
              label: `待解析 ${pendingJobs.length}`,
              children: pendingJobs.length ? (
                <>
                  <Typography.Paragraph
                    type="secondary"
                    style={{ fontSize: 12 }}
                  >
                    这些岗位缺少可定位的公开地点信息，只计入待解析，不在地图上伪造坐标。
                  </Typography.Paragraph>
                  <List
                    size="small"
                    dataSource={pendingJobs}
                    renderItem={(job) => (
                      <List.Item>
                        <List.Item.Meta
                          title={job.title}
                          description={`${job.company} · ${job.location_text || "未知地点"} · ${job.source}`}
                        />
                      </List.Item>
                    )}
                  />
                </>
              ) : (
                <Empty description="没有待解析岗位" />
              ),
            },
          ]}
        />
      </Drawer>
    </div>
  )
}

export default RadarApp
