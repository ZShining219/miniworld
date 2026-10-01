import {
  Alert,
  App as AntApp,
  Button,
  Popconfirm,
  Space,
  Typography,
} from "antd"
import { FileDown, Send } from "lucide-react"
import { useState } from "react"
import { api } from "../api"
import type { InterviewHandoffResult } from "../types"

type PendingAction = "export" | "push" | null

export function InterviewHandoffActions({
  jobId,
  roleId,
  level,
}: {
  jobId: string
  roleId?: string | null
  level?: string | null
}) {
  const { message } = AntApp.useApp()
  const [pending, setPending] = useState<PendingAction>(null)
  const [result, setResult] = useState<InterviewHandoffResult | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handoff(push: boolean) {
    setPending(push ? "push" : "export")
    setError(null)
    try {
      const next = await api.interviewHandoff(jobId, {
        push,
        role_id: roleId ?? undefined,
        level: level ?? undefined,
      })
      setResult(next)
      if (next.pushed) {
        message.success("已推送到面试项目 pending 语料，等待对方审核")
      } else if (push) {
        message.warning("推送未成功，交接文件已导出到本机")
      } else {
        message.success("交接文件已导出到本机")
      }
    } catch (reason) {
      const detail = reason instanceof Error ? reason.message : "交接失败"
      setError(detail)
      message.error(detail)
    } finally {
      setPending(null)
    }
  }

  return (
    <div className="interview-handoff">
      <Space wrap>
        <Button
          icon={<FileDown size={14} />}
          loading={pending === "export"}
          onClick={() => void handoff(false)}
        >
          导出交接文件
        </Button>
        <Popconfirm
          title="推送到面试项目？"
          description="会向本机面试项目写入一条 pending 语料，仍需在对方侧审核后才生效。"
          okText="推送"
          cancelText="取消"
          onConfirm={() => void handoff(true)}
        >
          <Button
            type="primary"
            icon={<Send size={14} />}
            loading={pending === "push"}
          >
            去练面试
          </Button>
        </Popconfirm>
      </Space>
      {result && (
        <Alert
          type={result.pushed ? "success" : "info"}
          showIcon
          style={{ marginTop: 12 }}
          message={
            result.pushed
              ? `已通过 ${result.push_channel} 推送为 pending 语料`
              : `已导出交接文件（${result.push_channel === "none" ? "未推送" : (result.detail ?? "推送失败")}）`
          }
          description={
            <Typography.Text
              copyable={{ text: result.file }}
              style={{ fontSize: 12 }}
            >
              {result.file}
            </Typography.Text>
          }
        />
      )}
      {result && (
        <Typography.Paragraph
          type="secondary"
          style={{ fontSize: 12, marginTop: 8, marginBottom: 0 }}
        >
          面试角色：{result.role_id ?? "未判定"} · 级别：
          {result.level ?? "未判定"} · 记录 ID：{result.document_external_id}
          {result.detail ? ` · ${result.detail}` : ""}
        </Typography.Paragraph>
      )}
      {error && (
        <Alert
          type="error"
          showIcon
          style={{ marginTop: 12 }}
          message={error}
        />
      )}
      <Typography.Paragraph
        type="secondary"
        style={{ fontSize: 12, marginTop: 8 }}
      >
        交接只包含公开岗位信息；面试项目收到后仍为待审核状态。
      </Typography.Paragraph>
    </div>
  )
}
