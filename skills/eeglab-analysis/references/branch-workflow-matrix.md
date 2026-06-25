# Canonical Branch Workflow Matrix

This EEGLAB branch workflow matrix is the execution-layer branch contract for
the `eeglab` MCP workflow skill.

This file is the execution-layer workflow matrix for branch-appropriate EEG analysis.
If `docs/` and `references/` ever differ, follow `docs/` for authority policy and
update this matrix to match.

## Universal Preamble

Apply these steps before any branch-specific processing:

1. Project intake and branch selection
2. Raw preservation and separate derivative output path
3. Recording/provenance audit
4. QC loadability check
5. Event or continuous-data suitability check
6. Plugin check if the branch depends on plugins
7. Method preflight before any high-risk step
8. Default figure companion review in `scripts/advanced_figures/`

## ERP

Mode: `event_locked`

Required steps:

1. Event semantics audit
2. Filter and line-noise cleanup
3. Rereference
4. Epoch and baseline
5. ERP analysis
6. Save derivative
7. Protocol export
8. Final report

Conditional steps:

- clean_rawdata / ASR when justified
- ICA, ICLabel, and component review when justified
- Component removal or epoch rejection when justified
- Channel interpolation when montage and review support it

Forbidden steps:

- Epoching around boundary, impedance, excluded, or segment-only markers
- Treating segment markers as condition triggers
- Overwriting raw input
- Skipping event semantics audit

Required figures:

- ERP waveform
- Topoplot
- PSD
- Optional ERP image/trial heatmap when the dataset and workflow support it

## Resting-State Spectral/Connectivity

Mode: `continuous`

Required steps:

1. Continuous-data suitability review
2. Filter and line-noise cleanup
3. Rereference
4. Spectral analysis
5. Save derivative
6. Protocol export
7. Final report

Conditional steps:

- Conservative clean_rawdata / ASR
- Sensor connectivity
- Channel interpolation when montage repair is needed

Forbidden steps:

- Epoching as a default branch step
- Baseline correction as if the data were event-locked
- Anatomical connectivity claims from sensor-level summaries
- Overwriting raw input

Required figures:

- PSD
- Optional connectivity matrix/network

## Time-Frequency

Mode: `event_locked`

Required steps:

1. Event semantics audit
2. Filter and line-noise cleanup
3. Epoch and baseline
4. Time-frequency analysis
5. Save derivative
6. Protocol export
7. Final report

Conditional steps:

- clean_rawdata / ASR when justified
- Rereference
- ICA, ICLabel, and component review when justified
- Channel interpolation when montage and review support it

Forbidden steps:

- Treating boundary/QC markers as triggers
- Skipping baseline
- Claiming time-frequency results from continuous data without epochs
- Overwriting raw input

Required figures:

- Time-frequency plot
- Optional topoplot and PSD for time-window or frequency-window context

## Source Localization

Mode: `model_based`

Required steps:

1. Channel-location review or repair
2. DIPFIT plugin check
3. Source-model settings
4. Source localization
5. Save derivative
6. Protocol export
7. Final report

Conditional steps:

- ICA and component review
- Topoplot or component plots for review support

Forbidden steps:

- Source claims without channel locations
- Anatomical certainty claims
- Skipping DIPFIT resources
- Overwriting raw input

Required figures:

- ICA/component figure
- Optional topoplot for component localization review

## STUDY / Group Analysis

Mode: `group`

Required steps:

1. Project plan
2. BIDS/STUDY plugin check
3. Single-subject protocol lock
4. Staged STUDY preflight
5. STUDY create
6. STUDY design
7. STUDY statistics
8. Save derivative
9. Protocol export
10. Final report

Conditional steps:

- STUDY precompute when measures are claimed
- ICA clustering when explicitly claimed
- LIMO or SIFT plugin checks when those paths are used

Forbidden steps:

- Direct group statistics before locking single-subject preprocessing
- Skipping design variables
- Claiming precompute or clustering without evidence
- Overwriting raw input

Required figures:

- ERP figure
- Optional PSD, time-frequency, connectivity, and component review figures when the measure family supports them

## Branch Completeness Record

Each protocol or final report should record:

- branch ID and branch mode
- universal preamble steps completed
- ordered branch steps completed
- missing required steps
- blocked or forbidden steps encountered
- required figures and figure paths
- required outputs and output paths
- branch notes and remaining limitations
