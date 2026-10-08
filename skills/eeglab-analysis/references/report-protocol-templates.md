# Report And Protocol Templates

Use `eeglab_protocol_export` for durable protocol text. Prefer passing upstream
`gate_results`, `source_claim_ids`, `report_fields`, and override fields directly
from planning/preflight outputs so the protocol preserves the scientific gate
record instead of reconstructing it from prose.

## Recording Record

- Input path and output path
- Set name, file name, data shape, sampling rate, points/trials, duration
- Channel count, reference/montage, channel-location coverage
- Event labels/counts, event latency range, urevent links if available
- Comments/BIDS metadata, HED/events.json/codebook source, importer/exporter plugin path, and processing-history availability

## Parameter Record

- Tool sequence and exact parameters
- Filter cutoffs, line-noise settings, sample rate, rereference
- ASR thresholds, bad-channel policy, ICA algorithm/PCA rank
- ICLabel thresholds, component review/removal rationale
- Epoch/baseline/time/frequency windows, channel/ROI list
- Event-script modification rules, latency units, HED schema/version, and urevent preservation/relinking when used
- Output files and derivative-output policy
- External export format, metadata completeness, exporter plugin/function, and validation limits when used

## Official Gate Record

- `method_profile_id`
- `gate_status`
- `source_claim_ids`
- missing requirements and safe next step
- `override_used`, `override_reason`, `blocked_requirements_acknowledged`
- report field matrix coverage for recording/acquisition, events/design,
  preprocessing, analysis parameters, outputs/limits

If no `gate_results` are available, say gate coverage is not provided. Do not
pretend all official claim IDs apply to a protocol; list only explicit
`source_claim_ids` or those derived from the supplied gate results.

## Limitations

State that outputs are EEG signal-processing results, not clinical conclusions. Mention missing metadata, plugin limitations, incomplete montage/event semantics, and any override.
