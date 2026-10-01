import "@ant-design/v5-patch-for-react-19"
import { App as AntApp, ConfigProvider, theme } from "antd"
import zhCN from "antd/locale/zh_CN"
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
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: theme.darkAlgorithm,
        token: {
          colorPrimary: "#d5ff4f",
          colorInfo: "#8bc8ff",
          colorSuccess: "#9be36d",
          colorWarning: "#ffd84d",
          colorError: "#ff7145",
          colorTextBase: "#f2f0e7",
          colorBgBase: "#0e0f0b",
          colorBgContainer: "#171913",
          colorBgElevated: "#1e2018",
          colorBorder: "#35392b",
          colorBorderSecondary: "#2b2e22",
          colorTextSecondary: "#8e9480",
          borderRadius: 8,
          fontFamily: '"Avenir Next", "PingFang SC", sans-serif',
        },
      }}
    >
      <AntApp>
        {isRadarSurface ? (
          <Suspense fallback={null}>
            <RadarApp />
          </Suspense>
        ) : (
          <App />
        )}
      </AntApp>
    </ConfigProvider>
  </StrictMode>,
)
