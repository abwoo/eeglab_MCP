# Official Gate Policy

The EEGLAB MCP uses hard gates with explicit override for high-risk EEG processing. Gates are derived from official EEGLAB/SCCN documentation and plugin repositories, then encoded in `official_alignment.py`.

## Gate Status

- `pass`: critical requirements are satisfied.
- `advisory`: advisory-mode preflight found gaps, or hard-mode preflight found only non-critical documentation gaps. Execution still requires critical gaps to be resolved or explicitly overridden.
- `blocked`: one or more critical official requirements are missing.
- `override_accepted`: blocked requirements exist, but the user supplied `override_gate=true` and an explicit `override_reason`.
- `unknown_method`: the method is not mapped to the official claim map.

## High-Risk Methods

- ERP/epoch/time-frequency: block if no confirmed condition trigger remains or if only boundary, impedance, excluded, or segment-only markers are available.
- clean_rawdata/ASR: block if data are epoched-only, plugin availability is unknown/missing, thresholds are missing, or no derivative-output strategy is present.
- ICA/ICLabel/component removal: block if continuous-data suitability, rank/reference review, bad-channel policy, ICA weights, ICLabel availability, component review, or derivative output are missing as applicable.
- source/DIPFIT: block if ICA/source model, channel locations, DIPFIT availability, or head model/template assumptions are missing.
- BIDS/STUDY/group statistics: block if project structure, single-subject preprocessing protocol, or design variables are missing.
- Acquisition/provenance: block analysis-ready claims if raw input preservation, derivative output policy, reference/montage, power-line frequency, or acquisition-filter notes are missing and not explicitly documented as unavailable.
- BIDS metadata: block BIDS-ready/event-semantics claims if EEG sidecars are incomplete, events.tsv lacks onset/duration, or trial_type/additional event columns lack events.json/HED/codebook descriptions.
- Channel-location repair/topography: allow edit/interpolation tools only with existing coordinates or a concrete repair plan; block topography/source interpretation when usable coordinates are missing.
- Spectral/connectivity: block or warn when frequency range, artifact policy, channel/ROI selection, or sensor/source interpretation limits are missing.
- LIMO/SIFT: guidance-only unless plugin availability, design/model, validation, and correction policy are explicit.
- one-click pipeline: block unless raw preservation, derivative output, and explicit default acceptance are present.

## Override Rule

An override is allowed only when the user explicitly accepts the risk. The MCP call must include:

- `override_gate: true`
- `override_reason: "<specific reason>"`

The result must record `override_used`, `override_reason`, and `blocked_requirements_acknowledged`. The skill must report that the workflow proceeded under override and list the blocked official requirements.

## Reporting Rule

Every high-risk output or protocol should include:

- official method profile ID
- source claim IDs
- gate status
- missing requirements
- override status
- exact tool parameters
- derivative output path
- limitations
