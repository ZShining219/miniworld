# MiniWorld Agent Working Agreement

## Source of truth

1. Read `goal.md` before changing product behavior.
2. Read `goal/README.md`, the relevant implementation document, and `.ai/last_summary.md` before editing.
3. User intent and `goal.md` override templates, frameworks, upstream instructions, and implementation convenience.
4. If a technical choice conflicts with the three product loops, address privacy, or approval boundaries, change the technical choice.

## Non-negotiable boundaries

- Serve one local user for the Demo.
- Keep job discovery, profile/resume, and work reporting as separate workflows.
- Never send the exact home address or exact home coordinates externally.
- Job discovery must not directly modify the profile or resume.
- Remote models receive only authorized, minimized task material through the provider gateway.
- Job applications, messages, uploads, account authorization, public pushes containing personal data, and other external writes require explicit user confirmation.
- Never commit real personal materials, addresses, API keys, databases, logs, generated resumes, or model transcripts.

## Engineering workflow

- Use the `.ai/` append-only governance pools and claim scope before editing.
- Keep changes aligned with the current phase in `goal/plan.md`.
- Record user-facing decisions in `goal/decisions.md` and implementation facts in `goal/implementation-log.md`.
- Add or update tests for behavior changes and record the commands/results.
- Import upstream code only from a pinned commit, preserve license notices, and do not copy upstream `.git` or agent instruction files.
- Use `codex/` branch names for implementation work.

## Frontend presentation gate

- Before changing any file under `apps/miniworld-shell/**`, `frontend/**`, or any new user interface, read and follow `goal/frontend-presentation-rules.md`.
- The presentation rules are a completion gate, not optional design guidance. A frontend task cannot be marked verified, pushed, or deployed until every applicable automated, visual, responsive, state, and real-device requirement has evidence.
- Mobile UI must use the selected unibest/Wot UI 2 component system; PC UI must use the selected React/Ant Design system. New page-level raw controls or one-off visual systems are prohibited unless the documented exception process has explicit user approval.
- Desktop viewport emulation does not count as physical-phone acceptance. If real-device evidence is missing, report the task as pending visual review.
