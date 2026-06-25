# EEGLAB Session Order

## Start Here

1. Read the official docs first.
2. Load the `eeglab-analysis` Skill.
3. Read `skills/eeglab-analysis/references/`.
4. Plan with `eeglab_project_plan` or `eeglab_workflow_recommend`.
5. Run the read-only intake: `eeglab_init` -> `eeglab_load_data` -> `eeglab_qc_report` -> `eeglab_info` -> `eeglab_get_events` -> `eeglab_history`.
6. Audit event semantics before any event-locked branch.
7. Run `eeglab_plugin_check` when plugins are needed.
8. Run `eeglab_method_preflight` before every high-risk step.
9. Follow `branch-workflow-matrix.md` exactly.
10. Use `figure-atlas.md` for required, conditional, and guidance-only figure families.
11. Save only derivative outputs.
12. Export the protocol.
13. Generate the final report.

## Rules

- Use only real loaded EEG data and real project metadata.
- Never fabricate provenance, events, figures, outputs, or gate results.
- Never overwrite raw EEG files.
- Keep machine-generated text in English.

## Branch Guide

- ERP: event semantics -> preflight -> filter/line-noise -> optional ASR -> rereference -> optional ICA/ICLabel -> epoch + baseline -> ERP -> figures -> save -> protocol -> report
- Resting-state spectral/connectivity: preflight -> filter/line-noise -> optional ASR -> rereference -> spectral -> optional connectivity -> figures -> save -> protocol -> report
- Connectivity review: preflight -> spectral sanity check -> connectivity matrix/network -> optional topomap -> save -> protocol -> report
- Time-frequency: event semantics -> preflight -> filter/line-noise -> epoch + baseline -> timefreq -> figures -> save -> protocol -> report
- Source localization: channel locations -> plugin check -> preflight -> optional ICA -> source settings -> source localization -> figures -> save -> protocol -> report
- STUDY/group analysis: project plan -> plugin check -> single-subject lock -> staged STUDY preflight -> create -> design -> statistics -> optional precompute/clustering -> figures -> save -> protocol -> report

See `canonical-session-checklist.md` for the full strict version.
