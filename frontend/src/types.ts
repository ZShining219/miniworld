export type AgentRun = {
  id: string
  graph_name: string
  execution_mode: "demo" | "live"
  trigger: string
  status: string
  current_node: string | null
  message: string | null
  result_json: Record<string, unknown> | null
  retry_count: number
  error_history: Array<Record<string, unknown>>
  started_at: string
  finished_at: string | null
}

export type Overview = {
  execution_mode: string
  provider_mode: string
  live_job_search_enabled: boolean
  location_configured: boolean
  landmark_count: number
  job_count: number
  fact_count: number
  resume_version: number | null
  work_entry_count: number
  report_count: number
  pending_approvals: number
  recent_runs: AgentRun[]
}

export type Job = {
  id: string
  source: string
  external_id: string | null
  title: string
  company: string
  location_text: string
  distance_km: number | null
  distance_status: string
  distance_reason: string | null
  url: string
  job_type: string | null
  summary: string | null
  published_at: string | null
  observed_at: string
}

export type Artifact = {
  id: string
  source_type: "file" | "github" | "gpt_conversation"
  source_label: string
  content_sha256: string
  status: string
  created_at: string
  processed_at: string | null
}

export type ProfileFact = {
  id: string
  fact_type: string
  value_json: Record<string, unknown>
  status: string
  confidence: number
  evidence_artifact_id: string
  created_at: string
}

export type ResumeDraft = {
  id: string
  version: number
  content_json: Record<string, unknown>
  created_at: string
}

export type WorkEntry = {
  id: string
  work_date: string
  content: string
  tags: string[]
  created_at: string
  updated_at: string
}

export type WorkReport = {
  id: string
  report_type: string
  period_start: string
  period_end: string
  content: string
  source_entry_ids: string[]
  provider: string
  created_at: string
}

export type LocationStatus = {
  configured: boolean
  masked_address: string | null
  is_demo: boolean
  updated_at: string | null
}

export type Landmark = {
  id: string
  name: string
  query_text: string
  latitude: number | null
  longitude: number | null
  rotation_order: number
  enabled: boolean
  created_at: string
}

export type Schedule = {
  job_discovery_enabled: boolean
  interval_minutes: number
  last_triggered_at: string | null
}
