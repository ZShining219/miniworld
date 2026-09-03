#!/usr/bin/env bash

set -euo pipefail

API_BASE="${API_BASE:-http://127.0.0.1:8000/api/v1}"
DEMO_FILE="backend/tests/fixtures/demo-profile.md"
VERIFY_RESTART="${VERIFY_RESTART:-true}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "missing required command: $1" >&2
    exit 1
  fi
}

json_post() {
  local path="$1"
  local payload="$2"
  curl -fsS \
    -H "Content-Type: application/json" \
    -X POST \
    --data "$payload" \
    "${API_BASE}${path}"
}

assert_json() {
  local payload="$1"
  local expression="$2"
  local description="$3"
  if ! jq -e "$expression" >/dev/null <<<"$payload"; then
    echo "verification failed: $description" >&2
    jq . <<<"$payload" >&2
    exit 1
  fi
}

require_command curl
require_command docker-compose
require_command jq
require_command grep

health="$(curl -fsS "${API_BASE}/health")"
assert_json "$health" '.status == "ok" and .execution_mode == "demo" and .database == "postgresql" and .checkpoint_mode == "postgres"' "PostgreSQL demo health"

overview="$(curl -fsS "${API_BASE}/overview")"
assert_json "$overview" '.execution_mode == "demo" and .provider_mode == "demo" and (.live_job_search_enabled | not) and .location_configured and .landmark_count >= 2' "safe seeded overview"

location="$(curl -fsS "${API_BASE}/location")"
assert_json "$location" '.configured and .is_demo and (has("exact_address") | not) and (has("latitude") | not) and (has("longitude") | not)' "masked location response"

job_payload='{"query":"internship","live":false}'
job_run_one="$(json_post "/job-runs" "$job_payload")"
assert_json "$job_run_one" '.graph_name == "job_discovery" and .execution_mode == "demo" and .status == "succeeded"' "first job graph run"
jobs_after_one="$(curl -fsS "${API_BASE}/jobs")"
assert_json "$jobs_after_one" 'length >= 3 and all(.[]; .distance_status == "calculated" and .distance_reason == null and (.distance_km | type == "number"))' "job distance results"
job_count_one="$(jq 'length' <<<"$jobs_after_one")"

job_run_two="$(json_post "/job-runs" "$job_payload")"
assert_json "$job_run_two" '.status == "succeeded"' "idempotent second job graph run"
jobs_after_two="$(curl -fsS "${API_BASE}/jobs")"
job_count_two="$(jq 'length' <<<"$jobs_after_two")"
if [[ "$job_count_one" != "$job_count_two" ]]; then
  echo "verification failed: repeated job discovery changed unique job count" >&2
  exit 1
fi

live_gate="$(json_post "/job-runs" '{"query":"internship","live":true}')"
assert_json "$live_gate" '.status == "awaiting_configuration" and .current_node == "mode_gate"' "live mode gate"

existing_imports="$(curl -fsS "${API_BASE}/imports")"
file_id="$(jq -r 'first(.[] | select(.source_type == "file" and .source_label == "demo-profile.md" and .status == "processed")) | .id // empty' <<<"$existing_imports")"
if [[ -z "$file_id" ]]; then
  file_artifact="$(curl -fsS -X POST -F "file=@${DEMO_FILE};type=text/markdown" "${API_BASE}/imports/file")"
  file_id="$(jq -r '.id' <<<"$file_artifact")"
  file_run="$(curl -fsS -X POST "${API_BASE}/imports/${file_id}/process")"
  assert_json "$file_run" '.graph_name == "profile_ingestion" and .status == "succeeded"' "file import graph"
fi

github_payload="$(jq -cn \
  --arg label "公开 GitHub 项目说明（演示）" \
  --arg content $'项目：MiniWorld Agent\n技能：Python 和 LangGraph\n成果：完成本地演示' \
  '{source_type:"github",source_label:$label,content:$content}')"
github_id="$(jq -r 'first(.[] | select(.source_type == "github" and .source_label == "公开 GitHub 项目说明（演示）" and .status == "processed")) | .id // empty' <<<"$existing_imports")"
if [[ -z "$github_id" ]]; then
  github_artifact="$(json_post "/imports/text" "$github_payload")"
  github_id="$(jq -r '.id' <<<"$github_artifact")"
  github_run="$(curl -fsS -X POST "${API_BASE}/imports/${github_id}/process")"
  assert_json "$github_run" '.status == "succeeded"' "GitHub material graph"
fi

gpt_payload="$(jq -cn \
  --arg label "GPT 对话导出（演示）" \
  --arg content $'项目：Agent 工作流讨论\n技能：结构化输出\n成果：明确本地隐私边界' \
  '{source_type:"gpt_conversation",source_label:$label,content:$content}')"
gpt_id="$(jq -r 'first(.[] | select(.source_type == "gpt_conversation" and .source_label == "GPT 对话导出（演示）" and .status == "processed")) | .id // empty' <<<"$existing_imports")"
if [[ -z "$gpt_id" ]]; then
  gpt_artifact="$(json_post "/imports/text" "$gpt_payload")"
  gpt_id="$(jq -r '.id' <<<"$gpt_artifact")"
  gpt_run="$(curl -fsS -X POST "${API_BASE}/imports/${gpt_id}/process")"
  assert_json "$gpt_run" '.status == "succeeded"' "GPT conversation graph"
fi

facts="$(curl -fsS "${API_BASE}/profile-facts")"
for artifact_id in "$file_id" "$github_id" "$gpt_id"; do
  if ! jq -e --arg id "$artifact_id" 'any(.[]; .evidence_artifact_id == $id)' >/dev/null <<<"$facts"; then
    echo "verification failed: profile fact has no evidence for ${artifact_id}" >&2
    exit 1
  fi
done
resumes="$(curl -fsS "${API_BASE}/resume-drafts")"
assert_json "$resumes" 'length >= 3 and .[0].version >= 3' "versioned resume drafts"

facts_before_work="$(jq 'length' <<<"$facts")"
existing_work_entries="$(curl -fsS "${API_BASE}/work-entries")"
entry_one_id="$(jq -r 'first(.[] | select(.work_date == "2026-08-17" and .content == "完成 API 骨架")) | .id // empty' <<<"$existing_work_entries")"
if [[ -z "$entry_one_id" ]]; then
  entry_one="$(json_post "/work-entries" '{"work_date":"2026-08-17","content":"完成 API 骨架","tags":["demo"]}')"
  assert_json "$entry_one" '.id != null' "first work entry"
fi
entry_two_id="$(jq -r 'first(.[] | select(.work_date == "2026-08-18" and .content == "完成前端看板；下一步验证容器")) | .id // empty' <<<"$existing_work_entries")"
if [[ -z "$entry_two_id" ]]; then
  entry_two="$(json_post "/work-entries" '{"work_date":"2026-08-18","content":"完成前端看板；下一步验证容器","tags":["demo"]}')"
  assert_json "$entry_two" '.id != null' "second work entry"
fi

reports="$(curl -fsS "${API_BASE}/reports")"
if ! jq -e 'any(.[]; .report_type == "daily" and .period_start == "2026-08-18" and .period_end == "2026-08-18")' >/dev/null <<<"$reports"; then
  daily="$(json_post "/reports" '{"report_type":"daily","period_start":"2026-08-18","period_end":"2026-08-18"}')"
  assert_json "$daily" '.graph_name == "work_report" and .status == "succeeded"' "daily report graph"
fi
if ! jq -e 'any(.[]; .report_type == "weekly" and .period_start == "2026-08-17" and .period_end == "2026-08-18")' >/dev/null <<<"$reports"; then
  weekly="$(json_post "/reports" '{"report_type":"weekly","period_start":"2026-08-17","period_end":"2026-08-18"}')"
  assert_json "$weekly" '.graph_name == "work_report" and .status == "succeeded"' "weekly report graph"
fi
reports="$(curl -fsS "${API_BASE}/reports")"
assert_json "$reports" 'any(.[]; .report_type == "daily" and (.source_entry_ids | length > 0)) and any(.[]; .report_type == "weekly" and (.source_entry_ids | length > 0))' "traceable reports"

# Produce a real node failure, fix its local precondition, and resume the same
# persisted PostgreSQL checkpoint. A second retry must be rejected so the
# successful business write cannot be duplicated.
existing_runs="$(curl -fsS "${API_BASE}/agent-runs?limit=500")"
recovered_run_id="$(jq -r 'first(.[] | select(.graph_name == "work_report" and .status == "succeeded" and .retry_count >= 1 and (.error_history | length >= 1))) | .id // empty' <<<"$existing_runs")"
if [[ -z "$recovered_run_id" ]]; then
  reports_before_retry="$(jq 'length' <<<"$reports")"
  existing_entries="$(curl -fsS "${API_BASE}/work-entries")"
  retry_year=2099
  while jq -e --arg work_date "${retry_year}-01-01" 'any(.[]; .work_date == $work_date)' >/dev/null <<<"$existing_entries"; do
    retry_year=$((retry_year + 1))
    if [[ "$retry_year" -gt 9999 ]]; then
      echo "verification failed: no free fictional date for checkpoint proof" >&2
      exit 1
    fi
  done
  retry_date="${retry_year}-01-01"
  failed_report_payload="$(jq -cn --arg retry_date "$retry_date" '{report_type:"daily",period_start:$retry_date,period_end:$retry_date}')"
  failed_report="$(json_post "/reports" "$failed_report_payload")"
  assert_json "$failed_report" '.status == "failed" and .current_node == "stopped" and (.error_history | length == 1)' "visible failed checkpoint run"
  recovered_run_id="$(jq -r '.id' <<<"$failed_report")"
  retry_entry_payload="$(jq -cn --arg retry_date "$retry_date" '{work_date:$retry_date,content:"用于 checkpoint 恢复验收的虚构记录",tags:["checkpoint-proof"]}')"
  retry_entry="$(json_post "/work-entries" "$retry_entry_payload")"
  assert_json "$retry_entry" '.id != null' "checkpoint retry precondition"
  recovered_report="$(curl -fsS -X POST "${API_BASE}/agent-runs/${recovered_run_id}/retry")"
  assert_json "$recovered_report" '.status == "succeeded" and .retry_count == 1 and (.error_history | length == 1)' "PostgreSQL checkpoint recovery"
  reports="$(curl -fsS "${API_BASE}/reports")"
  if [[ "$(jq 'length' <<<"$reports")" -ne $((reports_before_retry + 1)) ]]; then
    echo "verification failed: checkpoint retry created an unexpected report count" >&2
    exit 1
  fi
fi
retry_again_status="$(curl -sS -o /dev/null -w '%{http_code}' -X POST "${API_BASE}/agent-runs/${recovered_run_id}/retry")"
if [[ "$retry_again_status" != "409" ]]; then
  echo "verification failed: completed checkpoint retry was not protected from duplication" >&2
  exit 1
fi
reports="$(curl -fsS "${API_BASE}/reports")"
facts_after_work="$(curl -fsS "${API_BASE}/profile-facts" | jq 'length')"
if [[ "$facts_before_work" != "$facts_after_work" ]]; then
  echo "verification failed: work reporting modified profile facts" >&2
  exit 1
fi

schedule="$(curl -fsS -X POST "${API_BASE}/schedule/run-once")"
assert_json "$schedule" '.triggered' "forced local schedule tick"
runs="$(curl -fsS "${API_BASE}/agent-runs")"
assert_json "$runs" 'any(.[]; .graph_name == "job_discovery" and .trigger == "scheduler" and .execution_mode == "demo") and any(.[]; .graph_name == "profile_ingestion") and any(.[]; .graph_name == "work_report")' "three graph run history"

scheduler_count_before="$(jq '[.[] | select(.graph_name == "job_discovery" and .trigger == "scheduler")] | length' <<<"$runs")"
docker-compose exec -T db psql -U miniworld -d miniworld -v ON_ERROR_STOP=1 -c \
  "update schedule_config set last_triggered_at = null where id = 1" >/dev/null
scheduler_count_after="$scheduler_count_before"
for _ in {1..10}; do
  sleep 2
  scheduler_count_after="$(curl -fsS "${API_BASE}/agent-runs" | jq '[.[] | select(.graph_name == "job_discovery" and .trigger == "scheduler")] | length')"
  if [[ "$scheduler_count_after" -gt "$scheduler_count_before" ]]; then
    break
  fi
done
if [[ "$scheduler_count_after" -le "$scheduler_count_before" ]]; then
  echo "verification failed: Worker scheduler did not trigger a due job" >&2
  exit 1
fi

checkpoint_tables="$(docker-compose exec -T db psql -U miniworld -d miniworld -Atc \
  "select tablename from pg_tables where schemaname='public' and tablename in ('checkpoints','checkpoint_blobs','checkpoint_writes','checkpoint_migrations') order by tablename")"
if [[ "$(wc -l <<<"$checkpoint_tables" | tr -d ' ')" -ne 4 ]]; then
  echo "verification failed: LangGraph checkpoint tables are incomplete" >&2
  printf '%s\n' "$checkpoint_tables" >&2
  exit 1
fi
checkpoint_count="$(docker-compose exec -T db psql -U miniworld -d miniworld -Atc "select count(*) from checkpoints")"
if [[ "$checkpoint_count" -lt 1 ]]; then
  echo "verification failed: no persisted LangGraph checkpoints" >&2
  exit 1
fi
expected_migration="${EXPECTED_ALEMBIC_VERSION:-$(grep -RhoE 'revision: str = "[^"]+"' backend/app/alembic/versions \
  | sed -E 's/.*"([^"]+)"/\1/' \
  | sort \
  | tail -1)}"
migration="$(docker-compose exec -T db psql -U miniworld -d miniworld -Atc "select version_num from alembic_version")"
if [[ "$migration" != "$expected_migration" ]]; then
  echo "verification failed: unexpected Alembic version ${migration} (expected ${expected_migration})" >&2
  exit 1
fi

api_port="$(docker-compose port api 8000)"
frontend_port="$(docker-compose port frontend 80)"
if [[ "$api_port" != "127.0.0.1:8000" || "$frontend_port" != "127.0.0.1:5173" ]]; then
  echo "verification failed: published ports are not loopback-only" >&2
  printf 'api=%s frontend=%s\n' "$api_port" "$frontend_port" >&2
  exit 1
fi

if [[ "$VERIFY_RESTART" == "true" ]]; then
  overview_before_restart="$(curl -fsS "${API_BASE}/overview")"
  docker-compose restart db >/dev/null
  db_ready=false
  for _ in {1..15}; do
    if docker-compose exec -T db pg_isready -U miniworld -d miniworld >/dev/null 2>&1; then
      db_ready=true
      break
    fi
    sleep 2
  done
  if [[ "$db_ready" != "true" ]]; then
    echo "verification failed: PostgreSQL did not recover after restart" >&2
    exit 1
  fi

  docker-compose restart api worker frontend >/dev/null
  api_ready=false
  for _ in {1..30}; do
    if curl -fsS "${API_BASE}/health" >/dev/null 2>&1; then
      api_ready=true
      break
    fi
    sleep 2
  done
  if [[ "$api_ready" != "true" ]]; then
    echo "verification failed: API did not recover after restart" >&2
    exit 1
  fi
  curl -fsS http://127.0.0.1:5173 >/dev/null

  overview_after_restart="$(curl -fsS "${API_BASE}/overview")"
  for field in job_count fact_count resume_version work_entry_count report_count; do
    before="$(jq -r --arg field "$field" '.[$field]' <<<"$overview_before_restart")"
    after="$(jq -r --arg field "$field" '.[$field]' <<<"$overview_after_restart")"
    if [[ "$before" != "$after" ]]; then
      echo "verification failed: ${field} changed across container restart" >&2
      exit 1
    fi
  done
  checkpoint_count_after_restart="$(docker-compose exec -T db psql -U miniworld -d miniworld -Atc "select count(*) from checkpoints")"
  if [[ "$checkpoint_count_after_restart" -lt "$checkpoint_count" ]]; then
    echo "verification failed: checkpoint rows were lost across database restart" >&2
    exit 1
  fi
fi

public_payloads="$(printf '%s\n' "$health" "$overview" "$location" "$jobs_after_two" "$facts" "$resumes" "$reports" "$runs")"
for forbidden in "虚构演示住址（不会外发）" "31.2304" "121.4737"; do
  if grep -Fq "$forbidden" <<<"$public_payloads"; then
    echo "verification failed: restricted demo location leaked through public API" >&2
    exit 1
  fi
done

echo "MiniWorld container Demo verification passed"
echo "jobs=${job_count_two} facts=$(jq 'length' <<<"$facts") reports=$(jq 'length' <<<"$reports") checkpoints=${checkpoint_count}"
