# EEGLAB Research Standard

This project treats the EEGLAB MCP as a local-first research workflow agent, not a clinical decision system. The MCP executes EEGLAB/MATLAB operations; the skill and MCP resources enforce planning, provenance, event semantics, QC gates, parameter records, and reproducible reporting.

## Official Reference Anchors

- [sccn/eeglab GitHub](https://github.com/sccn/eeglab): EEGLAB is the upstream open-source MATLAB/Octave environment this server wraps.
- [EEGLAB functions guide](https://eeglab.org/tutorials/ConceptsGuide/EEGLAB_functions.html): official `pop_` and `eeg_` function model. MCP tools should expose research actions in the same spirit: `pop_`-style user-facing operations plus `eeg_checkset`-style consistency checks.
- [EEGLAB tutorials](https://eeglab.org/tutorials/): official tutorial index for preprocessing, ICA, scripting, ERP, time-frequency, STUDY, and source workflows.
- [EEGLAB import tutorials](https://eeglab.org/tutorials/04_Import/Importing_Continuous_and_Epoched_Data.html): official import guidance for non-native formats and plugin-dependent import paths.
- [EEGLAB data export tutorial](https://eeglab.org/tutorials/misc/Exporting_Data.html): official export guidance for derivative data exchange.
- [EEGLAB history scripting](https://eeglab.org/tutorials/11_Scripting/Using_EEGLAB_history.html) and [event processing scripts](https://eeglab.org/tutorials/11_Scripting/Event_Processing_command_line.html): official scripting anchors for history-derived protocols and event changes.
- [clean_rawdata](https://eeglab.org/plugins/clean_rawdata/): official plugin path for ASR, bad-channel, and bad-segment cleaning.
- [ICLabel](https://github.com/sccn/ICLabel): official component classification plugin used after ICA.
- [DIPFIT](https://eeglab.org/plugins/dipfit/): official source-localization plugin and prerequisite for DIPFIT workflows.
- [EEG-BIDS in EEGLAB](https://eeglab.org/tutorials/11_Scripting/Analyzing_EEG_BIDS_data_in_EEGLAB.html): official BIDS import and STUDY analysis path.
- [HEDTools](https://github.com/sccn/HEDTools), [MFF-matlab-io](https://eeglab.org/plugins/MFF-matlab-io/), [NWB-io](https://eeglab.org/plugins/NWB-io/), and [BVA-io](https://eeglab.org/plugins/BVA-io/): official SCCN/EEGLAB plugin anchors for event annotation and import/export exchange paths.
- [EEGLAB Course](https://github.com/sccn/EEGLAB_course): official course material covering BIDS, preprocessing, ERP/time-frequency, source/connectivity, ICA clustering, and statistics.
- `BIDS-EEG-001`: BIDS EEG sidecars, recording metadata, and HED/event-code descriptions are used as reporting and event-semantics evidence. They supplement EEGLAB official guidance; they do not override EEGLAB/SCCN method gates.
- `BIDS-EVENTS-001`: BIDS `events.tsv` and `events.json` descriptions help validate event semantics. Event labels alone are not enough for ERP/ERSP triggers when condition meaning is undocumented.

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

High-risk methods also use official preflight gates through `eeglab_method_preflight` or high-risk tool `method_context`. Missing critical requirements return `official_gate_blocked` unless the user supplies an explicit override reason. Overrides must be recorded in provenance and protocols.

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
- EEG-BIDS import/export tools for BIDS/STUDY workflows
- BIOSIG, File-IO, MFF-matlab-io, NWB-io, and BVA-io for plugin-dependent import/export paths
- HEDTools for HED event annotation and event-metadata validation
- firfilt, CleanLine, and Zapline-Plus for filter or line-noise variants when requested
- BIDS export and STUDY precompute/ICA clustering only as indexed/guidance-only support unless dedicated execution workflows exist
- history-derived scripts and event-script modification only as gated guidance unless the script, parameters, event rules, urevent policy, and derivative outputs are reviewed
- AMICA or Picard for ICA variants only when plugin availability and method choice are documented
- LIMO, SIFT/groupSIFT, NFT, or NSGportal only as indexed/guidance-only support unless a dedicated execution workflow exists

See `docs/official-method-map.md`, `docs/official-gate-policy.md`, and `docs/official-plugin-map.md` for the claim-map backed gate implementation.
For complete coverage auditing, read the official topic index, support matrix, risk matrix, and report field matrix exposed as MCP resources:
`eeglab://official/topic-index.md`, `eeglab://official/support-matrix.md`, `eeglab://official/tool-support-matrix.md`, `eeglab://official/risk-matrix.md`, and `eeglab://official/report-field-matrix.md`.

## Analysis Branch Prerequisites

- ERP: validated condition triggers, epoch/baseline windows, channel/ROI plan, filtering/rereference policy.
- Time-frequency: ERP prerequisites plus frequency range, cycles/wavelet settings, and baseline plan.
- Resting-state: continuous data suitability, eyes-open/eyes-closed or block context, spectral/connectivity outputs, artifact policy.
- ICA cleanup: continuous-data suitability, rank/reference policy, bad-channel handling, ICA algorithm, ICLabel review policy.
- Source localization: ICA or justified source model, complete montage/channel locations, DIPFIT resources, model/template assumptions.
- BIDS/STUDY/group: stable single-subject preprocessing protocol, subject/session metadata, design variables, alpha/correction policy.

## Reporting Minimum

Each report should include input path, output path, sampling rate, duration, channel count, channel-location coverage, reference/montage, event labels/counts and semantics, filter cutoffs, line-noise method, rereference, epoch/baseline windows, artifact rejection or ICA decisions, plugins, official gate status, source claim IDs, generated files, failures/recovery, and limitations. The report field matrix is the minimum reporting checklist for ERP, resting spectral, ERSP/ITC, BIDS/STUDY, source, LIMO, and SIFT guidance workflows.
