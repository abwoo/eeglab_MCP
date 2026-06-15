# EEGLAB MCP User Workflows

These workflows are designed for users who want fast progress without losing research rigor.

## 1. quick_qc

Goal: inspect a dataset without modifying it.

Use when the user says: "看看这个数据", "先检查一下", "load and QC", or gives a new file with no goal yet.

Tool path:

1. `eeglab_init`
2. `eeglab_load_data`
3. `eeglab_qc_report`
4. `eeglab_info`
5. `eeglab_get_events`
6. `eeglab_history`

Output: recording/provenance summary, event table, montage/channel-location status, history availability, risk hints, and recommended next step.

## 2. safe_erp

Goal: run ERP only when event semantics are scientifically valid.

Use when the user has task events such as target/standard/condition codes and wants ERP outputs.

Required gates:

- condition triggers confirmed by user, event map, or behavioral log
- boundary/impedance/segment markers excluded from epoching
- epoch and baseline windows justified
- output path is separate from raw files

Tool path:

1. `eeglab_project_plan` or `eeglab_workflow_recommend`
2. `eeglab_event_semantics_audit`
3. `eeglab_method_preflight` with `method="epoch"` and confirmed event roles
4. `eeglab_filter`
5. optional `eeglab_clean_line_noise`
6. optional ICA/ICLabel branch after its own preflight
7. `eeglab_epoch`
8. `eeglab_erp_analysis`
9. optional `eeglab_plot_erp` or `eeglab_topoplot`
10. `eeglab_save_data`
11. `eeglab_protocol_export`

## 3. segment_qc

Goal: analyze datasets that have only start/end markers or task-block boundaries.

Use when the marker file has labels like `s1000` for experiment start/end and no condition-level trigger remains.

Policy:

- preserve markers as boundary or segment annotations
- pair start/end markers sequentially only if user confirms that convention
- do not claim ERP/ERSP condition effects
- report segment start/end samples, times, durations, and excluded markers

Tool path:

1. `eeglab_get_events`
2. `eeglab_event_semantics_audit`
3. `eeglab_method_preflight` with `method="epoch"` to document why ERP epoching is blocked
4. `eeglab_qc_report`
5. optional external marker-file parser for precise segment tables
6. `eeglab_protocol_export`

## 4. study_ready_check

Goal: decide whether a multi-subject or BIDS project is ready for STUDY/group statistics.

Required gates:

- subject/session layout known
- BIDS or dataset paths consistent
- event/condition variables known
- single-subject preprocessing protocol locked
- plugin availability checked
- alpha and correction policy documented

Tool path:

1. `eeglab_project_plan`
2. `eeglab_plugin_check`
3. `eeglab_method_preflight` with `method="study"` before any group-level conclusion
4. `eeglab_method_preflight` with `method="bids_import"` before BIDS import, or `method="study_create"` before creating a STUDY from existing datasets
5. `eeglab_import_bids` or `eeglab_study_create`
6. `eeglab_method_preflight` with `method="study_design"`, then `eeglab_study_design`
7. `eeglab_method_preflight` with `method="study_statistics"`, then `eeglab_study_statistics`
8. `eeglab_protocol_export`

## 5. plugin_doctor

Goal: check whether the local MATLAB/EEGLAB environment can support the requested workflow.

Use before:

- ASR or clean_rawdata
- ICA + ICLabel cleanup
- DIPFIT/source localization
- EEG-BIDS/STUDY import
- BIOSIG, File-IO, MFF, NWB, or BrainVision/BVA import/export readiness
- HEDTools or HED event annotation readiness
- firfilt, CleanLine, or Zapline-Plus line-noise/filtering choices
- BIDS export or derivative-publication readiness
- STUDY precompute, visualization, or ICA clustering interpretation
- AMICA or Picard ICA variants
- RELICA, Viewprops, get_chanlocs, ROIconnect, EEGstats, LIMO, SIFT, groupSIFT, NFT, or NSGportal-dependent analysis

Tool path:

1. `eeglab_init`
2. `eeglab_plugin_check`
3. `eeglab_method_preflight` for the requested plugin-dependent method
4. report each plugin's `support_level`, missing functions, dependent profiles, and next installation/path steps

Policy:

- `executable` and `gated_guidance` plugins still require method preflight before scientific claims.
- `indexed_only` plugins are planning/reporting support only unless a dedicated MCP workflow exists.
- `bids_export`, `import_plugins`, `data_export`, `hed_event_annotation`, `history_scripting`, `event_script_modification`, `study_precompute`, `ica_clustering`, `amica_ica`, `relica_reliability`, `viewprops_review`, `get_chanlocs_digitization`, `roiconnect_source_connectivity`, `eegstats_metrics`, `sift_connectivity`, and `nsg_remote` are guidance/preflight profiles, not default execution support.

## Choosing eeglab MCP vs matlab MCP

Use `eeglab` MCP for EEG/EEGLAB standard workflows. Use the general `matlab` MCP only for custom MATLAB scripts, external toolboxes, statistics/matrix code, or follow-up calculations outside the EEGLAB MCP surface.

The two MCP servers do not share MATLAB workspace. Save `.set/.fdt`, `.mat`, `.csv`, `.png`, or protocol/report files from `eeglab`, then pass the explicit path to `matlab`.
