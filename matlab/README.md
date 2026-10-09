# MATLAB Tool Interface

This is the execution implementation of EEGLAB MCP. MathWorks' [MATLAB MCP Server](https://github.com/matlab/matlab-mcp-server) loads `eeglab-mcp-tools.json` and calls the MATLAB functions in this directory. The transport runs on a GitHub runner and uses a cloud MATLAB session; no desktop client configuration is supplied.

## Argument Convention

`eeglab_init` accepts the scalar `eeglab_path`; `eeglab_load_data` accepts `filepath`. Information, events, history, QC and official-claims tools take no arguments. Other tools accept one required `options` string encoding a JSON object. Use `"{}"` for defaults; selections and `method_context` go inside that object. MathWorks supports scalar argument types only.

A tool call such as `eeglab_filter` receives:

```json
{"options":"{\"filter_type\":\"bandpass\",\"low_cutoff\":1,\"high_cutoff\":40,\"method_context\":{\"raw_input_preserved\":true,\"derivative_output_planned\":true}}"}
```

Functions print one JSON result, captured by the official MCP server. EEGLAB globals hold the current EEG/STUDY in the shared MATLAB session. Errors return `status`, `code`, `error` and `next_step`. Method preflight and research workflows also report gate provenance and limitations.

## Research Workflows

- `eeglab_workflow_recommend` and `eeglab_project_plan` start with QC when facts are unknown; markers need explicit confirmation before ERP/time-frequency claims.
- `eeglab_method_preflight` evaluates all 39 profiles without changing EEG.
- `eeglab_event_semantics_audit` preserves explicit exclusions and keeps QC/boundary/impedance markers out of confirmed conditions.
- `eeglab_plugin_check` reports function availability without promoting indexed plugins to execution support.
- `eeglab_protocol_export` records gates, overrides, missing requirements and report fields in JSON/Markdown cloud artifacts.
- `eeglab_erp_light_workflow` loads, filters, epochs, summarizes and saves a derivative. Channels and triggers are explicit.
- `eeglab_pipeline` composes gated ERP/resting/time-frequency tools. Filter and average reference are the recorded defaults; ASR/ICA are opt-in. Every child gate applies and component removal remains a separate reviewed tool.
- `eeglab_official_claims` returns the versioned 47-claim source map.

## STUDY

`eeglab_study_create` accepts either `dataset_paths` with optional matching `subjects` and `conditions`, or `bids_path`. It does not resave raw datasets. `eeglab_study_design` takes explicit `variable_name`, `variable_values` and `paired`. Statistics require a locked protocol, a defined design and precomputed channel measures, produced with the official `std_precomp` function.

`eeglab_study_statistics` reads ERP, spectrum or ERSP measures and runs `statcond` with the design's pairing. It applies FDR, Bonferroni or no correction to the complete returned p-value family. Cluster inference is outside this tool and requires a separately validated model.

## Validation

GitHub CI runs the option/error regressions, frozen requirement/preflight cases for every profile, EEGLAB sample-data processing tests, derivative workflows and real paired STUDY statistics. It then calls the same functions over MathWorks' official MCP server. The test harness is transport scaffolding; all EEG analysis and method gates are MATLAB.
