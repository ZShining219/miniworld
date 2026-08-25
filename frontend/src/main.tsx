import { lazy, StrictMode, Suspense } from "react"
import { createRoot } from "react-dom/client"
import App from "./App"
import "./styles.css"

const RadarApp = lazy(() => import("./radar/RadarApp"))

const root = document.getElementById("root")
if (!root) throw new Error("Root element is missing")

const isRadarSurface =
  window.location.pathname === "/radar" ||
  new URLSearchParams(window.location.search).get("surface") === "radar"
document.body.classList.toggle("radar-surface", isRadarSurface)

createRoot(root).render(
  <StrictMode>
    {isRadarSurface ? (
      <Suspense fallback={null}>
        <RadarApp />
      </Suspense>
    ) : (
      <App />
    )}
  </StrictMode>,
)
