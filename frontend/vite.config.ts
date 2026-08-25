import react from "@vitejs/plugin-react-swc"
import { defineConfig } from "vite"

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    // MapLibre resolves its worker next to the package entry. Pre-bundling the
    // entry moves it into .vite/deps without moving the worker beside it.
    exclude: ["maplibre-gl"],
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
  },
  preview: {
    host: "127.0.0.1",
    port: 5173,
  },
})
