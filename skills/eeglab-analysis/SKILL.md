---
name: eeglab-analysis
description: Standardized EEG/EEGLAB research workflows using the local eeglab MCP server. Use when Codex or another IDE agent needs to inspect recording/acquisition metadata, preserve EEG provenance, preprocess, clean, epoch, run ICA/ICLabel, analyze ERP/spectral/time-frequency/connectivity results, create figures, or guide users through reproducible EEG processing with the eeglab_* MCP tools.
---

# EEGLAB Analysis

Use the local `eeglab` MCP server as the execution surface for EEG research work. Prefer conservative, inspect-first workflows: initialize EEGLAB, load data, run QC, inspect recording/channel/event/provenance metadata, choose the smallest scientifically appropriate processing sequence, then report parameters and limitations without clinical claims.

This skill can be used with only the `eeglab` MCP server, or with both `eeglab` and a separate matlab MCP. The routing rule is eeglab first for EEG/EEGLAB research work; use matlab MCP only for generic MATLAB scripts, custom matrix/statistical code, or non-EEGLAB toolboxes.

## Workflow

1. Confirm the `eeglab` MCP server is available and exposes `eeglab_*` tools.
2. Start with `eeglab_init`, then `eeglab_load_data`, `eeglab_qc_report`, `eeglab_info`, `eeglab_get_events`, and `eeglab_history`.
3. Call `eeglab_workflow_recommend` before destructive processing. If the user gave a goal, pass `research_goal` and `analysis_type`; if not, pass available data facts and use the returned `clarifying_questions`, `default_assumptions`, and `qc_gates`.
4. Choose a workflow from `references/workflows.md`: inspection, ERP, resting-state spectral, time-frequency, ICA cleanup, visualization, STUDY, or source localization.
5. Before destructive processing, ask for or choose an output path and preserve the original dataset.
6. Report recording/provenance facts first: source path, sampling rate, duration, data shape, channel count, channel-location coverage, reference/montage, event labels/counts, event latency range, and processing history availability.
7. Report every processing parameter used: filter cutoffs, line-noise frequency, ASR threshold, rereference, ICA algorithm, epoch/baseline windows, channel list, frequency range, rejected components/epochs, and output files.
8. State uncertainty and prerequisites clearly. Do not make diagnosis, treatment, or clinical interpretation claims.

## Project System

For large research projects, treat the workflow as a staged system rather than a single command chain:

1. Project intake: clarify hypothesis, analysis family, subject/session structure, data format, and expected outputs.
2. Recording/provenance audit: preserve raw files and inspect sampling rate, data shape, duration, montage, reference, events, BIDS/comments, and history.
3. QC gate before processing: verify loadability, channel-location coverage, event integrity, plugin prerequisites, and missing metadata.
4. Single-subject preprocessing: apply transparent filtering, line-noise cleanup, rereferencing, bad-channel handling, ICA/ICLabel when justified, and save named intermediates.
5. Analysis branch: choose ERP, resting-state spectral/connectivity, time-frequency, source, or STUDY based on the validated design.
6. Output/reporting: save datasets, figures, tables, parameters, QC risks, and limitations.
7. Project evolution: convert repeated failures, missing metadata, or stable parameter decisions into updated workflow notes/evals after review.

## Adaptive Defaults

- If the user states a research goal, follow it and report any methodological risks.
- If the goal is missing, ask for the primary goal, project scale, event labels/conditions, montage/reference, output requirements, and whether group analysis is needed.
- If the user cannot answer yet, use a conservative default plan from the data: event-marked data starts with ERP/time-frequency feasibility; no-event continuous data starts with resting/QC/spectral feasibility; epoched data should not be assumed suitable for resting-state or ICA until confirmed.
- If channel locations are incomplete, avoid topography/source localization until montage metadata is repaired.
- If event labels are missing or sparse, avoid event-locked claims and recommend event audit before epoching.
- If a plugin-dependent step fails, preserve the current state, report the prerequisite, and continue with the highest-valid lower-risk workflow.

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
