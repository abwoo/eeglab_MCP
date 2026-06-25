# Canonical Session Checklist / 规范会话清单

This page is the strict one-page order for EEG/EEGLAB work.
本页是 EEG/EEGLAB 工作的严格一页式顺序表。

## Authority / 权威

- EN: Read the 10 official docs first: `official-gate-policy.md`, `official-method-map.md`, `official-plugin-map.md`, `official-report-field-matrix.md`, `official-risk-matrix.md`, `official-support-matrix.md`, `official-tool-support-matrix.md`, `official-topic-index.md`, `research-standard.md`, and `user-workflows.md`.
- ZH: 先读 10 个官方文档：`official-gate-policy.md`、`official-method-map.md`、`official-plugin-map.md`、`official-report-field-matrix.md`、`official-risk-matrix.md`、`official-support-matrix.md`、`official-tool-support-matrix.md`、`official-topic-index.md`、`research-standard.md`、`user-workflows.md`。
- EN: If `docs/` and `references/` disagree, `docs/` wins and `references/` must be updated.
- ZH: 如果 `docs/` 和 `references/` 冲突，以 `docs/` 为准，并回改 `references/`。
- EN: Use only real loaded EEG data and real project metadata.
- ZH: 只使用真实加载的 EEG 数据和真实项目元数据。
- EN: Save derivative outputs only; never overwrite raw EEG files.
- ZH: 只保存 derivative，不覆盖 raw EEG 文件。
- EN: Keep all machine-generated text in English.
- ZH: 所有机器生成文本保持英文。

## Canonical Session Order / 规范会话顺序

1. Load the `eeglab-analysis` Skill.
2. Read `docs/` first, then `skills/eeglab-analysis/references/`.
3. Plan the project with `eeglab_project_plan` or `eeglab_workflow_recommend`.
4. Run the read-only intake: `eeglab_init` -> `eeglab_load_data` -> `eeglab_qc_report` -> `eeglab_info` -> `eeglab_get_events` -> `eeglab_history`.
5. Audit event semantics with `eeglab_event_semantics_audit` before any event-locked branch.
6. Run `eeglab_plugin_check` when the branch depends on plugins.
7. Run `eeglab_method_preflight` before every high-risk step.
8. Follow `branch-workflow-matrix.md` exactly for required, conditional, and forbidden steps.
9. Use `figure-atlas.md` for required, conditional, and guidance-only figure families.
10. Save only derivative outputs.
11. Export the protocol with `eeglab_protocol_export`.
12. Generate the final report with `eeglab_generate_report` or `scripts/generate_eeg_report.py`.

## Branch Orders / 分支顺序

| Branch | Required order | Forbidden shortcuts |
|---|---|---|
| ERP | event semantics audit -> preflight -> filter/line-noise -> optional ASR -> rereference -> optional ICA/ICLabel -> epoch + baseline -> ERP analysis -> figures -> save derivative -> protocol -> report | No boundary/impedance/segment markers as triggers; no raw overwrite |
| Resting-state spectral/connectivity | preflight -> filter/line-noise -> optional ASR -> rereference -> spectral -> optional connectivity -> figures -> save derivative -> protocol -> report | No default epoching; no anatomical connectivity claims from sensor summaries |
| Connectivity review | preflight -> spectral sanity check -> connectivity matrix/network -> optional topomap -> save derivative -> protocol -> report | No sensor-source anatomical claims without source modeling |
| Time-frequency | event semantics audit -> preflight -> filter/line-noise -> epoch + baseline -> timefreq -> figures -> save derivative -> protocol -> report | No skipping baseline; no continuous-data ERSP/ITC claims |
| Source localization | channel-location review/repair -> plugin check -> preflight -> optional ICA -> source settings -> source localization -> figures -> save derivative -> protocol -> report | No source claims without channel locations; no anatomical certainty claims |
| STUDY/group analysis | project plan -> plugin check -> single-subject lock -> staged STUDY preflight -> study create -> study design -> study statistics -> optional precompute/clustering -> figures -> save derivative -> protocol -> report | No direct group statistics before single-subject lock; no unsupported precompute/clustering claims |

## Final Report / 最终报告

The report must include:

- recording/acquisition metadata
- events/design metadata
- preprocessing parameters
- analysis parameters
- outputs and limits
- `gate_results`, `source_claim_ids`, `branch_workflow`, `branch_completeness`, `figure_atlas`
- tool coverage, reference coverage, official-document coverage
- figure paths and output paths
- limitations and any override reason

如果缺少任何必要字段，必须记录缺口，不能虚构。
