---
name: eeglab-analysis
description: Standardized EEG/EEGLAB research workflows using the local eeglab MCP server. Use when Codex or another IDE agent needs to inspect recording/acquisition metadata, preserve EEG provenance, preprocess, clean, epoch, run ICA/ICLabel, analyze ERP/spectral/time-frequency/connectivity results, create figures, or guide users through reproducible EEG processing with the eeglab_* MCP tools.
---

# EEGLAB Analysis

Use the local `eeglab` MCP server as the execution surface for research-grade EEG work. The MCP executes EEGLAB/MATLAB operations; this skill is the method guardrail: research-goal intake, event semantics, QC gates, plugin prerequisites, parameter provenance, risk limits, and reproducible reporting.

This skill can be used with only the `eeglab` MCP server, or with both `eeglab` and a separate matlab MCP. The routing rule is eeglab first for EEG/EEGLAB research work; use matlab MCP only for generic MATLAB scripts, custom matrix/statistical code, or non-EEGLAB toolboxes. The two MCP servers are workspace-isolated; cross-server work must use explicit file handoff.

Official anchors for this skill are EEGLAB/SCCN sources: the EEGLAB repository, official EEGLAB function/tutorial docs, clean_rawdata, ICLabel, DIPFIT, EEGLAB BIDS/STUDY guidance, and EEGLAB Course materials. Do not treat unofficial blogs as normative defaults.

## Workflow

1. Confirm the `eeglab` MCP server is available and exposes `eeglab_*` tools.
2. Start with `eeglab_init`, then `eeglab_load_data`, `eeglab_qc_report`, `eeglab_info`, `eeglab_get_events`, and `eeglab_history`.
3. Call `eeglab_project_plan` or `eeglab_workflow_recommend` before destructive processing. If the user gave a goal, pass `research_goal` and `analysis_type`; if not, pass available data facts and use the returned `clarifying_questions`, `default_assumptions`, `blocking_conditions`, `not_recommended`, and `qc_gates`.
4. Choose a workflow from `references/workflows.md`: inspection, ERP, resting-state spectral, time-frequency, ICA cleanup, visualization, STUDY, or source localization.
5. Before destructive processing, ask for or choose an output path and preserve the original dataset.
6. Report recording/provenance facts first: source path, sampling rate, duration, data shape, channel count, channel-location coverage, reference/montage, event labels/counts, event latency range, and processing history availability.
7. Report every processing parameter used: filter cutoffs, line-noise frequency, ASR threshold, rereference, ICA algorithm, epoch/baseline windows, channel list, frequency range, rejected components/epochs, and output files.
8. State uncertainty and prerequisites clearly. Do not make diagnosis, treatment, or clinical interpretation claims.

## Research Method Guardrails

Start by asking or inferring:

- research question/hypothesis and intended inference level
- experiment design, conditions, event-code map, behavioral logs, and segment/block markers
- subject/session structure and whether the project is single-subject, multi-subject, BIDS/STUDY, or exploratory QC
- recording facts: sampling rate, duration, cap montage, reference, channel locations, acquisition filters, data format, and continuous vs epoched state
- expected outputs: cleaned dataset, ERP tables, spectra, ERSP/ITC, connectivity, source, figures, protocol, or group statistics

If the user cannot provide the goal, use a data-driven conservative plan and say the assumptions explicitly. Do not silently promote event presence into ERP: markers may be boundaries, impedance annotations, segment start/end labels, or excluded events.

## Project System

For large research projects, treat the workflow as a staged system rather than a single command chain:

1. Project intake: clarify hypothesis, analysis family, subject/session structure, data format, and expected outputs.
2. Recording/provenance audit: preserve raw files and inspect sampling rate, data shape, duration, montage, reference, events, BIDS/comments, and history.
3. QC gate before processing: verify loadability, channel-location coverage, event integrity, plugin prerequisites, and missing metadata.
4. Single-subject preprocessing: apply transparent filtering, line-noise cleanup, rereferencing, bad-channel handling, ICA/ICLabel when justified, and save named intermediates.
5. Analysis branch: choose ERP, resting-state spectral/connectivity, time-frequency, source, or STUDY based on the validated design.
6. Output/reporting: save datasets, figures, tables, parameters, QC risks, and limitations.
7. Project evolution: convert repeated failures, missing metadata, or stable parameter decisions into updated workflow notes/evals after review.

## Professional Policies

Recording/provenance audit: preserve raw files, record absolute input/output paths, inspect `EEG` dimensions, sampling rate, comments/BIDS metadata, channel-location coverage, event/urevent links, and `EEG.history`.

Event semantics and experimental design: use `eeglab_event_semantics_audit` when marker meanings are unclear. Classify labels as condition/trigger, boundary, impedance/QC annotation, segment marker, excluded marker, or candidate trigger. Do not epoch around boundaries, impedance, excluded markers, or segment-only start/end labels.

Preprocessing decision tree: choose the smallest justified sequence. Filtering, resampling, rereferencing, clean_rawdata/ASR, ICA, component removal, and epoch rejection all require recorded parameters and a separate derivative output.

ICA/ICLabel review policy: verify continuous-data suitability, rank/reference assumptions, bad-channel handling, and ICLabel availability. Use ICLabel as decision support; report thresholds and never auto-remove components without rationale.

ERP/ERSP/ITC parameter policy: ERP/time-frequency requires confirmed condition triggers, epoch and baseline windows, channel/ROI plan, frequency/cycle settings for ERSP/ITC, and event counts after rejection.

Resting-state spectral/connectivity policy: require continuous-data suitability, recording/block context, artifact policy, frequency range, and connectivity interpretation limits. Avoid resting-state claims from epoched-only data unless the design explicitly supports it.

BIDS/STUDY/group-analysis policy: stabilize single-subject preprocessing before group statistics. Record subject/session layout, design variables, alpha, correction method, and BIDS/STUDY metadata assumptions.

Source localization prerequisites: require channel locations, ICA or another justified model, DIPFIT resources, template/head model assumptions, and residual variance reporting. Do not claim anatomical certainty.

Reporting and reproducibility checklist: every report needs input/output paths, sampling rate, duration, channel count, montage/location coverage, reference, event labels/counts/semantics, filter cutoffs, rereference, artifact/ICA choices, epoch/baseline/frequency windows, plugin status, generated files, failures/recovery, and limitations.

## Adaptive Defaults

- If the user states a research goal, follow it and report any methodological risks.
- If the goal is missing, ask for the primary goal, project scale, event labels/conditions, montage/reference, output requirements, and whether group analysis is needed.
- If the user cannot answer yet, use a conservative default plan from the data: event-marked data starts with ERP/time-frequency feasibility; no-event continuous data starts with resting/QC/spectral feasibility; epoched data should not be assumed suitable for resting-state or ICA until confirmed.
- If channel locations are incomplete, avoid topography/source localization until montage metadata is repaired.
- If event labels are missing or sparse, avoid event-locked claims and recommend event audit before epoching.
- If a plugin-dependent step fails, preserve the current state, report the prerequisite, and continue with the highest-valid lower-risk workflow.

## User Shortcut Modes

- `quick_qc`: load, QC, events, and history only; no data modification.
- `safe_erp`: ERP branch only after `eeglab_event_semantics_audit` confirms condition triggers.
- `segment_qc`: for datasets with start/end markers but no task-condition triggers; report segment durations and avoid ERP claims.
- `study_ready_check`: multi-subject/BIDS prerequisite check before STUDY/group statistics.
- `plugin_doctor`: run `eeglab_plugin_check` before ASR, ICLabel, DIPFIT, BIDS/STUDY, LIMO, or SIFT-dependent work.

## Tool Use Rules

- Use absolute paths for EEG files and output artifacts.
- When both `eeglab` and matlab MCP are available, route EEG data loading, QC, event audit, ICA, ERP, time-frequency, STUDY, source localization, and EEGLAB figures to `eeglab_*` tools first.
- Use matlab MCP for general MATLAB computation, custom `.m` scripts, external toolbox calls, or follow-up calculations that are outside the EEGLAB MCP tool surface.
- Assume workspace isolation between the two MCP servers: an `EEG` variable loaded by `eeglab` is not visible to matlab MCP unless it is saved and reloaded explicitly.
- Use file handoff for cross-MCP work. Save `.set/.fdt`, `.mat`, `.csv`, `.png`, or report files from `eeglab`, then give matlab MCP the exact output path.
- Do not let `eeglab` and matlab MCP write to the same output file or scratch directory at the same time.
- Do not run ICA, source localization, or one-click pipelines casually; they can be slow and plugin-dependent.
- If a tool returns `status: error`, read `code`, `error`, and `next_step`, then recover or explain the prerequisite.
- Prefer explicit step-by-step tools over `eeglab_pipeline` when the user needs transparency or reproducibility.
- Prefer `eeglab_qc_report` for first-pass quality checks and `eeglab_workflow_recommend` before destructive preprocessing.
- Prefer `eeglab_project_plan` for large or ambiguous projects; use `eeglab_protocol_export` when the user needs a protocol or handoff artifact.
- Use `eeglab_event_semantics_audit` before ERP/time-frequency work when event labels are ambiguous, sparse, or include boundaries/impedance/segment markers.
- Use `eeglab_plugin_check` before plugin-dependent workflows: clean_rawdata, ICLabel, DIPFIT, BIDS/STUDY, LIMO, and SIFT.
- Treat EEG recording/acquisition metadata as evidence, not decoration: if comments, channel locations, event labels, reference, or processing history are missing, report the gap.
- Use `qc_gates` from `eeglab_workflow_recommend` as a checklist before claiming a dataset is ready for processing or analysis.
- Use `eeglab_erp_light_workflow` for a smoke-tested ERP chain when the user wants a complete lightweight ERP run into a new output directory.
- Use `eeglab_pipeline` only when the user wants a quick standardized run and accepts its defaults.

## Self-Evolution Protocol

- At the end of each project or failed workflow, record missing metadata, failed tools/plugins, parameter decisions, and successful recovery paths.
- Do not silently change scientific defaults. Update skill references or eval prompts only when a repeated pattern is observed or the user explicitly approves a project-specific protocol.
- When adding a new supported research pattern, add or update an eval prompt that requires at least two MCP tool calls and a decision based on previous output.
- Keep the MCP and this skill synchronized: if a tool output adds a new QC field or decision rule, update the skill/reporting guidance; if the skill requires a new invariant, add a verifier or eval.

## Reporting Templates

Recording record: input path, set name/file name, sampling rate, data shape, points/trials, duration, channel count, channel-location coverage, reference/montage, event labels/counts, event latency range, comments/BIDS metadata if available, and processing-history availability.

Parameter record: output path, filter cutoffs, line-noise choice, ASR threshold, rereference, ICA algorithm/PCA rank, ICLabel thresholds, epoch window, baseline window, channels, frequency range, rejected data/components, and software/plugin limitations.

Result report: summarize recording metadata, dataset dimensions, processing steps, exact parameters, generated files, QC/provenance risks, failures/recovery, and analysis limits. Do not make clinical or diagnostic claims.

## References

- For workflow recipes and tool sequences, read `references/workflows.md`.
- For MCP/client setup and verification, read `references/setup.md`.
- For tool groups and common parameters, read `references/tools.md`.
- For official EEGLAB reference anchors, read MCP resource `eeglab://official/references.md` or project file `docs/research-standard.md`.
