# EEGLAB MCP Workflow Recipes

Use these recipes as starting points. The canonical branch order lives in
`branch-workflow-matrix.md`; this file explains how to enter that matrix and
how to separate universal, event-locked, continuous, and group-analysis work.

## Canonical Session Order

Every research session should follow this order:

1. Load the `eeglab-analysis` Skill.
2. Read `docs/` first, then the skill-side `references/`.
3. Plan with `eeglab_project_plan` or `eeglab_workflow_recommend`.
4. Run the read-only intake: `eeglab_init` -> `eeglab_load_data` -> `eeglab_qc_report` -> `eeglab_info` -> `eeglab_get_events` -> `eeglab_history`.
5. Run `eeglab_event_semantics_audit` before any event-locked branch.
6. Run `eeglab_plugin_check` when the branch depends on plugins.
7. Run `eeglab_method_preflight` before each high-risk tool.
8. Follow `branch-workflow-matrix.md` for required, conditional, and forbidden steps.
9. Use `figure-atlas.md` for required, conditional, and guidance-only figure families.
10. Open the default browsable companion in `scripts/advanced_figures/` so the branch figure family stays visible during review.
11. Save only derivative outputs.
12. Export the protocol.
13. Generate the final report.

For a short entry page, read `../docs/homepage-session-order.md` first, then use
`canonical-session-checklist.md` for the full strict version.

## Data Integrity Rules

- Use real loaded EEG data and real project metadata only.
- Do not fabricate provenance, figures, outputs, gate results, or event semantics.
- Keep machine-generated artifacts in English.

## Project-Level Research System

Large EEG projects should move through explicit phases:

1. Intake: identify hypothesis, analysis family, data format, project scale, subject/session layout, conditions, and expected outputs.
2. Recording/provenance audit: preserve raw files; inspect sampling rate, data shape, duration, channel montage/reference, event markers, comments/BIDS metadata, and EEGLAB history.
3. QC gate: verify loadability, channel-location coverage, event integrity, missing metadata, plugin prerequisites, and whether data is continuous or epoched.
4. Branch matrix selection: choose the canonical branch workflow matrix.
5. Preprocessing and analysis: follow the branch-specific required, conditional, and forbidden steps exactly.
6. Reporting: output datasets/figures/tables plus exact parameters, QC risks, rejected data/components, software/plugin limitations, tool/reference coverage, and no clinical claims.
7. Evolution: turn repeated project patterns, failures, and accepted defaults into updated workflow notes/evals after review.

Before phase 4, call `eeglab_project_plan` for large or ambiguous projects or `eeglab_workflow_recommend` for a lighter branch recommendation. Pass any known `research_goal`, `analysis_type`, `project_scale`, `event_types`, `event_semantics`, `srate`, `data_shape`, `has_ica`, `has_channel_locations`, `has_continuous_raw`, and `has_behavioral_log`. Use returned `clarifying_questions`, `default_assumptions`, `blocking_conditions`, `not_recommended`, `qc_gates`, and `adaptive_decision_rules` as the project checklist.

Before any high-risk tool, call `eeglab_method_preflight` or provide `method_context` directly to the tool. Treat `official_gate_blocked` as a scientific stop. Continue only after missing requirements are resolved or the user gives an explicit override reason.

## Universal Preamble

These steps appear before every branch in the canonical matrix:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`
7. `eeglab_project_plan` or `eeglab_workflow_recommend`
8. `eeglab_plugin_check` when the branch depends on plugins
9. `eeglab_method_preflight` before any high-risk step

## Event-Locked Steps

Use `eeglab_event_semantics_audit` before epoching or any event-locked claim.
Only confirmed condition triggers may drive ERP or ERSP/ITC analysis.

## Continuous-Data-Only Steps

Resting-state spectral/connectivity analysis stays continuous unless the study
design explicitly justifies segmentation. Do not use epoching or baseline as a
default resting-state step.

## Branch Matrix Reference

The strict order, required steps, conditional steps, forbidden steps, required
figures, and required outputs for ERP, resting-state, time-frequency, source
localization, and STUDY/group analysis live in `branch-workflow-matrix.md`.

## Default Figure Companion

Open `scripts/advanced_figures/` during every branch review so the official
figure atlas stays visible in a browsable form alongside the MCP workflow.

## Branch Entry Notes

- ERP: confirm task-condition triggers first, then follow the event-locked branch.
- Resting-state: prefer spectral and optional connectivity outputs from continuous data.
- Time-frequency: use only event-locked epochs with explicit baseline and cycle settings.
- Source localization: require channel-location coverage, ICA/source model assumptions, and DIPFIT resources.
- STUDY/group analysis: lock single-subject preprocessing before design and statistics.

## Branch Outputs

Every branch should save a derivative, export a protocol, and generate a final
report. Figures are branch-specific:

- ERP: ERP waveform, topoplot, PSD
- Resting-state: PSD, optional connectivity
- Time-frequency: time-frequency plots
- Source: component or source-review figures as justified
- STUDY: group figures justified by the measure family

## Figure Atlas

See `figure-atlas.md` for the canonical static figure families, metadata fields, and branch-specific guidance.

## Safe ERP Shortcut

`safe_erp` is the ERP branch applied through the canonical matrix. Do not enter
it if `eeglab_event_semantics_audit` reports no confirmed analysis events.

## Segment QC

Use `segment_qc` when data contains start/end or block markers but no
condition-level ERP trigger remains.

Sequence:

1. `eeglab_get_events`
2. `eeglab_event_semantics_audit`
3. `eeglab_qc_report`
4. If marker sidecars exist, parse them non-destructively for exact segment start/end samples, times, and durations.
5. `eeglab_protocol_export`

Report that segment markers are boundaries/task-block annotations, not ERP
triggers. Recommend the user provide event codes or behavioral logs before
condition-level ERP/ERSP analysis.

## Light ERP Smoke Workflow

Use `eeglab_erp_light_workflow` when the user wants a complete lightweight ERP
run and accepts a conservative smoke-test sequence. Pass absolute `data_path`
and a new `output_dir`; do not point output at the raw dataset.

Default verification parameters: bandpass 0.5-40 Hz, events `target/standard`,
epoch `[-0.2, 0.8]` seconds, baseline `[-200, 0]` ms, channel `Cz`, ERP time
window `[250, 450]` ms.

Report the workflow `steps`, `parameters`, `outputs`, `summary`, and
`limitations` fields.

## Import Plugin Guidance

BIOSIG, File-IO, MFF-matlab-io, NWB-io, and BVA-io are official or officially
indexed import routes, but plugin-dependent imports need readiness checks
before analysis claims.

1. Use `eeglab_project_plan` to record source format, sidecars/header files, event source, channel-location source, and raw preservation.
2. Use `eeglab_plugin_check` for the requested importer.
3. Use `eeglab_method_preflight` for `import_plugins` with source format, plugin availability, event/channel mapping, and raw input preservation.
4. Use `eeglab_protocol_export` if plugin support, sidecars, or mapping assumptions are missing.

Do not treat imported event or channel metadata as validated until importer
mapping and event semantics have been reviewed.

## BIDS Export Guidance

BIDS export is indexed and plugin-checkable, but this MCP does not expose a
dedicated BIDS export execution tool by default.

1. Use `eeglab_project_plan` to confirm export purpose, derivative status, and metadata completeness.
2. Use `eeglab_plugin_check` for EEG-BIDS export functions.
3. Use `eeglab_method_preflight` for `bids_export` with sidecars, events.tsv columns, events.json/HED/codebook descriptions, derivative output directory, and software/plugin provenance.
4. Use `eeglab_protocol_export` to document export readiness or blockers.

Do not claim BIDS export execution support unless a dedicated export tool,
output validation, and eval coverage are added.

## Data Export Guidance

External data export is indexed through official EEGLAB export guidance and
plugin pages. The MCP can save EEGLAB `.set` derivatives, but BrainVision,
MFF, NWB, and BIDS export paths remain guidance-only unless a dedicated
exporter tool is added.

1. Use `eeglab_project_plan` to identify target format, consumer, derivative status, and required metadata.
2. Use `eeglab_plugin_check` for EEG-BIDS, MFF-matlab-io, NWB-io, BVA-io, or the requested exporter.
3. Use `eeglab_method_preflight` for `data_export` with format support, derivative output, export metadata completeness, and software/plugin provenance.
4. Use `eeglab_protocol_export` for export readiness, limitations, and validation gaps.

Do not present external export as executed support when only a planning/report
path exists.

## HED Event Annotation Guidance

HEDTools and BIDS events metadata can support event semantics, but HED tags
are not automatically condition triggers.

1. Use `eeglab_event_semantics_audit` to classify markers.
2. Use `eeglab_plugin_check` for HEDTools when HED-specific tooling is requested.
3. Use `eeglab_method_preflight` for `hed_event_annotation` with event descriptions, HED schema/version, and a validated condition-code map.
4. Use `eeglab_protocol_export` to report HED/events.json/codebook provenance and remaining ambiguity.

Do not epoch or interpret ERP/ERSP effects from HED labels alone when
condition triggers are not validated.

## History Scripting Guidance

EEGLAB history can help recover GUI work into scripts, but copied history is
not automatically a reproducible batch protocol.

1. Use `eeglab_history` to inspect available history.
2. Use `eeglab_method_preflight` for `history_scripting` with history availability, script review, explicit parameters, and derivative output policy.
3. Use `eeglab_protocol_export` to document reviewed script steps, parameters, outputs, and limitations.

Do not run a history-derived batch script until paths, defaults, dataset
state, and output policy are reviewed.

## Event Script Modification Guidance

Scripted event edits can recode labels, remove markers, shift latencies, or
repair event/urevent relationships, but this MCP does not expose a generic
event-mutation execution tool by default.

1. Use `eeglab_get_events` and `eeglab_event_semantics_audit` before event edits.
2. Use `eeglab_method_preflight` for `event_script_modification` with recode/deletion/latency rules, latency units, urevent policy, and semantic evidence.
3. Use `eeglab_protocol_export` for a report-only plan or recovery note.

Do not create condition triggers through event scripts without a behavioral
log, events.json/HED record, or lab codebook.

## STUDY Precompute And ICA Clustering Guidance

STUDY precompute, visualization, and ICA clustering are indexed official
workflows. The current MCP can plan and gate them, but does not expose
dedicated precompute or clustering execution tools.

1. Use `eeglab_project_plan` for subject/session structure, design variables, and preprocessing protocol lock.
2. Use `eeglab_method_preflight` for `study_precompute` before interpreting STUDY plots, measures, or statistics.
3. Use `eeglab_method_preflight` for `ica_clustering` before any ICA-cluster interpretation.
4. Use `eeglab_protocol_export` to record measure family, precompute parameters, clustering features, cluster algorithm/count, outlier policy, and review criteria.

Do not treat STUDY plots, precomputed measures, or ICA clusters as publishable
group evidence until the staged gates and report fields are complete.

## LIMO Guidance

LIMO is indexed and plugin-checkable, but this MCP does not expose a dedicated
LIMO execution workflow by default.

1. Use `eeglab_project_plan` for the statistical design and data hierarchy.
2. Use `eeglab_plugin_check` for LIMO.
3. Use `eeglab_method_preflight` for `limo_statistics` with plugin availability, first/second-level model, design variables, contrasts, alpha, and correction policy.
4. Use `eeglab_protocol_export` for a methods-ready report.

Do not claim LIMO results unless plugin availability, design matrix,
contrasts, correction policy, and executable workflow support are all explicit.

## AMICA Guidance

AMICA is indexed and plugin-checkable, but this MCP does not expose a dedicated
AMICA execution workflow by default.

1. Use `eeglab_plugin_check` for AMICA.
2. Use `eeglab_method_preflight` for `amica_ica` with continuous-data suitability, rank/PCA/reference review, compute strategy, and derivative output.
3. Use `eeglab_protocol_export` to document algorithm choice and why AMICA is required over the supported runica/Picard path.

Do not run AMICA through generic ICA assumptions unless an AMICA-specific
workflow and eval coverage are added.

## RELICA Guidance

RELICA is indexed and plugin-checkable, but this MCP does not expose a dedicated
RELICA execution workflow by default.

1. Use `eeglab_plugin_check` for RELICA.
2. Use `eeglab_method_preflight` for `relica_reliability` with existing ICA state, RELICA plugin availability, bootstrap settings, compute strategy, and component review policy.
3. Use `eeglab_protocol_export` to record reliability-analysis blockers and why no local RELICA execution claim is made.

Do not claim ICA reliability analysis unless RELICA availability, ICA state,
and bootstrap/review settings are explicit.

## Viewprops Guidance

Viewprops is indexed and plugin-checkable as a component/channel review aid.
It is not a substitute for ICA or ICLabel review decisions.

1. Use `eeglab_plugin_check` for Viewprops and ICLabel.
2. Use `eeglab_method_preflight` for `viewprops_review` with ICA state, reviewed component set, classifier/source evidence, and reporting plan.
3. Use `eeglab_protocol_export` when component decisions need a reproducible review record.

Do not remove components merely because Viewprops is available; component-removal
gates still require explicit thresholds/rationale and derivative output.

## get_chanlocs Guidance

get_chanlocs is indexed and plugin-checkable for channel-location digitization
from head images or digitization sources.

1. Use `eeglab_plugin_check` for get_chanlocs.
2. Use `eeglab_method_preflight` for `get_chanlocs_digitization` with head image/digitization source, fiducials, coordinate assumptions, and channel-location repair plan.
3. Use `eeglab_protocol_export` to document why topography/source claims remain blocked until `EEG.chanlocs` are reviewed.

Do not treat digitization plans as completed channel-location coverage until
the resulting coordinates are loaded and inspected.

## ROIconnect Guidance

ROIconnect is indexed and plugin-checkable for source-level ROI connectivity,
but this MCP does not expose a dedicated ROIconnect execution workflow by
default.

1. Use `eeglab_project_plan` for source/connectivity goals and inference limits.
2. Use `eeglab_plugin_check` for ROIconnect.
3. Use `eeglab_method_preflight` for `roiconnect_source_connectivity` with source model, ROI atlas, connectivity metric, frequency/time window, and statistics/correction policy.
4. Use `eeglab_protocol_export` to document guidance-only status and blockers.

Do not interpret ROIconnect outputs as anatomical connectivity without
source-model, atlas, and statistical validation.

## EEGstats Guidance

EEGstats is indexed and plugin-checkable for band power, alpha peak frequency,
and alpha asymmetry metrics across datasets or STUDYs.

1. Use `eeglab_project_plan` for metric scope, dataset/STUDY structure, and intended inference.
2. Use `eeglab_plugin_check` for EEGstats.
3. Use `eeglab_method_preflight` for `eegstats_metrics` with band/frequency definitions, channels/ROIs or STUDY scope, artifact policy, and report fields.
4. Use `eeglab_protocol_export` to record parameters and limitations.

Do not claim EEGstats-derived results unless plugin availability, metric
definitions, and artifact/data scope are documented.

## SIFT Guidance

SIFT/groupSIFT are indexed and plugin-checkable, but source/MVAR connectivity
remains guidance-only by default.

1. Use `eeglab_project_plan` for connectivity goals and source/sensor interpretation.
2. Use `eeglab_plugin_check` for SIFT and groupSIFT.
3. Use `eeglab_method_preflight` for `sift_connectivity` with model order, stationarity, validation, source/model assumptions, and correction policy.
4. Use `eeglab_protocol_export` to document the guidance-only plan and blockers.

Do not run or claim SIFT connectivity support through this MCP unless a
dedicated execution workflow and eval coverage are added.

## NSGportal Guidance

NSGportal is indexed and plugin-checkable, but remote/HPC execution is outside
the local-first MCP surface by default.

1. Use `eeglab_plugin_check` for NSGportal.
2. Use `eeglab_method_preflight` for `nsg_remote` with user approval, credential policy, data-upload policy, job parameters, upload manifest, and download/recovery plan.
3. Use `eeglab_protocol_export` for the remote-job provenance plan.

Do not execute or claim NSG remote compute support unless a dedicated secure
integration is added.

## Plugin Development Guidance

EEGLAB plugin development is indexed from official contribution tutorials. It
is engineering guidance, not a data-analysis workflow.

1. Use `eeglab_project_plan` to scope the plugin goal, target user operation, and expected research workflow.
2. Use `eeglab_method_preflight` for `plugin_development` with function family, GUI/command-line boundary, and validation plan.
3. Use `eeglab_protocol_export` to document the proposed extension and why no current MCP analysis support is implied.

Do not treat a planned plugin as an official executable analysis path until
implementation, validation, documentation, and eval coverage exist.
