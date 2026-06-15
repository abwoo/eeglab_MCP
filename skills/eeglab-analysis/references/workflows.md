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

Before any high-risk tool, call `eeglab_method_preflight` or provide `method_context` directly to the tool. Treat `official_gate_blocked` as a scientific stop. Continue only after missing requirements are resolved or the user gives an explicit override reason.

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
3. `eeglab_method_preflight` for `epoch` and any planned filtering/ICA/ASR branch
4. `eeglab_filter` using study-appropriate cutoffs, often `bandpass` 0.1-40 Hz or 0.5-40 Hz
5. `eeglab_clean_line_noise` at 50 Hz or 60 Hz as appropriate
6. `eeglab_clean_rawdata` for conservative ASR cleanup when requested
7. `eeglab_reref`, usually average reference unless the study specifies otherwise
8. Optional `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_remove_components`
9. `eeglab_epoch` using explicit event types and baseline window
10. `eeglab_erp_analysis`
11. Optional `eeglab_plot_erp` and `eeglab_topoplot`
12. `eeglab_save_data`
13. `eeglab_protocol_export`

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
2. `eeglab_method_preflight` for `derivative_processing`, `line_noise`, and `spectral` as needed
3. `eeglab_filter`, often highpass 0.5 or 1 Hz and lowpass 45/80/100 Hz
4. `eeglab_clean_line_noise` with local 50/60 Hz frequency recorded
4. Optional conservative `eeglab_clean_rawdata`
5. `eeglab_reref`
6. `eeglab_spectral` with explicit `freq_range`

Report absolute and relative band-power summaries only as signal analysis results, not diagnoses. Include artifact policy, channels/ROIs, frequency range, and why the data shape supports resting or block-level spectral analysis.

## Sensor Connectivity

1. Confirm the research question really needs connectivity and whether the interpretation is sensor-level or source-level.
2. Run `eeglab_method_preflight` for `connectivity` with frequency range, method, channels/ROIs, artifact policy, and interpretation limits.
3. Use `eeglab_connectivity` only for supported sensor-level summaries such as coherence or PLV.
4. For SIFT/MVAR/source connectivity, keep the workflow as guidance-only unless SIFT/groupSIFT availability, model order, stationarity, validation, and correction policy are documented.

Report method, frequency range, channel/ROI set, artifact policy, and the limit that sensor-level connectivity is not anatomical connectivity.

## Time-Frequency Analysis

1. Inspect recording metadata and events
2. Filter and line-noise cleanup
3. Epoch with task-relevant event types
4. `eeglab_timefreq` with explicit `channels`, `freq_range`, `cycles`, and `baseline`
5. Optional `eeglab_plot_timefreq`

Report ERSP/ITC settings and baseline. Avoid over-interpreting single-channel results.

## ICA Cleanup

1. Ensure data is continuous or appropriately prepared for ICA
2. Run `eeglab_method_preflight` for `run_ica`
3. Run `eeglab_plugin_check` when ICLabel/Picard availability matters
4. Filter with ICA-appropriate highpass, commonly 1 Hz
5. Remove or interpolate obvious bad channels only when justified
6. Run `eeglab_run_ica`
7. Run `eeglab_method_preflight` for `iclabel` or `remove_components`
8. Run `eeglab_classify_ica`
9. Use `eeglab_flag_components` or `eeglab_remove_components`
10. Save a processed copy, never overwrite the original by default

Report ICA algorithm, PCA components if used, ICLabel thresholds, and removed components.

## STUDY / Group Analysis

Shortcut name: `study_ready_check`.

1. Use `eeglab_project_plan`
2. Use `eeglab_method_preflight` for `bids_metadata` and the staged BIDS/STUDY gate you are about to execute
3. Use `eeglab_plugin_check` for BIDS/LIMO/SIFT if needed
4. Use `eeglab_method_preflight` with `method="bids_import"` before `eeglab_import_bids`, or `method="study_create"` before `eeglab_study_create`
5. Use `eeglab_method_preflight` with `method="study_design"` before `eeglab_study_design`
6. Use `eeglab_method_preflight` with `method="study_statistics"` before `eeglab_study_statistics`
7. Use `eeglab_protocol_export`

Confirm subjects, design variables, variable levels, alpha, correction method, and the single-subject preprocessing/provenance assumptions used before group statistics.

## Import Plugin Guidance

BIOSIG, File-IO, MFF-matlab-io, NWB-io, and BVA-io are official or officially indexed import routes, but plugin-dependent imports need readiness checks before analysis claims.

1. Use `eeglab_project_plan` to record source format, sidecars/header files, event source, channel-location source, and raw preservation.
2. Use `eeglab_plugin_check` for the requested importer.
3. Use `eeglab_method_preflight` for `import_plugins` with source format, plugin availability, event/channel mapping, and raw input preservation.
4. Use `eeglab_protocol_export` if plugin support, sidecars, or mapping assumptions are missing.

Do not treat imported event or channel metadata as validated until importer mapping and event semantics have been reviewed.

## BIDS Export Guidance

BIDS export is indexed and plugin-checkable, but this MCP does not expose a dedicated BIDS export execution tool by default.

1. Use `eeglab_project_plan` to confirm export purpose, derivative status, and metadata completeness.
2. Use `eeglab_plugin_check` for EEG-BIDS export functions.
3. Use `eeglab_method_preflight` for `bids_export` with sidecars, events.tsv columns, events.json/HED/codebook descriptions, derivative output directory, and software/plugin provenance.
4. Use `eeglab_protocol_export` to document export readiness or blockers.

Do not claim BIDS export execution support unless a dedicated export tool, output validation, and eval coverage are added.

## Data Export Guidance

External data export is indexed through official EEGLAB export guidance and plugin pages. The MCP can save EEGLAB `.set` derivatives, but BrainVision, MFF, NWB, and BIDS export paths remain guidance-only unless a dedicated exporter tool is added.

1. Use `eeglab_project_plan` to identify target format, consumer, derivative status, and required metadata.
2. Use `eeglab_plugin_check` for EEG-BIDS, MFF-matlab-io, NWB-io, BVA-io, or the requested exporter.
3. Use `eeglab_method_preflight` for `data_export` with format support, derivative output, export metadata completeness, and software/plugin provenance.
4. Use `eeglab_protocol_export` for export readiness, limitations, and validation gaps.

Do not present external export as executed support when only a planning/report path exists.

## HED Event Annotation Guidance

HEDTools and BIDS events metadata can support event semantics, but HED tags are not automatically condition triggers.

1. Use `eeglab_event_semantics_audit` to classify markers.
2. Use `eeglab_plugin_check` for HEDTools when HED-specific tooling is requested.
3. Use `eeglab_method_preflight` for `hed_event_annotation` with event descriptions, HED schema/version, and a validated condition-code map.
4. Use `eeglab_protocol_export` to report HED/events.json/codebook provenance and remaining ambiguity.

Do not epoch or interpret ERP/ERSP effects from HED labels alone when condition triggers are not validated.

## History Scripting Guidance

EEGLAB history can help recover GUI work into scripts, but copied history is not automatically a reproducible batch protocol.

1. Use `eeglab_history` to inspect available history.
2. Use `eeglab_method_preflight` for `history_scripting` with history availability, script review, explicit parameters, and derivative output policy.
3. Use `eeglab_protocol_export` to document reviewed script steps, parameters, outputs, and limitations.

Do not run a history-derived batch script until paths, defaults, dataset state, and output policy are reviewed.

## Event Script Modification Guidance

Scripted event edits can recode labels, remove markers, shift latencies, or repair event/urevent relationships, but this MCP does not expose a generic event-mutation execution tool by default.

1. Use `eeglab_get_events` and `eeglab_event_semantics_audit` before event edits.
2. Use `eeglab_method_preflight` for `event_script_modification` with recode/deletion/latency rules, latency units, urevent policy, and semantic evidence.
3. Use `eeglab_protocol_export` for a report-only plan or recovery note.

Do not create condition triggers through event scripts without a behavioral log, events.json/HED record, or lab codebook.

## STUDY Precompute And ICA Clustering Guidance

STUDY precompute, visualization, and ICA clustering are indexed official workflows. The current MCP can plan and gate them, but does not expose dedicated precompute or clustering execution tools.

1. Use `eeglab_project_plan` for subject/session structure, design variables, and preprocessing protocol lock.
2. Use `eeglab_method_preflight` for `study_precompute` before interpreting STUDY plots, measures, or statistics.
3. Use `eeglab_method_preflight` for `ica_clustering` before any ICA-cluster interpretation.
4. Use `eeglab_protocol_export` to record measure family, precompute parameters, clustering features, cluster algorithm/count, outlier policy, and review criteria.

Do not treat STUDY plots, precomputed measures, or ICA clusters as publishable group evidence until the staged gates and report fields are complete.

## LIMO Guidance

LIMO is indexed and plugin-checkable, but this MCP does not expose a dedicated LIMO execution workflow by default.

1. Use `eeglab_project_plan` for the statistical design and data hierarchy.
2. Use `eeglab_plugin_check` for LIMO.
3. Use `eeglab_method_preflight` for `limo_statistics` with plugin availability, first/second-level model, design variables, contrasts, alpha, and correction policy.
4. Use `eeglab_protocol_export` for a methods-ready report.

Do not claim LIMO results unless plugin availability, design matrix, contrasts, correction policy, and executable workflow support are all explicit.

## AMICA Guidance

AMICA is indexed and plugin-checkable, but this MCP does not expose a dedicated AMICA execution workflow by default.

1. Use `eeglab_plugin_check` for AMICA.
2. Use `eeglab_method_preflight` for `amica_ica` with continuous-data suitability, rank/PCA/reference review, compute strategy, and derivative output.
3. Use `eeglab_protocol_export` to document algorithm choice and why AMICA is required over the supported runica/Picard path.

Do not run AMICA through generic ICA assumptions unless an AMICA-specific workflow and eval coverage are added.

## SIFT Guidance

SIFT/groupSIFT are indexed and plugin-checkable, but source/MVAR connectivity remains guidance-only by default.

1. Use `eeglab_project_plan` for connectivity goals and source/sensor interpretation.
2. Use `eeglab_plugin_check` for SIFT and groupSIFT.
3. Use `eeglab_method_preflight` for `sift_connectivity` with model order, stationarity, validation, source/model assumptions, and correction policy.
4. Use `eeglab_protocol_export` to document the guidance-only plan and blockers.

Do not run or claim SIFT connectivity support through this MCP unless a dedicated execution workflow and eval coverage are added.

## NSGportal Guidance

NSGportal is indexed and plugin-checkable, but remote/HPC execution is outside the local-first MCP surface by default.

1. Use `eeglab_plugin_check` for NSGportal.
2. Use `eeglab_method_preflight` for `nsg_remote` with user approval, credential policy, data-upload policy, job parameters, upload manifest, and download/recovery plan.
3. Use `eeglab_protocol_export` for the remote-job provenance plan.

Do not execute or claim NSG remote compute support unless a dedicated secure integration is added.

## Source Localization

Prerequisites: ICA must exist, channel locations must be correct, and DIPFIT resources must be available.

1. `eeglab_info` to check ICA status
2. `eeglab_method_preflight` for `source`
3. `eeglab_plugin_check` for DIPFIT
4. `eeglab_run_ica` if needed
5. `eeglab_source_settings`
6. `eeglab_source_localization`

Report model/template settings and residual variance. Do not claim anatomical or clinical certainty.

## One-Click Pipeline

Use `eeglab_pipeline` only when the user wants a quick standardized path and accepts defaults. After it runs, call `eeglab_info`, `eeglab_qc_report`, and `eeglab_history`, then summarize recording metadata, steps, output files, and limitations.

## Failure Recovery

If a workflow step fails, read `code`, `error`, `next_step`, and `details.step`. Common recoveries are: initialize EEGLAB, load data first, inspect event labels before epoching, keep baseline inside the epoch window, choose an output path that does not overwrite input, and verify required plugins before ICA/source/STUDY work. If `code=official_gate_blocked`, do not retry blindly; resolve `missing_requirements` or obtain explicit user override.

## Report-Only Recovery

When the scientifically correct outcome is to stop execution, produce a report rather than forcing a workflow:

1. Summarize the requested analysis and available facts.
2. Include official gate status, missing requirements, source claim IDs, plugin matrix status, and support_level.
3. List safe next steps, such as collecting events.json/HED/codebook, loading channel locations, installing plugins, or locating continuous raw data.
4. Use `eeglab_protocol_export` to preserve the recovery decision.

## Protocol Export

Use `eeglab_protocol_export` when a plan or completed workflow needs a durable artifact. Include research goal, analysis type, workflow steps, parameters, QC gates, outputs, limitations, upstream `gate_results`, `source_claim_ids`, `report_fields`, and any override fields. Use Markdown for reports/handoffs and JSON when another tool will consume the protocol.

## Self-Evolution

After each substantial project, review what happened:

- Repeated missing metadata: update intake questions and provenance reporting guidance.
- Repeated tool/plugin failures: add a recovery note and, when useful, an eval prompt.
- Repeated parameter choices accepted by the user: document them as project-specific defaults, not universal defaults.
- New analysis pattern: add an eval requiring at least two tool calls and a decision based on earlier output before treating it as supported.
