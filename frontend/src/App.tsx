import {
  Activity,
  Archive,
  ArrowUpRight,
  BriefcaseBusiness,
  CalendarDays,
  Check,
  ChevronRight,
  CircleAlert,
  FileText,
  Fingerprint,
  MapPin,
  Orbit,
  Play,
  Radar,
  RefreshCw,
  Settings2,
  ShieldCheck,
  Sparkles,
  Upload,
} from "lucide-react"
import { useCallback, useEffect, useMemo, useState } from "react"
import { api } from "./api"
import type {
  AgentRun,
  Artifact,
  Job,
  Landmark,
  LocationStatus,
  Overview,
  ProfileFact,
  ResumeDraft,
  Schedule,
  WorkEntry,
  WorkReport,
} from "./types"

type View = "overview" | "jobs" | "profile" | "work" | "runs" | "settings"
type Notify = (message: string, tone?: "good" | "bad") => void

const NAV: Array<{
  id: View
  label: string
  hint: string
  icon: typeof Radar
}> = [
  { id: "overview", label: "雷达总览", hint: "Overview", icon: Radar },
  { id: "jobs", label: "岗位信号", hint: "Jobs", icon: BriefcaseBusiness },
  { id: "profile", label: "个人档案", hint: "Profile", icon: Fingerprint },
  { id: "work", label: "工作沉淀", hint: "Work", icon: CalendarDays },
  { id: "runs", label: "Agent 运行", hint: "Runs", icon: Activity },
  { id: "settings", label: "本地设置", hint: "Settings", icon: Settings2 },
]

const TODAY = new Date().toISOString().slice(0, 10)

function formatTime(value: string | null): string {
  if (!value) return "—"
  return new Intl.DateTimeFormat("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value))
}

function statusTone(status: string): string {
  if (["succeeded", "processed", "confirmed", "calculated"].includes(status)) {
    return "status good"
  }
  if (["failed", "rejected", "blocked_by_policy"].includes(status)) {
    return "status bad"
  }
  return "status waiting"
}

function App() {
  const [view, setView] = useState<View>("overview")
  const [notice, setNotice] = useState<{
    message: string
    tone: "good" | "bad"
  } | null>(null)

  const notify: Notify = useCallback((message, tone = "good") => {
    setNotice({ message, tone })
    window.setTimeout(() => setNotice(null), 4200)
  }, [])

  const current = NAV.find((item) => item.id === view) ?? NAV[0]

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <button
          className="brand"
          type="button"
          onClick={() => setView("overview")}
        >
          <span className="brand-mark">
            <Orbit size={22} />
          </span>
          <span>
            <b>MINIWORLD</b>
            <small>PERSONAL AGENT / 01</small>
          </span>
        </button>

        <div className="sidebar-label">工作台 / MODULES</div>
        <nav>
          {NAV.map((item) => {
            const Icon = item.icon
            return (
              <button
                type="button"
                className={`nav-item ${view === item.id ? "active" : ""}`}
                key={item.id}
                onClick={() => setView(item.id)}
              >
                <Icon size={18} />
                <span>
                  <b>{item.label}</b>
                  <small>{item.hint}</small>
                </span>
                <ChevronRight size={14} />
              </button>
            )
          })}
        </nav>

        <div className="privacy-seal">
          <ShieldCheck size={23} />
          <div>
            <b>LOCAL FIRST</b>
            <span>精确地址不离开本机</span>
          </div>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div>
            <span className="eyebrow">{current.hint} / 个人成长操作系统</span>
            <h1>{current.label}</h1>
          </div>
          <div className="mode-chip">
            <span /> DEMO MODE · 本地确定性
          </div>
        </header>

        <section className="content" key={view}>
          {view === "overview" && <OverviewPage notify={notify} go={setView} />}
          {view === "jobs" && <JobsPage notify={notify} />}
          {view === "profile" && <ProfilePage notify={notify} />}
          {view === "work" && <WorkPage notify={notify} />}
          {view === "runs" && <RunsPage notify={notify} />}
          {view === "settings" && <SettingsPage notify={notify} />}
        </section>
      </main>

      {notice && <div className={`toast ${notice.tone}`}>{notice.message}</div>}
    </div>
  )
}

function OverviewPage({
  notify,
  go,
}: {
  notify: Notify
  go: (view: View) => void
}) {
  const [data, setData] = useState<Overview | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setLoading(true)
    try {
      setData(await api.overview())
    } catch (error) {
      notify(error instanceof Error ? error.message : "无法载入总览", "bad")
    } finally {
      setLoading(false)
    }
  }, [notify])

  useEffect(() => {
    void load()
  }, [load])

  if (loading && !data) return <Loading />
  if (!data) return <Empty title="API 尚未连接" text="请先启动后端服务。" />

  const stats = [
    ["岗位信号", data.job_count, "含直线距离", "lime"],
    [
      "档案事实",
      data.fact_count,
      `简历 v${data.resume_version ?? "—"}`,
      "orange",
    ],
    ["工作记录", data.work_entry_count, `${data.report_count} 份报告`, "cream"],
    ["待确认", data.pending_approvals, "外部行为闸门", "muted"],
  ] as const

  return (
    <div className="page-stack">
      <div className="hero-grid">
        <article className="radar-card panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">SIGNAL FIELD</span>
              <h2>个人机会雷达</h2>
            </div>
            <button
              className="icon-button"
              type="button"
              onClick={() => void load()}
              aria-label="刷新"
            >
              <RefreshCw size={17} />
            </button>
          </div>
          <div
            className="radar-visual"
            role="img"
            aria-label="三个独立 Agent 闭环状态示意"
          >
            <div className="radar-ring ring-1" />
            <div className="radar-ring ring-2" />
            <div className="radar-ring ring-3" />
            <div className="sweep" />
            <span className="radar-origin">
              <Orbit size={18} />
            </span>
            <button
              className="signal signal-jobs"
              type="button"
              onClick={() => go("jobs")}
            >
              <i />
              岗位 {data.job_count}
            </button>
            <button
              className="signal signal-profile"
              type="button"
              onClick={() => go("profile")}
            >
              <i />
              档案 {data.fact_count}
            </button>
            <button
              className="signal signal-work"
              type="button"
              onClick={() => go("work")}
            >
              <i />
              沉淀 {data.work_entry_count}
            </button>
          </div>
          <div className="radar-caption">
            <span>HOME ORIGIN / 本机坐标</span>
            <span>距离只在本地计算</span>
          </div>
        </article>

        <article className="manifesto panel">
          <span className="index-no">01</span>
          <span className="eyebrow">TODAY'S DIRECTIVE</span>
          <h2>
            找到机会，
            <br />
            沉淀证据，
            <br />
            <em>记录成长。</em>
          </h2>
          <p>
            三个 Graph 独立运行。岗位不会改写简历，日报不会未经确认进入档案。
          </p>
          <div className="mode-grid">
            <div>
              <b>{data.execution_mode.toUpperCase()}</b>
              <span>执行模式</span>
            </div>
            <div>
              <b>{data.provider_mode.toUpperCase()}</b>
              <span>模型 Provider</span>
            </div>
          </div>
        </article>
      </div>

      <div className="stats-grid">
        {stats.map(([label, value, hint, color]) => (
          <article className={`stat-card panel ${color}`} key={label}>
            <span>{label}</span>
            <strong>{String(value).padStart(2, "0")}</strong>
            <small>{hint}</small>
          </article>
        ))}
      </div>

      <div className="split-grid">
        <article className="panel run-list">
          <div className="panel-head">
            <div>
              <span className="eyebrow">RECENT RUNS</span>
              <h2>最近运行</h2>
            </div>
            <button
              className="text-button"
              type="button"
              onClick={() => go("runs")}
            >
              查看全部 <ArrowUpRight size={15} />
            </button>
          </div>
          {data.recent_runs.length ? (
            data.recent_runs.map((run) => <RunRow run={run} key={run.id} />)
          ) : (
            <Empty title="尚无运行" text="从任一模块发起首次任务。" />
          )}
        </article>
        <article className="panel boundary-card">
          <span className="eyebrow">PRIVACY BOUNDARY</span>
          <h2>两步位置策略</h2>
          <ol>
            <li>
              <b>本地精确地址</b>
              <span>只用于最终 Haversine 计算</span>
            </li>
            <li>
              <b>附近变动地标</b>
              <span>用于面向公开来源的查询</span>
            </li>
          </ol>
          <button
            className="secondary-button"
            type="button"
            onClick={() => go("settings")}
          >
            <MapPin size={16} /> 检查位置设置
          </button>
        </article>
      </div>
    </div>
  )
}

function JobsPage({ notify }: { notify: Notify }) {
  const [jobs, setJobs] = useState<Job[]>([])
  const [query, setQuery] = useState("实习 OR internship")
  const [running, setRunning] = useState(false)
  const load = useCallback(async () => setJobs(await api.jobs()), [])
  useEffect(() => {
    void load().catch((error: Error) => notify(error.message, "bad"))
  }, [load, notify])

  async function run() {
    setRunning(true)
    try {
      const result = await api.runJobs(query, false)
      notify(
        result.status === "succeeded"
          ? "岗位雷达完成一次本地扫描"
          : (result.message ?? result.status),
        result.status === "succeeded" ? "good" : "bad",
      )
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "运行失败", "bad")
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="page-stack">
      <article className="command-bar panel">
        <div>
          <span className="eyebrow">JOB DISCOVERY GRAPH</span>
          <h2>扫描公开岗位信号</h2>
          <p>外部查询只使用附近地标；精确住址只在本地参与距离计算。</p>
        </div>
        <div className="command-actions">
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            aria-label="岗位关键词"
          />
          <button
            className="primary-button"
            type="button"
            onClick={() => void run()}
            disabled={running}
          >
            <Play size={16} />
            {running ? "扫描中" : "运行 Demo 扫描"}
          </button>
        </div>
      </article>
      <article className="panel table-panel">
        <div className="panel-head">
          <div>
            <span className="eyebrow">DISTANCE INDEX</span>
            <h2>{jobs.length} 个岗位</h2>
          </div>
          <span className="legend">
            <i /> 直线距离 / KM
          </span>
        </div>
        {jobs.length ? (
          <div className="job-list">
            {jobs.map((job, index) => (
              <a
                className="job-row"
                href={job.url}
                target="_blank"
                rel="noreferrer"
                key={job.id}
              >
                <span className="row-index">
                  {String(index + 1).padStart(2, "0")}
                </span>
                <div className="job-main">
                  <strong>{job.title}</strong>
                  <span>
                    {job.company} · {job.location_text}
                  </span>
                  <small>{job.summary}</small>
                  {job.distance_reason && (
                    <small className="distance-reason">
                      距离说明：{job.distance_reason}
                    </small>
                  )}
                </div>
                <div className="job-meta">
                  <span className={statusTone(job.distance_status)}>
                    {job.distance_status}
                  </span>
                  <b>
                    {job.distance_km === null
                      ? "—"
                      : job.distance_km.toFixed(1)}
                    <small> KM</small>
                  </b>
                  <em>{job.source}</em>
                </div>
                <ArrowUpRight size={17} />
              </a>
            ))}
          </div>
        ) : (
          <Empty
            title="雷达尚未捕获岗位"
            text="运行一次 Demo 扫描即可验证距离闭环。"
          />
        )}
      </article>
    </div>
  )
}

function ProfilePage({ notify }: { notify: Notify }) {
  const [artifacts, setArtifacts] = useState<Artifact[]>([])
  const [facts, setFacts] = useState<ProfileFact[]>([])
  const [resumes, setResumes] = useState<ResumeDraft[]>([])
  const [sourceType, setSourceType] =
    useState<Artifact["source_type"]>("github")
  const [label, setLabel] = useState("公开材料 / 手动导入")
  const [content, setContent] = useState(
    "项目：MiniWorld Agent\n技能：Python、LangGraph、React\n成果：完成本地优先的三闭环产品设计",
  )
  const load = useCallback(async () => {
    const [nextArtifacts, nextFacts, nextResumes] = await Promise.all([
      api.imports(),
      api.facts(),
      api.resumes(),
    ])
    setArtifacts(nextArtifacts)
    setFacts(nextFacts)
    setResumes(nextResumes)
  }, [])
  useEffect(() => {
    void load().catch((error: Error) => notify(error.message, "bad"))
  }, [load, notify])

  async function createText() {
    try {
      await api.createTextImport(sourceType, label, content)
      notify("材料已保存到本地，等待处理")
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "导入失败", "bad")
    }
  }
  async function upload(file: File | undefined) {
    if (!file) return
    try {
      await api.uploadFile(file)
      notify("文件已在本地转换并保存")
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "文件导入失败", "bad")
    }
  }
  async function process(id: string) {
    try {
      const run = await api.processImport(id)
      notify(
        run.message ?? run.status,
        run.status === "succeeded" ? "good" : "bad",
      )
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "处理失败", "bad")
    }
  }

  return (
    <div className="page-stack">
      <div className="split-grid profile-top">
        <article className="panel form-panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">MANUAL INGESTION</span>
              <h2>导入新的个人证据</h2>
            </div>
            <Upload size={20} />
          </div>
          <div className="field-row">
            <label>
              来源类型
              <select
                value={sourceType}
                onChange={(event) =>
                  setSourceType(event.target.value as Artifact["source_type"])
                }
              >
                <option value="file">文件文字</option>
                <option value="github">GitHub 公开材料</option>
                <option value="gpt_conversation">GPT 对话导出</option>
              </select>
            </label>
            <label>
              来源标签
              <input
                value={label}
                onChange={(event) => setLabel(event.target.value)}
              />
            </label>
          </div>
          <label>
            材料正文
            <textarea
              rows={7}
              value={content}
              onChange={(event) => setContent(event.target.value)}
            />
          </label>
          <div className="form-actions">
            <label className="file-button">
              <Upload size={15} /> 选择本地文件
              <input
                type="file"
                onChange={(event) => void upload(event.target.files?.[0])}
              />
            </label>
            <button
              className="primary-button"
              type="button"
              onClick={() => void createText()}
            >
              <Archive size={16} /> 保存材料
            </button>
          </div>
        </article>
        <article className="panel resume-preview">
          <span className="eyebrow">LATEST RESUME DRAFT</span>
          <h2>结构化简历草稿</h2>
          {resumes[0] ? (
            <>
              <div className="resume-version">
                V{resumes[0].version.toString().padStart(2, "0")}
              </div>
              <pre>{JSON.stringify(resumes[0].content_json, null, 2)}</pre>
            </>
          ) : (
            <Empty title="尚无草稿" text="处理一份材料后生成首个版本。" />
          )}
        </article>
      </div>
      <div className="split-grid">
        <article className="panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">SOURCE LEDGER</span>
              <h2>材料台账</h2>
            </div>
            <span>{artifacts.length} ITEMS</span>
          </div>
          <div className="compact-list">
            {artifacts.map((item) => (
              <div className="compact-row" key={item.id}>
                <FileText size={17} />
                <div>
                  <b>{item.source_label}</b>
                  <span>
                    {item.source_type} · {item.content_sha256.slice(0, 10)}
                  </span>
                </div>
                <span className={statusTone(item.status)}>{item.status}</span>
                {item.status !== "processed" && (
                  <button
                    className="mini-button"
                    type="button"
                    onClick={() => void process(item.id)}
                  >
                    处理
                  </button>
                )}
              </div>
            ))}
          </div>
        </article>
        <article className="panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">EVIDENCE FACTS</span>
              <h2>可追溯事实</h2>
            </div>
            <span>{facts.length} FACTS</span>
          </div>
          <div className="compact-list">
            {facts.map((fact) => (
              <div className="fact-row" key={fact.id}>
                <div>
                  <b>{fact.fact_type}</b>
                  <span>
                    {String(
                      fact.value_json.text ?? JSON.stringify(fact.value_json),
                    )}
                  </span>
                  <small>
                    置信度 {Math.round(fact.confidence * 100)}% · 证据{" "}
                    {fact.evidence_artifact_id.slice(0, 8)}
                  </small>
                </div>
                <span className={statusTone(fact.status)}>{fact.status}</span>
              </div>
            ))}
          </div>
        </article>
      </div>
    </div>
  )
}

function WorkPage({ notify }: { notify: Notify }) {
  const [entries, setEntries] = useState<WorkEntry[]>([])
  const [reports, setReports] = useState<WorkReport[]>([])
  const [date, setDate] = useState(TODAY)
  const [content, setContent] = useState(
    "完成 MiniWorld Agent 的本地运行骨架与隐私策略测试",
  )
  const [tags, setTags] = useState("agent,demo")
  const [reportType, setReportType] = useState<"daily" | "weekly">("daily")
  const [start, setStart] = useState(TODAY)
  const [end, setEnd] = useState(TODAY)
  const load = useCallback(async () => {
    const [nextEntries, nextReports] = await Promise.all([
      api.workEntries(),
      api.reports(),
    ])
    setEntries(nextEntries)
    setReports(nextReports)
  }, [])
  useEffect(() => {
    void load().catch((error: Error) => notify(error.message, "bad"))
  }, [load, notify])

  async function save() {
    try {
      await api.createWorkEntry(
        date,
        content,
        tags
          .split(",")
          .map((tag) => tag.trim())
          .filter(Boolean),
      )
      notify("工作记录已沉淀到本地")
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "保存失败", "bad")
    }
  }
  async function report() {
    try {
      const run = await api.createReport(
        reportType,
        start,
        reportType === "daily" ? start : end,
      )
      notify(
        run.message ?? run.status,
        run.status === "succeeded" ? "good" : "bad",
      )
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "生成失败", "bad")
    }
  }

  return (
    <div className="page-stack">
      <div className="split-grid">
        <article className="panel form-panel">
          <span className="eyebrow">DAILY CAPTURE</span>
          <h2>记录今天完成的事</h2>
          <label>
            日期
            <input
              type="date"
              value={date}
              onChange={(event) => setDate(event.target.value)}
            />
          </label>
          <label>
            工作内容
            <textarea
              rows={5}
              value={content}
              onChange={(event) => setContent(event.target.value)}
            />
          </label>
          <label>
            标签 / 逗号分隔
            <input
              value={tags}
              onChange={(event) => setTags(event.target.value)}
            />
          </label>
          <button
            className="primary-button"
            type="button"
            onClick={() => void save()}
          >
            <Check size={16} /> 保存工作记录
          </button>
        </article>
        <article className="panel form-panel report-command">
          <span className="eyebrow">REPORT GRAPH</span>
          <h2>生成日报 / 周报</h2>
          <div className="segmented">
            <button
              className={reportType === "daily" ? "active" : ""}
              type="button"
              onClick={() => setReportType("daily")}
            >
              日报
            </button>
            <button
              className={reportType === "weekly" ? "active" : ""}
              type="button"
              onClick={() => setReportType("weekly")}
            >
              周报
            </button>
          </div>
          <div className="field-row">
            <label>
              开始
              <input
                type="date"
                value={start}
                onChange={(event) => setStart(event.target.value)}
              />
            </label>
            {reportType === "weekly" && (
              <label>
                结束
                <input
                  type="date"
                  value={end}
                  onChange={(event) => setEnd(event.target.value)}
                />
              </label>
            )}
          </div>
          <p>报告只读取所选日期范围的工作记录，不会自动写入个人档案。</p>
          <button
            className="secondary-button"
            type="button"
            onClick={() => void report()}
          >
            <Sparkles size={16} /> 生成
            {reportType === "daily" ? "日报" : "周报"}
          </button>
        </article>
      </div>
      <div className="split-grid">
        <article className="panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">WORK LEDGER</span>
              <h2>原始记录</h2>
            </div>
            <span>{entries.length} ENTRIES</span>
          </div>
          <div className="timeline">
            {entries.map((entry) => (
              <div className="timeline-item" key={entry.id}>
                <time>{entry.work_date}</time>
                <div>
                  <b>{entry.content}</b>
                  <span>{entry.tags.map((tag) => `#${tag}`).join("  ")}</span>
                </div>
              </div>
            ))}
          </div>
        </article>
        <article className="panel">
          <div className="panel-head">
            <div>
              <span className="eyebrow">GENERATED REPORTS</span>
              <h2>报告版本</h2>
            </div>
            <span>{reports.length} REPORTS</span>
          </div>
          <div className="report-list">
            {reports.map((item) => (
              <details key={item.id}>
                <summary>
                  <span className="status good">{item.report_type}</span>
                  <b>
                    {item.period_start} → {item.period_end}
                  </b>
                  <small>{item.provider}</small>
                </summary>
                <pre>{item.content}</pre>
              </details>
            ))}
          </div>
        </article>
      </div>
    </div>
  )
}

function RunsPage({ notify }: { notify: Notify }) {
  const [runs, setRuns] = useState<AgentRun[]>([])
  const [loading, setLoading] = useState(true)
  const [retrying, setRetrying] = useState<string | null>(null)
  const load = useCallback(async () => {
    setLoading(true)
    try {
      setRuns(await api.runs())
    } finally {
      setLoading(false)
    }
  }, [])
  useEffect(() => {
    void load()
  }, [load])
  async function retry(run: AgentRun) {
    setRetrying(run.id)
    try {
      const result = await api.retryRun(run.id)
      notify(
        result.status === "succeeded"
          ? "已从 LangGraph checkpoint 恢复并完成"
          : (result.message ?? result.status),
        result.status === "succeeded" ? "good" : "bad",
      )
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "重试失败", "bad")
    } finally {
      setRetrying(null)
    }
  }
  return (
    <article className="panel run-ledger">
      <div className="panel-head">
        <div>
          <span className="eyebrow">EXECUTION LEDGER</span>
          <h2>可审计 Agent 运行</h2>
        </div>
        <button
          className="icon-button"
          type="button"
          onClick={() => void load()}
        >
          <RefreshCw size={17} />
        </button>
      </div>
      {loading && !runs.length ? (
        <Loading />
      ) : (
        runs.map((run) => (
          <RunRow
            run={run}
            key={run.id}
            expanded
            onRetry={run.status === "failed" ? retry : undefined}
            retrying={retrying === run.id}
          />
        ))
      )}
    </article>
  )
}

function SettingsPage({ notify }: { notify: Notify }) {
  const [location, setLocation] = useState<LocationStatus | null>(null)
  const [landmarks, setLandmarks] = useState<Landmark[]>([])
  const [schedule, setSchedule] = useState<Schedule | null>(null)
  const [address, setAddress] = useState("")
  const [lat, setLat] = useState("")
  const [lon, setLon] = useState("")
  const [landmarkName, setLandmarkName] = useState("新的附近地标")
  const [landmarkQuery, setLandmarkQuery] = useState("地标附近")
  const load = useCallback(async () => {
    const [nextLocation, nextLandmarks, nextSchedule] = await Promise.all([
      api.location(),
      api.landmarks(),
      api.schedule(),
    ])
    setLocation(nextLocation)
    setLandmarks(nextLandmarks)
    setSchedule(nextSchedule)
  }, [])
  useEffect(() => {
    void load().catch((error: Error) => notify(error.message, "bad"))
  }, [load, notify])
  async function saveLocation() {
    try {
      await api.setLocation(address, Number(lat), Number(lon))
      setAddress("")
      setLat("")
      setLon("")
      notify("精确位置已仅保存到本机，接口不会回显")
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "保存失败", "bad")
    }
  }
  async function addLandmark() {
    try {
      await api.createLandmark(landmarkName, landmarkQuery, landmarks.length)
      notify("附近地标已加入轮换")
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "添加失败", "bad")
    }
  }
  async function saveSchedule(enabled: boolean) {
    if (!schedule) return
    try {
      await api.updateSchedule(enabled, schedule.interval_minutes)
      notify("定时读取策略已更新")
      await load()
    } catch (error) {
      notify(error instanceof Error ? error.message : "更新失败", "bad")
    }
  }
  async function runOnce() {
    try {
      const result = await api.runScheduleOnce()
      notify(
        result.triggered ? "已模拟一次 Worker 定时触发" : "调度当前未启用",
        result.triggered ? "good" : "bad",
      )
    } catch (error) {
      notify(error instanceof Error ? error.message : "触发失败", "bad")
    }
  }

  return (
    <div className="page-stack settings-grid">
      <form
        className="panel form-panel"
        onSubmit={(event) => {
          event.preventDefault()
          void saveLocation()
        }}
      >
        <div className="panel-head">
          <div>
            <span className="eyebrow">RESTRICTED LOCAL</span>
            <h2>精确住址与坐标</h2>
          </div>
          <ShieldCheck size={21} />
        </div>
        <div className="privacy-banner">
          <b>{location?.configured ? "已配置" : "未配置"}</b>
          <span>
            {location?.masked_address ?? "仅在本地保存"} ·{" "}
            {location?.is_demo ? "当前为演示数据" : "用户数据"}
          </span>
        </div>
        <label>
          精确地址（提交后不回显）
          <input
            type="text"
            autoComplete="off"
            spellCheck={false}
            value={address}
            onChange={(event) => setAddress(event.target.value)}
            placeholder="仅在本机输入"
          />
        </label>
        <div className="field-row">
          <label>
            纬度
            <input
              inputMode="decimal"
              value={lat}
              onChange={(event) => setLat(event.target.value)}
              placeholder="仅在本机填写"
            />
          </label>
          <label>
            经度
            <input
              inputMode="decimal"
              value={lon}
              onChange={(event) => setLon(event.target.value)}
              placeholder="仅在本机填写"
            />
          </label>
        </div>
        <button
          className="primary-button"
          type="submit"
          disabled={!address || !lat || !lon}
        >
          <ShieldCheck size={16} /> 本地保存
        </button>
      </form>
      <article className="panel form-panel">
        <span className="eyebrow">PUBLIC QUERY LANDMARKS</span>
        <h2>附近变动地标</h2>
        <div className="compact-list">
          {landmarks.map((item) => (
            <div className="compact-row" key={item.id}>
              <MapPin size={17} />
              <div>
                <b>{item.name}</b>
                <span>{item.query_text}</span>
              </div>
              <span
                className={statusTone(item.enabled ? "succeeded" : "disabled")}
              >
                {item.enabled ? "启用" : "停用"}
              </span>
            </div>
          ))}
        </div>
        <div className="field-row">
          <label>
            名称
            <input
              value={landmarkName}
              onChange={(event) => setLandmarkName(event.target.value)}
            />
          </label>
          <label>
            公开查询文本
            <input
              value={landmarkQuery}
              onChange={(event) => setLandmarkQuery(event.target.value)}
            />
          </label>
        </div>
        <button
          className="secondary-button"
          type="button"
          onClick={() => void addLandmark()}
        >
          <MapPin size={16} /> 添加地标
        </button>
      </article>
      <article className="panel schedule-panel">
        <span className="eyebrow">SCHEDULER / LOCAL WORKER</span>
        <h2>定时公开读取</h2>
        <div className="big-toggle">
          <button
            type="button"
            className={schedule?.job_discovery_enabled ? "on" : ""}
            onClick={() => void saveSchedule(!schedule?.job_discovery_enabled)}
          >
            <span />
          </button>
          <div>
            <b>{schedule?.job_discovery_enabled ? "已启用" : "已暂停"}</b>
            <small>间隔 {schedule?.interval_minutes ?? "—"} 分钟</small>
          </div>
        </div>
        <p>Worker 只运行 Demo 岗位读取和限定本地更新。外部写入始终需要确认。</p>
        <button
          className="secondary-button"
          type="button"
          onClick={() => void runOnce()}
        >
          <Play size={16} /> 验证一次定时触发
        </button>
      </article>
    </div>
  )
}

function RunRow({
  run,
  expanded = false,
  onRetry,
  retrying = false,
}: {
  run: AgentRun
  expanded?: boolean
  onRetry?: (run: AgentRun) => void
  retrying?: boolean
}) {
  const details = useMemo(
    () => (run.result_json ? JSON.stringify(run.result_json) : run.message),
    [run],
  )
  return (
    <div className={`run-row ${expanded ? "expanded" : ""}`}>
      <span className="run-icon">
        {run.status === "succeeded" ? (
          <Check size={16} />
        ) : run.status === "failed" ? (
          <CircleAlert size={16} />
        ) : (
          <Activity size={16} />
        )}
      </span>
      <div>
        <b>{run.graph_name.split("_").join(" ")}</b>
        <span>
          {run.trigger} · {run.current_node ?? "queued"}
        </span>
        {expanded && details && <small>{details}</small>}
      </div>
      <span className={statusTone(run.status)}>{run.status}</span>
      <time>{formatTime(run.started_at)}</time>
      <em>{run.execution_mode}</em>
      {onRetry && (
        <button
          className="mini-button"
          type="button"
          disabled={retrying}
          onClick={() => onRetry(run)}
        >
          <RefreshCw size={13} /> {retrying ? "恢复中" : "从检查点重试"}
        </button>
      )}
    </div>
  )
}

function Loading() {
  return (
    <div className="loading">
      <RefreshCw size={19} />
      <span>同步本地状态…</span>
    </div>
  )
}
function Empty({ title, text }: { title: string; text: string }) {
  return (
    <div className="empty">
      <Orbit size={25} />
      <b>{title}</b>
      <span>{text}</span>
    </div>
  )
}

export default App
