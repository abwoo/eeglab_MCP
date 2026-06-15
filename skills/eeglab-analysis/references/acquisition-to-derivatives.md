# EEGLAB Acquisition To Derivatives

Use this reference when planning or reporting what happened between acquisition,
raw EEG files, and EEGLAB derivatives.

## Raw Preservation

- Treat original EEG recordings and sidecars as read-only.
- Write filtered, cleaned, epoched, ICA-cleaned, source, STUDY, and report
  outputs into a derivative directory.
- Record absolute input and output paths in protocols and reports.

## Acquisition Metadata

Before destructive processing, record or report gaps for:

- acquisition system and task description
- sampling rate and recording duration
- online reference, ground, montage, and cap layout
- hardware and software filters
- power-line frequency
- channel locations, electrodes, and coordinate system
- impedance or channel-quality notes when available
- event-code map, behavioral log, and run/block conventions

Use `eeglab_method_preflight` with `method="acquisition_metadata"` when these
facts are incomplete. Critical context fields include `raw_input_preserved`,
`derivative_output_planned`, `reference` or `montage`, `power_line_frequency`,
and `acquisition_filters`. If a fact cannot be recovered, add it to
`documented_missing_fields` so the report records the gap instead of silently
inventing metadata.

## BIDS-Compatible Records

Prefer BIDS-style evidence when available:

- `*_eeg.json` for sampling, filters, reference, power-line frequency, task, and
  recording metadata
- `*_events.tsv` plus `*_events.json` for onset, duration, trial type, and
  column descriptions
- `*_channels.tsv` for channel type/status and bad-channel notes
- `*_electrodes.tsv` and `*_coordsystem.json` for sensor coordinates

Use `eeglab_method_preflight` with `method="bids_metadata"` before relying on a
BIDS event table for condition semantics. Provide `sidecars` or explicit
`eeg_json`, `channels_tsv`, `electrodes_tsv`, `coordsystem_json`,
`events_tsv_columns`, and `events_json`/`event_code_map`/`hed_tags`.

Missing metadata is not fatal for QC, but it blocks analysis-ready claims that
depend on the missing facts.
