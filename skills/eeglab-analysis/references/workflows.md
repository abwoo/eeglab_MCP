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

Before phase 4, call `eeglab_workflow_recommend` with any known `research_goal`, `analysis_type`, `project_scale`, `event_types`, `srate`, `data_shape`, `has_ica`, and `has_channel_locations`. Use its `clarifying_questions`, `default_assumptions`, `qc_gates`, and `adaptive_decision_rules` as the project checklist.

## Inspection

1. `eeglab_init`
2. `eeglab_load_data` with absolute `filepath`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Report channel count, sampling rate, points/trials, duration, data shape, channel-location coverage, reference/montage, event types/counts, event latency range, file path, processing-history availability, and ICA status.

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
- Goal missing, events present: recommend ERP/time-frequency feasibility first; ask for conditions, epoch/baseline windows, and channels of interest.
- Goal missing, no events and continuous data: recommend resting-state QC/spectral feasibility first.
- Data already epoched: avoid assuming resting-state or ICA suitability until the original continuous data or design is confirmed.
- Missing channel locations: avoid topography/source localization and report that montage metadata must be loaded or repaired.
- Multi-subject or BIDS project: stabilize and document single-subject preprocessing before STUDY/group statistics.

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
2. `eeglab_filter` using study-appropriate cutoffs, often `bandpass` 0.1-40 Hz or 0.5-40 Hz
3. `eeglab_clean_line_noise` at 50 Hz or 60 Hz as appropriate
4. `eeglab_clean_rawdata` for conservative ASR cleanup when requested
5. `eeglab_reref`, usually average reference unless the study specifies otherwise
6. Optional `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_remove_components`
7. `eeglab_epoch` using explicit event types and baseline window
8. `eeglab_erp_analysis`
9. Optional `eeglab_plot_erp` and `eeglab_topoplot`
10. `eeglab_save_data`

Always report recording metadata, event types/counts, epoch window, baseline window, channels, and filtering choices.

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
2. Filter with ICA-appropriate highpass, commonly 1 Hz
3. Remove or interpolate obvious bad channels only when justified
4. Run `eeglab_run_ica`
5. Run `eeglab_classify_ica`
6. Use `eeglab_flag_components` or `eeglab_remove_components`
7. Save a processed copy, never overwrite the original by default

Report ICA algorithm, PCA components if used, ICLabel thresholds, and removed components.

## STUDY / Group Analysis

1. Use `eeglab_import_bids` or `eeglab_study_create`
2. Use `eeglab_study_design`
3. Use `eeglab_study_statistics`

Confirm subjects, design variables, variable levels, alpha, correction method, and the single-subject preprocessing/provenance assumptions used before group statistics.

## Source Localization

Prerequisites: ICA must exist, channel locations must be correct, and DIPFIT resources must be available.

1. `eeglab_info` to check ICA status
2. `eeglab_run_ica` if needed
3. `eeglab_source_settings`
4. `eeglab_source_localization`

Report model/template settings and residual variance. Do not claim anatomical or clinical certainty.

## One-Click Pipeline

Use `eeglab_pipeline` only when the user wants a quick standardized path and accepts defaults. After it runs, call `eeglab_info`, `eeglab_qc_report`, and `eeglab_history`, then summarize recording metadata, steps, output files, and limitations.

## Failure Recovery

If a workflow step fails, read `code`, `error`, `next_step`, and `details.step`. Common recoveries are: initialize EEGLAB, load data first, inspect event labels before epoching, keep baseline inside the epoch window, choose an output path that does not overwrite input, and verify required plugins before ICA/source/STUDY work.

## Self-Evolution

After each substantial project, review what happened:

- Repeated missing metadata: update intake questions and provenance reporting guidance.
- Repeated tool/plugin failures: add a recovery note and, when useful, an eval prompt.
- Repeated parameter choices accepted by the user: document them as project-specific defaults, not universal defaults.
- New analysis pattern: add an eval requiring at least two tool calls and a decision based on earlier output before treating it as supported.
