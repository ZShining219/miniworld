import { isTauri } from "@tauri-apps/api/core"
import { getCurrentWindow } from "@tauri-apps/api/window"
import {
  ArrowLeft,
  BriefcaseBusiness,
  Crosshair,
  LocateFixed,
  LockKeyhole,
  Minus,
  Move,
  Pin,
  PinOff,
  Plus,
  RotateCcw,
  X,
} from "lucide-react"
import * as maplibregl from "maplibre-gl"
import { Protocol } from "pmtiles"
import {
  type MouseEvent as ReactMouseEvent,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"
import { API_ROOT, api } from "../api"
import type { RadarScene } from "../types"
import { createRadarStyle } from "./radar-style"
import "maplibre-gl/dist/maplibre-gl.css"
import "./radar.css"

let pmtilesProtocolInstalled = false

type RadarErrorKind = "api" | "map" | "webgl"

function installPmtilesProtocol(): void {
  if (pmtilesProtocolInstalled) return
  const protocol = new Protocol()
  maplibregl.addProtocol("pmtiles", protocol.tile)
  pmtilesProtocolInstalled = true
}

function RadarApp() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<maplibregl.Map | null>(null)
  const [scene, setScene] = useState<RadarScene | null>(null)
  const [mapAvailability, setMapAvailability] = useState<
    "checking" | "available" | "missing"
  >("checking")
  const [status, setStatus] = useState<"loading" | "ready" | "error">("loading")
  const [error, setError] = useState("")
  const [errorKind, setErrorKind] = useState<RadarErrorKind | null>(null)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const nativeWindow = useMemo(
    () => (isTauri() ? getCurrentWindow() : null),
    [],
  )
  const [pinned, setPinned] = useState(true)
  const selectedJob = useMemo(
    () =>
      scene?.jobs.features.find((job) => job.id === selectedId)?.properties ??
      scene?.jobs.features[0]?.properties ??
      null,
    [scene, selectedId],
  )
  const center = scene?.center ?? null
  const signalCount = scene?.jobs.features.length ?? 0

  useEffect(() => {
    if (!nativeWindow) return
    void nativeWindow
      .isAlwaysOnTop()
      .then(setPinned)
      .catch(() => undefined)
  }, [nativeWindow])

  useEffect(() => {
    let active = true

    void api
      .radarScene()
      .then((nextScene) => {
        if (!active) return
        if (!nextScene.center) {
          throw new Error("请先在本地设置用户位置，再打开岗位雷达。")
        }
        setScene(nextScene)
        setSelectedId(nextScene.jobs.features[0]?.id ?? null)
      })
      .catch((reason: unknown) => {
        if (!active) return
        const message = reason instanceof Error ? reason.message : ""
        setError(
          message.startsWith("请先在本地设置")
            ? message
            : "本地 API 未连接。请先启动 FastAPI 或 Docker Compose，再重新打开岗位雷达。",
        )
        setErrorKind("api")
        setStatus("error")
      })

    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!scene) return
    if (!scene.map_available) {
      setMapAvailability("missing")
      setError("本地街道地图包不存在或无法读取，请先运行资源准备脚本。")
      setErrorKind("map")
      setStatus("error")
      return
    }
    const controller = new AbortController()
    const mapUrl = `${API_ROOT}/radar/maps/${encodeURIComponent(scene.map_name)}`

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
  }, [scene])

  useEffect(() => {
    if (mapAvailability !== "available" || !scene || !center) return
    const container = mapContainer.current
    if (!container) return

    let animationFrame = 0
    let disposed = false
    let mapReady = false
    const mapUrl = `${API_ROOT}/radar/maps/${encodeURIComponent(scene.map_name)}`
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
      mapReady = true
      map.addSource("radar-jobs", {
        type: "geojson",
        data: scene.jobs,
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

      map.on("click", "radar-job-points", (event) => {
        const feature = event.features?.[0]
        const id = feature?.properties?.id
        if (typeof id === "string") setSelectedId(id)
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
        animationFrame = window.requestAnimationFrame(animate)
      }
      animationFrame = window.requestAnimationFrame(animate)
      setStatus("ready")
    })

    map.on("error", (event) => {
      if (disposed || mapReady) return
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
      mapRef.current = null
      map.remove()
    }
  }, [center, mapAvailability, scene])

  const adjustZoom = (amount: number) => {
    const map = mapRef.current
    if (!map) return
    map.easeTo({
      center: center ?? undefined,
      zoom: Math.min(17, Math.max(12.5, map.getZoom() + amount)),
      duration: 320,
    })
  }

  const recenter = () => {
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
      (event.target as HTMLElement).closest("button, a")
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
            ? "OFFLINE"
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

        {center && (
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
          <span>
            {String(signalCount).padStart(2, "0")} SIGNALS
            {scene && scene.unresolved_count > 0
              ? ` / ${scene.unresolved_count} PENDING`
              : ""}
          </span>
          <BriefcaseBusiness size={11} />
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
            <button
              className="radar-state-action"
              type="button"
              onClick={leaveRadar}
            >
              <ArrowLeft size={11} /> 返回岗位列表
            </button>
          </div>
        )}

        {selectedJob && (
          <article className="radar-signal-card" aria-live="polite">
            <div className="signal-index">
              <i />
              {selectedJob.id.toUpperCase()}
            </div>
            <h1>{selectedJob.title}</h1>
            <p>
              {selectedJob.company} · {selectedJob.source}
            </p>
            <strong>
              {selectedJob.distance_km === null
                ? "— km"
                : `${selectedJob.distance_km.toFixed(1)} km`}
            </strong>
          </article>
        )}

        <footer className="radar-map-footer">
          <span>
            {scene?.mode === "fictional_demo"
              ? "FICTIONAL DEMO DATA"
              : "LOCAL PRIVATE SCENE"}
          </span>
          <a
            href="https://www.openstreetmap.org/copyright"
            target="_blank"
            rel="noreferrer"
          >
            © OpenStreetMap contributors
          </a>
        </footer>
      </main>

      <button className="radar-back-link" type="button" onClick={leaveRadar}>
        <ArrowLeft size={13} /> 返回主看板
      </button>
    </div>
  )
}

export default RadarApp
