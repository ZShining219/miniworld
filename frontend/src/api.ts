import type {
  AgentRun,
  Artifact,
  Job,
  Landmark,
  LocationStatus,
  Overview,
  ProfileFact,
  RadarScene,
  ResumeDraft,
  Schedule,
  WorkEntry,
  WorkReport,
} from "./types"

export const API_ROOT =
  import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1"

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_ROOT}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData
        ? {}
        : { "Content-Type": "application/json" }),
      ...init?.headers,
    },
  })
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`
    try {
      const body = (await response.json()) as { detail?: unknown }
      if (typeof body.detail === "string") detail = body.detail
      else if (body.detail) detail = JSON.stringify(body.detail)
    } catch {
      // Keep the status fallback.
    }
    throw new Error(detail)
  }
  if (response.status === 204) return undefined as T
  return (await response.json()) as T
}

export const api = {
  overview: () => request<Overview>("/overview"),
  radarScene: () => request<RadarScene>("/radar/scene"),
  jobs: () => request<Job[]>("/jobs"),
  runJobs: (query: string, live: boolean) =>
    request<AgentRun>("/job-runs", {
      method: "POST",
      body: JSON.stringify({ query, live }),
    }),
  imports: () => request<Artifact[]>("/imports"),
  createTextImport: (
    sourceType: Artifact["source_type"],
    label: string,
    content: string,
  ) =>
    request<Artifact>("/imports/text", {
      method: "POST",
      body: JSON.stringify({
        source_type: sourceType,
        source_label: label,
        content,
      }),
    }),
  uploadFile: (file: File) => {
    const data = new FormData()
    data.append("file", file)
    return request<Artifact>("/imports/file", { method: "POST", body: data })
  },
  processImport: (id: string) =>
    request<AgentRun>(`/imports/${id}/process`, { method: "POST" }),
  facts: () => request<ProfileFact[]>("/profile-facts"),
  setFactStatus: (id: string, status: "confirmed" | "rejected") =>
    request<ProfileFact>(`/profile-facts/${id}`, {
      method: "PATCH",
      body: JSON.stringify({ status }),
    }),
  resumes: () => request<ResumeDraft[]>("/resume-drafts"),
  workEntries: () => request<WorkEntry[]>("/work-entries"),
  createWorkEntry: (workDate: string, content: string, tags: string[]) =>
    request<WorkEntry>("/work-entries", {
      method: "POST",
      body: JSON.stringify({ work_date: workDate, content, tags }),
    }),
  reports: () => request<WorkReport[]>("/reports"),
  createReport: (reportType: "daily" | "weekly", start: string, end: string) =>
    request<AgentRun>("/reports", {
      method: "POST",
      body: JSON.stringify({
        report_type: reportType,
        period_start: start,
        period_end: end,
      }),
    }),
  runs: () => request<AgentRun[]>("/agent-runs"),
  retryRun: (id: string) =>
    request<AgentRun>(`/agent-runs/${id}/retry`, { method: "POST" }),
  location: () => request<LocationStatus>("/location"),
  setLocation: (exactAddress: string, latitude: number, longitude: number) =>
    request<LocationStatus>("/location", {
      method: "PUT",
      body: JSON.stringify({
        exact_address: exactAddress,
        latitude,
        longitude,
        is_demo: false,
      }),
    }),
  landmarks: () => request<Landmark[]>("/landmarks"),
  createLandmark: (name: string, queryText: string, order: number) =>
    request<Landmark>("/landmarks", {
      method: "POST",
      body: JSON.stringify({
        name,
        query_text: queryText,
        latitude: null,
        longitude: null,
        rotation_order: order,
        enabled: true,
      }),
    }),
  schedule: () => request<Schedule>("/schedule"),
  updateSchedule: (enabled: boolean, minutes: number) =>
    request<Schedule>("/schedule", {
      method: "PUT",
      body: JSON.stringify({
        job_discovery_enabled: enabled,
        interval_minutes: minutes,
      }),
    }),
  runScheduleOnce: () =>
    request<{ triggered: boolean }>("/schedule/run-once", { method: "POST" }),
}
