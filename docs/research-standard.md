# EEGLAB Research Standard

This project treats the EEGLAB MCP as a local-first research workflow agent, not a clinical decision system. The MCP executes EEGLAB/MATLAB operations; the skill and MCP resources enforce planning, provenance, event semantics, QC gates, parameter records, and reproducible reporting.

## Official Reference Anchors

- [sccn/eeglab GitHub](https://github.com/sccn/eeglab): EEGLAB is the upstream open-source MATLAB/Octave environment this server wraps.
- [EEGLAB functions guide](https://eeglab.org/tutorials/ConceptsGuide/EEGLAB_functions.html): official `pop_` and `eeg_` function model. MCP tools should expose research actions in the same spirit: `pop_`-style user-facing operations plus `eeg_checkset`-style consistency checks.
- [EEGLAB tutorials](https://eeglab.org/tutorials/): official tutorial index for preprocessing, ICA, scripting, ERP, time-frequency, STUDY, and source workflows.
- [clean_rawdata](https://eeglab.org/plugins/clean_rawdata/): official plugin path for ASR, bad-channel, and bad-segment cleaning.
- [ICLabel](https://github.com/sccn/ICLabel): official component classification plugin used after ICA.
- [DIPFIT](https://eeglab.org/plugins/dipfit/): official source-localization plugin and prerequisite for DIPFIT workflows.
- [EEG-BIDS in EEGLAB](https://eeglab.org/tutorials/11_Scripting/Analyzing_EEG_BIDS_data_in_EEGLAB.html): official BIDS import and STUDY analysis path.
- [EEGLAB Course](https://github.com/sccn/EEGLAB_course): official course material covering BIDS, preprocessing, ERP/time-frequency, source/connectivity, ICA clustering, and statistics.

## Product Advantages

- Faster than generic MATLAB MCP for EEG: the user asks for research actions, not raw MATLAB scripts.
- More reproducible than manual GUI-only work: tool calls record JSON arguments, outputs, limitations, and QC gates.
- Safer than an unconstrained agent: the skill requires goal/design intake, raw preservation, event semantics, montage checks, and plugin gates before high-risk steps.
- More reliable than a skill alone: the MCP actually executes EEGLAB locally; the skill decides and documents.
- Local-first by design: EEG data stays on the user's machine. Cross-MCP collaboration happens only through explicit files.

## Research Gate Policy

Every project starts with `quick_qc`: load, info, events, history, and QC report. No filtering, ICA, source localization, or group statistics should happen before these gates are checked:

- raw input preserved and output directory separate
- recording metadata reported
- channel-location coverage checked
- event labels and latencies audited
- processing history or current-session steps recorded
- analysis branch matches design and data shape
- destructive steps write new outputs
- artifact rejection thresholds recorded
- outputs and limitations reported

## Event Semantics Policy

Event labels are not automatically analysis triggers. Before ERP or time-frequency analysis:

- classify labels as condition/trigger, boundary, impedance/QC annotation, segment marker, excluded marker, or candidate trigger
- do not epoch around boundary, impedance, excluded, or segment-only markers
- if only start/end markers remain, use segment-level QC or task-block analysis until a behavioral log or condition-code map is provided
- report the user-provided event meaning as source of truth when it conflicts with heuristic inference

## Plugin Policy

Plugin-dependent workflows must check availability before claiming readiness:

- clean_rawdata for ASR and bad-channel/bad-segment cleanup
- ICLabel for automated ICA component labels
- DIPFIT for source localization
- BIDS import tools for BIDS/STUDY workflows
- LIMO or SIFT only when those workflows are explicitly requested and installed

## Analysis Branch Prerequisites

- ERP: validated condition triggers, epoch/baseline windows, channel/ROI plan, filtering/rereference policy.
- Time-frequency: ERP prerequisites plus frequency range, cycles/wavelet settings, and baseline plan.
- Resting-state: continuous data suitability, eyes-open/eyes-closed or block context, spectral/connectivity outputs, artifact policy.
- ICA cleanup: continuous-data suitability, rank/reference policy, bad-channel handling, ICA algorithm, ICLabel review policy.
- Source localization: ICA or justified source model, complete montage/channel locations, DIPFIT resources, model/template assumptions.
- BIDS/STUDY/group: stable single-subject preprocessing protocol, subject/session metadata, design variables, alpha/correction policy.

## Reporting Minimum

Each report should include input path, output path, sampling rate, duration, channel count, channel-location coverage, reference/montage, event labels/counts and semantics, filter cutoffs, rereference, epoch/baseline windows, artifact rejection or ICA decisions, plugins, generated files, failures/recovery, and limitations.
