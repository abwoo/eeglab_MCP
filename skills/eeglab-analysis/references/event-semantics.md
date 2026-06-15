# Event Semantics

Use this reference before ERP, epoching, ERSP/ITC, or any event-locked claim.

## Required Steps

1. Inspect event labels and counts with `eeglab_get_events`.
2. Classify labels with `eeglab_event_semantics_audit`.
3. Treat only confirmed condition/task triggers as analysis events.
4. Run `eeglab_method_preflight` for `epoch` or `timefreq` before event-locked tools.
5. If HED tags, events.json, or a lab codebook are used, run `hed_event_annotation` preflight before treating them as condition evidence.
6. If events will be recoded, deleted, latency-shifted, or relinked, run `event_script_modification` preflight and report urevent status.

## Marker Roles

- `condition` or `trigger`: can be used for epoching after counts/latencies are checked.
- `candidate_trigger`: ask the user or behavioral log to confirm before scientific claims.
- `boundary`, `impedance`, `qc_annotation`, `excluded`, `segment_marker`: do not use as ERP/time-frequency triggers.

For segment-only data, use `segment_qc`: report segment durations or block structure, and request a behavioral/event-code map before condition-level ERP/ERSP claims.

HED tags and event-code maps support provenance, not automatic epoching. They must still identify condition triggers, and scripted event edits must record modification rules, latency units, and `urevent` preservation or relinking.
