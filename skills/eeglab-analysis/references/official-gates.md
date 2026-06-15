# Official EEGLAB Gate Reference

Use this reference whenever a workflow reaches high-risk processing. It mirrors MCP resources `eeglab://official/method-map.md`, `eeglab://official/gate-policy.md`, and `eeglab://official/plugin-map.md`.

## Required Tool Pattern

1. Gather context from `quick_qc`, user goal, event semantics, plugin checks, montage status, and output path.
2. Call `eeglab_method_preflight` or pass `method_context` to the high-risk tool.
3. If `gate_status=blocked`, stop. Ask for missing facts or an explicit override.
4. If override is approved, call the tool with `override_gate=true`, `override_reason`, and `method_context`.
5. Report gate status, source claim IDs, missing requirements, override status, exact parameters, output path, and limitations.

## Method Gates

- `epoch`: needs confirmed condition events and must not use boundary, impedance, excluded, or segment-only markers.
- `timefreq`: needs event locking or justified design, baseline, and frequency/cycle settings.
- `clean_rawdata`: needs continuous-data suitability, plugin availability, thresholds, and derivative output.
- `run_ica`: needs continuous-data suitability, rank/reference review, and bad-channel policy.
- `iclabel`: needs ICA weights and ICLabel availability.
- `remove_components`: needs ICA weights, component review/threshold rationale, and derivative output.
- `source`: needs ICA/source model, channel locations, DIPFIT availability, and head model/template assumptions.
- `bids_import`: needs BIDS root/sidecars, EEG-BIDS import support, and event timing metadata review.
- `study_create`: needs BIDS/multi-subject structure; do not treat creation as statistics approval.
- `study_design`: needs BIDS/multi-subject structure plus design variables and levels.
- `study_statistics`: needs BIDS/multi-subject structure, locked single-subject preprocessing, design variables, measure, and alpha/correction.
- `study`: planning/ready-check alias for the combined BIDS/STUDY/group-analysis decision.
- `derivative_processing`: needs raw preservation, derivative output, and parameter record.
- `acquisition_provenance`: needs raw preservation, derivative output, reference/montage, power-line frequency, and acquisition-filter notes or explicit missing-metadata documentation.
- `bids_metadata`: needs BIDS EEG sidecars, events.tsv onset/duration, and events.json/HED/codebook descriptions for trial_type and other event columns.
- `pipeline`: needs raw preservation, derivative output, and explicit acceptance of bundled defaults.

## Override Language

If the user approves proceeding despite a blocked gate, the report must say:

```text
Official gate override used: yes
Override reason: <user-approved reason>
Blocked requirements acknowledged: <ids>
Source claim IDs: <claim ids>
Scientific limitation: results are exploratory/conditional because official preconditions were not fully met.
```

Never hide an override inside a normal success summary.
