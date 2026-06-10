# EEGLAB MCP Workflow Recipes

Use these recipes as starting points. Adapt parameters to the study design, acquisition setup, and the user's stated analysis goal.

## Project-Level Research System

Large EEG projects should move through explicit phases:

1. Intake: identify hypothesis, analysis family, data format, project scale, subject/session layout, conditions, and expected outputs.
2. Recording/provenance audit: preserve raw files; inspect sampling rate, data shape, duration, channel montage/reference, event markers, comments/BIDS metadata, and EEGLAB history.
3. QC gate: verify loadability, channel-location coverage, event integrity, missing metadata, plugin prerequisites, and whether data is continuous or epoched.
4. Preprocessing: apply transparent, study-appropriate filtering, line-noise cleanup, rereferencing, bad-channel handling, ICA/ICLabel when justified, and named intermediate saves.
5. Analysis branch: choose ERP, resting-state spectral/connectivity, time-frequency, source localization, or STUDY/group statistics according to the validated design.
6. Reporting: output datasets/figures/tables plus exact parameters, QC risks, rejected data/components, software/plugin limitations, and no clinical claims.
7. Evolution: turn repeated project patterns, failures, and accepted defaults into updated workflow notes/evals after review.

Before phase 4, call `eeglab_project_plan` for large/ambiguous projects or `eeglab_workflow_recommend` for a lighter branch recommendation. Pass any known `research_goal`, `analysis_type`, `project_scale`, `event_types`, `event_semantics`, `srate`, `data_shape`, `has_ica`, `has_channel_locations`, `has_continuous_raw`, and `has_behavioral_log`. Use returned `clarifying_questions`, `default_assumptions`, `blocking_conditions`, `not_recommended`, `qc_gates`, and `adaptive_decision_rules` as the project checklist.

## Inspection

1. `eeglab_init`
2. `eeglab_load_data` with absolute `filepath`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Report channel count, sampling rate, points/trials, duration, data shape, channel-location coverage, reference/montage, event types/counts, event latency range, file path, processing-history availability, and ICA status.

Shortcut name: `quick_qc`. This is the default first workflow for any new dataset and never modifies EEG data.

## Recording and Provenance Audit

EEGLAB analyzes imported EEG recordings; it does not replace acquisition software or lab notebooks. Before processing, audit what the imported file preserved:

1. Source path, set name, file name, and saved state from `eeglab_info`.
2. Sampling rate, points/trials, continuous versus epoched shape, and total data duration.
3. Channel labels, reference/montage, and `channel_location_coverage`; load or repair locations before topography/source work.
4. Event labels/counts, latency range, and `urevent` links; event-locked ERP/time-frequency work needs validated markers.
5. Comments, BIDS/STUDY metadata, and `eeglab_history`; if missing, report the provenance gap explicitly.

Use `eeglab_qc_report` as the concise research audit. It should produce `recording`, `risk_hints`, and `provenance_hints` in `summary`.

## Adaptive Workflow Selection

- User specified a goal: follow it, but check prerequisites and report risks.
- Goal missing, confirmed condition triggers present: recommend ERP/time-frequency feasibility first; ask for conditions, epoch/baseline windows, and channels of interest.
- Goal missing, only boundary/impedance/segment markers present: recommend segment-level QC or resting/task-block planning, not ERP.
- Goal missing, no events and continuous data: recommend resting-state QC/spectral feasibility first.
- Data already epoched: avoid assuming resting-state or ICA suitability until the original continuous data or design is confirmed.
- Missing channel locations: avoid topography/source localization and report that montage metadata must be loaded or repaired.
- Multi-subject or BIDS project: stabilize and document single-subject preprocessing before STUDY/group statistics.

## Event Semantics Audit

Use `eeglab_event_semantics_audit` before ERP or ERSP/ITC when markers are not already documented.

Inputs to provide when known:

- `event_types` and `event_counts` from `eeglab_get_events`
- `event_descriptions` from the user/lab notebook
- `condition_markers` for confirmed task conditions
- `boundary_markers`, `segment_markers`, and `exclude_markers` for non-analysis labels

Policy:

- condition markers can be used for epoching after counts/latencies are checked
- candidate triggers need user confirmation before scientific claims
- boundary, impedance, excluded, and segment markers must not be ERP triggers
- start/end marker data should use `segment_qc` unless a condition map or behavioral log is supplied

## QC Gates

Do not claim a dataset is analysis-ready until these gates are checked:

- Raw input preserved and transformed outputs target a new path.
- Recording metadata reported: source path, data shape, sampling rate, duration, channel count, reference/montage, event labels/counts, history availability.
- Channel-location coverage checked.
- Event labels and latencies checked before ERP/time-frequency analysis.
- Processing history or current session steps recorded.
- Analysis branch matches the study design and data shape.
- Artifact-rejection and ICA decisions have explicit thresholds/rationale.
- Output files and limitations are reported.

## ERP Preprocessing

Typical transparent sequence:

1. Inspect with `eeglab_info` and `eeglab_get_events`
2. Run `eeglab_event_semantics_audit` and confirm condition triggers
3. `eeglab_filter` using study-appropriate cutoffs, often `bandpass` 0.1-40 Hz or 0.5-40 Hz
4. `eeglab_clean_line_noise` at 50 Hz or 60 Hz as appropriate
5. `eeglab_clean_rawdata` for conservative ASR cleanup when requested
6. `eeglab_reref`, usually average reference unless the study specifies otherwise
7. Optional `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_remove_components`
8. `eeglab_epoch` using explicit event types and baseline window
9. `eeglab_erp_analysis`
10. Optional `eeglab_plot_erp` and `eeglab_topoplot`
11. `eeglab_save_data`
12. `eeglab_protocol_export`

Always report recording metadata, event types/counts, epoch window, baseline window, channels, and filtering choices.

Shortcut name: `safe_erp`. Do not enter this workflow if `eeglab_event_semantics_audit` reports no confirmed analysis events.

## Segment QC

Use `segment_qc` when data contains start/end or block markers but no condition-level ERP trigger remains.

Sequence:

1. `eeglab_get_events`
2. `eeglab_event_semantics_audit`
3. `eeglab_qc_report`
4. If marker sidecars exist, parse them non-destructively for exact segment start/end samples, times, and durations.
5. `eeglab_protocol_export`

Report that segment markers are boundaries/task-block annotations, not ERP triggers. Recommend the user provide event codes or behavioral logs before condition-level ERP/ERSP analysis.

## Light ERP Smoke Workflow

Use `eeglab_erp_light_workflow` when the user wants a complete lightweight ERP run and accepts a conservative smoke-test sequence. Pass absolute `data_path` and a new `output_dir`; do not point output at the raw dataset.

Default verification parameters: bandpass 0.5-40 Hz, events `target/standard`, epoch `[-0.2, 0.8]` seconds, baseline `[-200, 0]` ms, channel `Cz`, ERP time window `[250, 450]` ms.

Report the workflow `steps`, `parameters`, `outputs`, `summary`, and `limitations` fields.

## Resting-State Spectral Analysis

1. Inspect/load and verify data shape is appropriate for resting-state analysis
2. `eeglab_filter`, often highpass 0.5 or 1 Hz and lowpass 45/80/100 Hz
3. `eeglab_clean_line_noise`
4. Optional conservative `eeglab_clean_rawdata`
5. `eeglab_reref`
6. `eeglab_spectral` with explicit `freq_range`

Report absolute and relative band-power summaries only as signal analysis results, not diagnoses.

## Time-Frequency Analysis

1. Inspect recording metadata and events
2. Filter and line-noise cleanup
3. Epoch with task-relevant event types
4. `eeglab_timefreq` with explicit `channels`, `freq_range`, `cycles`, and `baseline`
5. Optional `eeglab_plot_timefreq`

Report ERSP/ITC settings and baseline. Avoid over-interpreting single-channel results.

## ICA Cleanup

1. Ensure data is continuous or appropriately prepared for ICA
2. Run `eeglab_plugin_check` when ICLabel/Picard availability matters
3. Filter with ICA-appropriate highpass, commonly 1 Hz
4. Remove or interpolate obvious bad channels only when justified
5. Run `eeglab_run_ica`
6. Run `eeglab_classify_ica`
7. Use `eeglab_flag_components` or `eeglab_remove_components`
8. Save a processed copy, never overwrite the original by default

Report ICA algorithm, PCA components if used, ICLabel thresholds, and removed components.

## STUDY / Group Analysis

Shortcut name: `study_ready_check`.

1. Use `eeglab_project_plan`
2. Use `eeglab_plugin_check` for BIDS/LIMO/SIFT if needed
3. Use `eeglab_import_bids` or `eeglab_study_create`
4. Use `eeglab_study_design`
5. Use `eeglab_study_statistics`
6. Use `eeglab_protocol_export`

Confirm subjects, design variables, variable levels, alpha, correction method, and the single-subject preprocessing/provenance assumptions used before group statistics.

## Source Localization

Prerequisites: ICA must exist, channel locations must be correct, and DIPFIT resources must be available.

1. `eeglab_info` to check ICA status
2. `eeglab_plugin_check` for DIPFIT
3. `eeglab_run_ica` if needed
4. `eeglab_source_settings`
5. `eeglab_source_localization`

Report model/template settings and residual variance. Do not claim anatomical or clinical certainty.

## One-Click Pipeline

Use `eeglab_pipeline` only when the user wants a quick standardized path and accepts defaults. After it runs, call `eeglab_info`, `eeglab_qc_report`, and `eeglab_history`, then summarize recording metadata, steps, output files, and limitations.

## Failure Recovery

If a workflow step fails, read `code`, `error`, `next_step`, and `details.step`. Common recoveries are: initialize EEGLAB, load data first, inspect event labels before epoching, keep baseline inside the epoch window, choose an output path that does not overwrite input, and verify required plugins before ICA/source/STUDY work.

## Protocol Export

Use `eeglab_protocol_export` when a plan or completed workflow needs a durable artifact. Include research goal, analysis type, workflow steps, parameters, QC gates, outputs, limitations, and official reference anchors. Use Markdown for reports/handoffs and JSON when another tool will consume the protocol.

## Self-Evolution

After each substantial project, review what happened:

- Repeated missing metadata: update intake questions and provenance reporting guidance.
- Repeated tool/plugin failures: add a recovery note and, when useful, an eval prompt.
- Repeated parameter choices accepted by the user: document them as project-specific defaults, not universal defaults.
- New analysis pattern: add an eval requiring at least two tool calls and a decision based on earlier output before treating it as supported.
