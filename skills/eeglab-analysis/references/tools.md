# EEGLAB MCP Tool Reference

The server exposes 40 tools grouped by workflow area: 37 compatible low-level tools plus 3 high-level workflow tools.

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

## Data Management

- `eeglab_init`: start MATLAB/EEGLAB.
- `eeglab_load_data`: load `.set/.fdt`, `.edf`, `.bdf`, `.vhdr`, `.cnt`; treat these as imported recordings whose acquisition metadata may be incomplete.
- `eeglab_save_data`: save the current EEG as `.set`.
- `eeglab_import_bids`: import BIDS data.
- `eeglab_info`: inspect recording dimensions, file provenance, data shape, channel-location coverage, events, processing-history availability, and ICA status.
- `eeglab_history`: read EEGLAB operation history.

## Preprocessing

- `eeglab_filter`: bandpass, highpass, lowpass, or notch filtering.
- `eeglab_resample`: change sampling rate.
- `eeglab_reref`: average, channel, or REST reference.
- `eeglab_select_channels`: include/exclude channels.
- `eeglab_interpolate_channels`: interpolate bad channels.
- `eeglab_edit_channels`: load channel locations or rename channels.
- `eeglab_clean_line_noise`: remove 50/60 Hz line noise.
- `eeglab_clean_rawdata`: ASR cleanup.

## ICA and Artifact Handling

- `eeglab_run_ica`: run `runica` or `picard`.
- `eeglab_classify_ica`: classify components with ICLabel.
- `eeglab_flag_components`: flag components by class probability ranges.
- `eeglab_remove_components`: remove listed or auto-selected components.
- `eeglab_reject_epochs`: reject epochs by threshold or joint probability.
- `eeglab_get_events`: summarize events.

## ERP and Epoching

- `eeglab_epoch`: epoch around events and baseline-correct.
- `eeglab_erp_analysis`: compute ERP summaries and optional peaks.
- `eeglab_sort_epochs`: sort epochs by condition/event.
- `eeglab_average_erp`: average ERP by condition/channel.

## Frequency and Connectivity

- `eeglab_spectral`: spectrum and band power.
- `eeglab_timefreq`: ERSP/ITC time-frequency analysis.
- `eeglab_connectivity`: coherence or PLV connectivity.

## Visualization

- `eeglab_topoplot`: scalp topography figure.
- `eeglab_plot_erp`: ERP waveform figure.
- `eeglab_plot_timefreq`: ERSP/ITC figure.
- `eeglab_plot_components`: ICA component plots.

## Source and Group Analysis

- `eeglab_source_settings`: DIPFIT model setup.
- `eeglab_source_localization`: component dipole fitting.
- `eeglab_study_create`: create STUDY from BIDS or datasets.
- `eeglab_study_design`: define STUDY design.
- `eeglab_study_statistics`: configure/run STUDY statistics.
- `eeglab_pipeline`: one-click ERP/resting/time-frequency pipeline.

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
- Self-evolution: add evals/references for repeated project patterns instead of relying on memory.
