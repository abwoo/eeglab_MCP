# EEGLAB MCP Tool Reference

The server exposes registry-defined 37 legacy low-level `eeglab_*` tools plus 8 research workflow tools for QC, planning, official preflight, protocol, plugin, and event-semantics work. Low-level tools follow the official EEGLAB pattern: user-facing `pop_` operations for data transformations/plots and `eeg_`/structure checks for consistency and metadata inspection.

## Dual MCP Routing

- Use eeglab first for EEG/EEGLAB workflows: load data, QC/provenance, events, preprocessing, ICA, ERP, spectral/time-frequency/connectivity, visualization, source, STUDY, and pipelines.
- Use matlab MCP for generic MATLAB scripts, custom `.m` functions, matrix/statistical code, or non-EEGLAB toolboxes.
- Treat `eeglab` and matlab MCP as workspace-isolated sessions; do not assume `EEG` or `ALLEEG` variables are shared.
- Use file handoff for cross-server work by saving explicit `.set/.fdt`, `.mat`, `.csv`, `.png`, or report paths.
- Keep output paths disjoint so both MCP servers do not write the same file concurrently.

## Research Workflows

- `eeglab_qc_report`: loaded-dataset QC summary, recording metadata, event/channel/ICA state, processing-history availability, provenance hints, and basic risk hints.
- `eeglab_erp_light_workflow`: load, inspect, bandpass filter, epoch, baseline, ERP summary, and save a processed copy.
- `eeglab_workflow_recommend`: recommend reproducible project phases, clarifying questions, default assumptions, adaptive decision rules, QC gates, self-evolution hooks, and minimum report fields without changing data.
- `eeglab_project_plan`: create a research-grade project plan from goal/design/data/event/montage/plugin facts; returns blocking conditions, not-recommended actions, QC gates, quick modes, and official reference anchors.
- `eeglab_protocol_export`: render Markdown/JSON protocol text and optionally write it to a local file; pass upstream `gate_results`, `source_claim_ids`, `report_fields`, and override fields for lab notebooks, handoff, or methods-section drafts.
- `eeglab_plugin_check`: probe local MATLAB/EEGLAB path for the official plugin matrix: clean_rawdata, ICLabel, DIPFIT, EEG-BIDS, BIOSIG, File-IO, MFF-matlab-io, NWB-io, BVA-io, HEDTools, firfilt, CleanLine, Zapline-Plus, AMICA, Picard, RELICA, Viewprops, get_chanlocs, ROIconnect, EEGstats, LIMO, SIFT, groupSIFT, NFT, and NSGportal. It returns availability, `support_level`, claim IDs, dependent profiles such as `import_plugins`, `data_export`, `hed_event_annotation`, `bids_export`, `study_precompute`, `ica_clustering`, `amica_ica`, `relica_reliability`, `viewprops_review`, `get_chanlocs_digitization`, `roiconnect_source_connectivity`, `eegstats_metrics`, and `nsg_remote`, checked functions, found functions, and next steps.
- `eeglab_event_semantics_audit`: classify markers as condition triggers, boundaries, impedance/QC annotations, segment markers, excluded labels, or candidate triggers before epoching.
- `eeglab_method_preflight`: evaluate official EEGLAB/SCCN method gates before high-risk processing; returns `gate_status`, missing requirements, `source_claim_ids`, and safe next step.

## High-Risk Gate Fields

High-risk tools accept these optional fields:

- `method_context`: known facts for official preflight, such as data shape, event roles, plugins, ICA state, channel locations, output plan, rank/reference review, or design variables.
- `override_gate`: set true only after the user explicitly accepts missing official prerequisites.
- `override_reason`: required when `override_gate=true`; must be reported in provenance and protocol output.

## Data Management

- `eeglab_init`: start MATLAB/EEGLAB.
- `eeglab_load_data`: load `.set/.fdt`, `.edf`, `.bdf`, `.vhdr`, `.cnt`; treat these as imported recordings whose acquisition metadata may be incomplete.
- `eeglab_save_data`: save the current EEG as `.set`.
- `eeglab_import_bids`: import BIDS data.
- `eeglab_info`: inspect recording dimensions, file provenance, data shape, channel-location coverage, events, processing-history availability, and ICA status.
- `eeglab_history`: read EEGLAB operation history.

## Preprocessing

- `eeglab_filter`: `pop_eegfiltnew`-style bandpass, highpass, lowpass, or notch filtering; records cutoffs and modifies in-memory EEG.
- `eeglab_resample`: `pop_resample`-style sample-rate change; justify target rate before use.
- `eeglab_reref`: `pop_reref`-style average/channel/REST reference; report rank/reference implications.
- `eeglab_select_channels`: `pop_select`-style include/exclude channel subset.
- `eeglab_interpolate_channels`: `pop_interp`-style bad-channel interpolation; requires usable channel locations.
- `eeglab_edit_channels`: `pop_chanedit`-style channel-location load or channel rename.
- `eeglab_clean_line_noise`: remove 50/60 Hz line noise; report local mains frequency.
- `eeglab_clean_rawdata`: `clean_rawdata`/ASR cleanup; plugin-dependent and high-impact, so record thresholds and removed data.

## ICA and Artifact Handling

- `eeglab_run_ica`: `pop_runica`/runica or Picard; high-risk/slow, needs rank/reference and continuous-data suitability.
- `eeglab_classify_ica`: classify components with ICLabel; requires ICA weights and ICLabel plugin.
- `eeglab_flag_components`: flag components by class probability ranges.
- `eeglab_remove_components`: `pop_subcomp`-style component removal; never remove without rationale and thresholds.
- `eeglab_reject_epochs`: reject epochs by threshold or joint probability.
- `eeglab_get_events`: summarize events.

## ERP and Epoching

- `eeglab_epoch`: `pop_epoch`-style epoching and baseline correction; requires confirmed condition triggers, not boundaries/impedance/segment markers.
- `eeglab_erp_analysis`: compute ERP summaries and optional peaks.
- `eeglab_sort_epochs`: sort epochs by condition/event.
- `eeglab_average_erp`: average ERP by condition/channel.

## Frequency and Connectivity

- `eeglab_spectral`: spectrum and band power.
- `eeglab_timefreq`: ERSP/ITC time-frequency analysis.
- `eeglab_connectivity`: coherence or PLV connectivity.
These tools require explicit frequency range and artifact policy before interpretation. Connectivity reports must state sensor/source limits and avoid anatomical connectivity claims without source/model validation.

## Visualization

- `eeglab_topoplot`: scalp topography figure.
- `eeglab_plot_erp`: ERP waveform figure.
- `eeglab_plot_timefreq`: ERSP/ITC figure.
- `eeglab_plot_components`: ICA component plots.

## Source and Group Analysis

- `eeglab_source_settings`: DIPFIT model setup; requires montage/model assumptions.
- `eeglab_source_localization`: DIPFIT component dipole fitting; requires ICA, channel locations, and DIPFIT resources.
- `eeglab_study_create`: create STUDY from BIDS or datasets; requires consistent subject/session metadata.
- `eeglab_study_design`: define STUDY design variables/levels.
- `eeglab_study_statistics`: configure/run STUDY statistics; report alpha and correction method.
- `eeglab_pipeline`: one-click ERP/resting/time-frequency pipeline.

## Official Function and Plugin Mapping

- `pop_loadset`, `pop_biosig`, BrainVision import functions: data loading and import.
- BIOSIG, File-IO, MFF-matlab-io, NWB-io, BVA-io, and HEDTools functions: plugin-dependent import/export/event-metadata guidance.
- `eeg_checkset`: consistency checks after load or transformations.
- `pop_saveset`: derivative `.set/.fdt` save.
- `pop_eegfiltnew`, `pop_resample`, `pop_reref`, `pop_select`, `pop_interp`, `pop_chanedit`: core preprocessing.
- `clean_rawdata`/`pop_clean_rawdata`: ASR, bad channels, and bad segments.
- `pop_runica`, runica, Picard: ICA decomposition.
- `pop_iclabel`, ICLabel: component classification.
- `pop_subcomp`: component removal.
- `pop_epoch`, baseline correction: event-locked ERP/ERSP preparation.
- `spectopo`, `newtimef`, `topoplot`: spectral, ERSP/ITC, and topography outputs.
- `pop_dipfit_settings`, DIPFIT, `pop_multifit`: source localization.
- `pop_importbids`, `pop_exportbids`, `bids_export`, `pop_study`, `std_makedesign`, STUDY precompute/statistics functions: BIDS/STUDY/group workflows.
- AMICA, RELICA, Viewprops, get_chanlocs, ROIconnect, EEGstats, and NSGportal functions are indexed for plugin checks, but execution remains guidance-only unless a dedicated workflow exists.

## Common Parameter Defaults

- First report: input path, sampling rate, data shape, duration, channel count, channel-location coverage, reference/montage, event labels/counts, event latency range, and history availability.
- Workflow recommendation input: pass `research_goal`, `analysis_type`, `project_scale`, `stage`, `event_types`, `srate`, `data_shape`, `has_ica`, and `has_channel_locations` whenever known. If unknown, let the tool return clarifying questions and conservative defaults.
- ERP epoch window: `[-0.2, 0.8]` seconds.
- ERP baseline: `[-200, 0]` ms.
- Resting spectral range: usually `[0.5, 45]` or `[0.5, 80]` Hz.
- Time-frequency range: often `[3, 80]` Hz.
- ASR `burst_criterion`: 20 is conservative; 5 is aggressive.
- ICA: `picard` is often faster when the plugin is available; `runica` is the stable built-in default.

## Project-Scale Guardrails

- Single-subject exploratory work: prefer explicit low-level tools and save named intermediate outputs.
- Multi-subject work: lock the single-subject preprocessing protocol before STUDY/group statistics.
- BIDS/STUDY work: keep sidecar metadata, subject/session identifiers, design variables, alpha, correction method, and preprocessing assumptions in the report.
- Missing goal: ask for the hypothesis/analysis family. If unavailable, choose a conservative feasibility workflow from data shape and event availability.
- Event ambiguity: call `eeglab_event_semantics_audit`; do not treat start/end, impedance, or segment markers as ERP triggers.
- Missing montage: block topography/source claims until channel locations are repaired.
- Plugin dependency: run `eeglab_plugin_check` before ASR, ICLabel, DIPFIT, EEG-BIDS/STUDY, BIDS export, BIOSIG/File-IO/MFF/NWB/BVA import/export, HEDTools event annotation, STUDY precompute/clustering, firfilt/CleanLine/Zapline, AMICA/Picard, RELICA, Viewprops, get_chanlocs, ROIconnect, EEGstats, LIMO, SIFT, groupSIFT, NFT, or NSGportal-dependent workflows. Treat `indexed_only` plugins and profiles as guidance-only unless a dedicated workflow exists.
- Official gate blocked: stop, report missing requirements and `source_claim_ids`, then ask for missing facts or explicit override.
- Self-evolution: add evals/references for repeated project patterns instead of relying on memory.
