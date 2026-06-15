# Official Tool Support Matrix

This matrix answers whether a specific MCP tool is officially aligned, whether it can execute, and what must be reported. It complements the topic index and method gate map.

## Support Labels

- `read_only`: inspects state, plans, audits, or renders reports without changing EEG data.
- `executable`: can run locally through EEGLAB/MATLAB after schema validation and any required method gates.
- `gated_executable`: executable only when the mapped official method profile passes.
- `guidance_only`: indexed, planned, or checked, but no dedicated execution workflow is promised.

## Research Workflow Tools

| Tool | Support | Official alignment | Read/write effect | Required report fields |
| --- | --- | --- | --- | --- |
| `eeglab_qc_report` | `read_only` | EEGLAB data structures and provenance | reads current EEG metadata/events/history | recording facts, channel-location coverage, event counts, history, risks |
| `eeglab_workflow_recommend` | `read_only` | project planning and official gates | no MATLAB execution | assumptions, clarifying questions, branch choice, blocked actions |
| `eeglab_project_plan` | `read_only` | topic/support/risk matrices | no MATLAB execution | project phases, gates, missing metadata, support levels |
| `eeglab_method_preflight` | `read_only` | official claim map | no MATLAB execution | method profile, gate status, missing requirements, source claim IDs |
| `eeglab_plugin_check` | `read_only` | official plugin matrix | probes MATLAB path only | plugin availability, support_level, functions checked, next steps |
| `eeglab_event_semantics_audit` | `read_only` | event/urevent and BIDS events policy | no data mutation | event roles, excluded markers, confirmed triggers, limitations |
| `eeglab_protocol_export` | `read_only` or file write | report field matrix | may write a protocol artifact | all report-field matrix groups, outputs, limitations |
| `eeglab_erp_light_workflow` | `gated_executable` | ERP/epoch and derivative gates | writes derivative ERP dataset | event semantics, filter/epoch/baseline parameters, output paths |

## Low-Level Tool Families

| Family | Tools | Support | Gate profile | Notes |
| --- | --- | --- | --- | --- |
| Data import/provenance | `eeglab_init`, `eeglab_load_data`, `eeglab_info`, `eeglab_history`, `eeglab_get_events`, `eeglab_save_data` | `executable`/`read_only` | acquisition provenance plus `import_plugins`, `data_export`, and `history_scripting` guidance where relevant | preserve source path, importer/exporter path, event/channel mapping, history, and derivative output status |
| BIDS/STUDY import | `eeglab_import_bids`, `eeglab_study_create`, `eeglab_study_design`, `eeglab_study_statistics` | `gated_executable` | `bids_import`, `study_create`, `study_design`, `study_statistics`, `bids_metadata` | stage gates separately: BIDS/plugin metadata for import, project structure for create, variables for design, protocol/measure/alpha/correction for statistics |
| BIDS export, import/export plugins, HED, history, and advanced STUDY | planning tools only: `eeglab_project_plan`, `eeglab_plugin_check`, `eeglab_protocol_export`, `eeglab_event_semantics_audit`, `eeglab_method_preflight` | `guidance_only` | `bids_export`, `import_plugins`, `data_export`, `hed_event_annotation`, `history_scripting`, `event_script_modification`, `study_precompute`, `ica_clustering` | indexed official topics; no default external export, HED mutation, event-mutation, precompute, or clustering execution tool is promised |
| Core preprocessing | `eeglab_filter`, `eeglab_resample`, `eeglab_reref`, `eeglab_reject_epochs` | `gated_executable` | `derivative_processing` | require raw preservation, derivative output, and parameter record |
| Montage and channel repair | `eeglab_edit_channels`, `eeglab_interpolate_channels`, `eeglab_select_channels` | `gated_executable` | `channel_locations` where relevant | edit/interpolation need existing coordinates or repair plan; topographic/source interpretation still needs usable locations |
| Line-noise cleanup | `eeglab_clean_line_noise` | `gated_executable` | `line_noise` | require local 50/60 Hz frequency, method parameters, and derivative output |
| ASR/clean_rawdata | `eeglab_clean_rawdata` | `gated_executable` | `clean_rawdata` | require continuous data, plugin availability, thresholds, derivative output |
| ICA/ICLabel | `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_flag_components`, `eeglab_remove_components`, `eeglab_plot_components` | `gated_executable` | `run_ica`, `iclabel`, `remove_components` | ICLabel is decision support; component removal needs review/rationale |
| ERP/epoching | `eeglab_epoch`, `eeglab_erp_analysis`, `eeglab_sort_epochs`, `eeglab_average_erp`, `eeglab_plot_erp` | `gated_executable` | `epoch` | confirmed condition triggers only; no boundary/impedance/segment-only epoching |
| Spectral/time-frequency/connectivity | `eeglab_spectral`, `eeglab_timefreq`, `eeglab_connectivity`, `eeglab_plot_timefreq` | `gated_executable` | `spectral`, `timefreq`, `connectivity` | report frequency range, baseline/cycles, artifact policy, channel/ROI, interpretation limits |
| Topography | `eeglab_topoplot` | `gated_executable` | `topography` | requires usable channel locations and time/frequency selection |
| Source/DIPFIT | `eeglab_source_settings`, `eeglab_source_localization` | `gated_executable` | `source` | requires ICA/source model, channel locations, DIPFIT, head model/template |
| One-click pipeline | `eeglab_pipeline` | `gated_executable` | `pipeline` | use only when defaults are accepted and outputs are derivatives |

## Guidance-Only Advanced Methods

LIMO, SIFT/groupSIFT, NFT, NSGportal, AMICA, Zapline-Plus, BIDS export, BIOSIG/File-IO/MFF/NWB/BVA import/export routes, HEDTools, STUDY precompute, ICA clustering, history-derived batch scripting, scripted event modification, and other advanced plugins/topics are covered by the plugin and method matrices. They are not default execution support unless a dedicated MCP tool/workflow, method gate, report template, and eval coverage are added.

## Minimum Answer Format

When asked whether a tool is safe to use, answer with:

- support label
- mapped EEGLAB function family
- method profile and source claim IDs
- preflight fields required before execution
- whether data will be modified or a derivative will be written
- report fields and limitations
