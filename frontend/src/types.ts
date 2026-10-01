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
  salary_text: string | null
  job_type: string | null
  summary: string | null
  ai_summary: string | null
  geocode_source: string | null
  interview_role_id: string | null
  interview_level: string | null
  fingerprint: string
  published_at: string | null
  first_seen_at: string
  observed_at: string
}

export type RadarJobProperties = {
  id: string
  title: string
  company: string
  distance_km: number | null
  source: string
  url: string
  location_text: string
  salary_text: string | null
  job_type: string | null
  summary: string | null
  ai_summary: string | null
  geocode_source: string | null
  interview_role_id: string | null
  interview_level: string | null
  is_new: boolean
  published_at: string | null
  observed_at: string | null
}

export type RadarJobFeature = {
  type: "Feature"
  id: string
  geometry: {
    type: "Point"
    coordinates: [number, number]
  }
  properties: RadarJobProperties
}

export type RadarPendingJob = {
  id: string
  title: string
  company: string
  location_text: string
  source: string
}

export type RadarRunStatus = {
  finished_at: string | null
  status: string
  trigger: string
  execution_mode: string
  new_count: number
  updated_count: number
  failed_count: number
}

export type RadarScene = {
  mode: "fictional_demo" | "local"
  center: [number, number] | null
  jobs: {
    type: "FeatureCollection"
    features: RadarJobFeature[]
  }
  unresolved_count: number
  total_count: number
  pending_jobs: RadarPendingJob[]
  generated_at: string | null
  last_run: RadarRunStatus | null
  map_name: string
  map_available: boolean
}

export type InterviewHandoffResult = {
  job_id: string
  role_id: string | null
  level: string | null
  pushed: boolean
  push_channel: "none" | "admin_api" | "cli"
  file: string
  document_external_id: string
  detail: string | null
  push_response: Record<string, unknown> | null
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
  live_enabled: boolean
  sources: string[]
  query_text: string
  last_triggered_at: string | null
  last_run_at: string | null
  last_run_status: string | null
  last_run_new: number | null
  last_run_updated: number | null
  last_run_failed: number | null
  last_run_message: string | null
}
