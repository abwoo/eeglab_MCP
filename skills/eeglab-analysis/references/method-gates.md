# EEGLAB Method Gates

Use this reference when a workflow is about to call a high-risk `eeglab_*` tool.
The executable gate is `eeglab_method_preflight`; this file explains the stable
method families and the facts that should be supplied as `context` or
`method_context`.

## Gate Inputs

- `method` or `tool_name`: map the requested work to a method profile.
- `context`: known facts such as event roles, data shape, plugin availability,
  ICA state, channel-location coverage, derivative output plan, rank/reference
  review, design variables, and single-subject protocol state.
- `override_reason`: only when the user explicitly accepts a blocked method
  risk and the report will not overclaim scientific certainty.

## High-Risk Families

- `derivative_processing`: filter, resample, rereference, line-noise cleanup,
  and epoch rejection require raw preservation, derivative output, and recorded
  parameters.
- `acquisition_provenance`: requires raw preservation, derivative output,
  reference/montage, power-line frequency, and acquisition-filter notes, or an
  explicit record that a metadata field is unavailable.
- `bids_metadata`: requires BIDS EEG sidecars, `events.tsv` onset/duration, and
  `events.json`, HED, or a lab codebook for `trial_type` and additional event
  columns before condition-level claims.
- `epoch` and `timefreq`: require confirmed condition triggers and baseline or
  frequency settings before ERP/ERSP/ITC claims.
- `clean_rawdata`: requires continuous-data suitability, clean_rawdata
  availability, thresholds, and derivative output.
- `run_ica`, `iclabel`, and `remove_components`: require continuous-data/rank
  review, ICA availability for ICLabel, plugin checks, and component-review
  rationale before removal.
- `source`: requires ICA or a justified source model, channel locations, DIPFIT
  resources, and head model/template assumptions.
- `bids_import`: requires BIDS metadata or sidecars, EEG-BIDS import support,
  and event timing metadata review.
- `import_plugins`: requires source format, importer/plugin availability,
  event/channel mapping, and raw-file preservation before plugin-dependent
  imports are treated as analysis-ready.
- `data_export`: requires target format support, derivative output, metadata
  completeness, and software/plugin provenance before non-.set export claims.
- `hed_event_annotation`: requires event descriptions, HED schema/version or
  codebook provenance, and condition-code validation before event-locked claims.
- `history_scripting`: requires processing history and reviewed history-derived
  scripts before GUI history is treated as a reusable batch protocol.
- `event_script_modification`: requires event modification rules, latency units,
  and urevent preservation/relinking before scripted event changes support
  analysis.
- `study_create`: requires BIDS or multi-subject organization; protocol lock is
  advisory until statistics-ready claims.
- `study_design`: requires BIDS or multi-subject organization plus design
  variables and levels.
- `study_statistics`: requires BIDS or multi-subject organization, locked
  single-subject preprocessing, design variables, measure, and alpha/correction.
- `study`: planning/ready-check alias for the combined BIDS/STUDY/group-analysis
  decision.
- `pipeline`: requires raw preservation, derivative output, and explicit
  acceptance of bundled defaults.

If a gate returns `blocked`, stop. Resolve missing critical requirements or
rerun only with a user-approved override reason.
