# BIDS And STUDY Policy

Use this reference for multi-subject, BIDS, STUDY, LIMO, or group-statistics requests.

## Required Gate

Run `eeglab_project_plan` first, then use staged `eeglab_method_preflight`
profiles instead of treating all STUDY work as one gate:

- `bids_metadata` before trusting BIDS sidecars for event or acquisition
  semantics.
- `bids_import` before `eeglab_import_bids`.
- `study_create` before `eeglab_study_create`.
- `study_design` before `eeglab_study_design`.
- `study_statistics` before `eeglab_study_statistics`.
- `study` remains a planning/ready-check alias for the combined group-analysis
  decision.

Required context:

- `project_scale`: `multi_subject` or `bids_study`
- BIDS root or dataset paths
- BIDS EEG metadata sidecars: `*_eeg.json`, `*_channels.tsv`,
  `*_electrodes.tsv`, and `*_coordsystem.json`, or an explicit provenance note
  explaining which metadata are unavailable
- `*_events.tsv` columns include `onset` and `duration`
- `*_events.json`, HED tags, behavioral log, or lab codebook describes
  `trial_type` and any additional event columns
- `single_subject_protocol_locked`
- `design_variables_defined`
- alpha/correction/statistical parameter policy before statistics

## Routing

Use `eeglab_method_preflight` with `method="bids_metadata"` before trusting BIDS sidecars for event semantics. Then use `eeglab_import_bids` for BIDS folders after `bids_import`, `eeglab_study_create` for BIDS or explicit dataset lists after `study_create`, `eeglab_study_design` for variables/levels after `study_design`, and `eeglab_study_statistics` only after `study_statistics` confirms the design, measure, preprocessing protocol, alpha, and correction policy.

Do not run group statistics as a substitute for unresolved single-subject preprocessing, missing design variables, or missing provenance.
