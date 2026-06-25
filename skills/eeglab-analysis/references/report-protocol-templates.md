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
- `missing_requirements` and safe next step
- `override_used`, `override_reason`, `blocked_requirements_acknowledged`
- report field matrix coverage for recording/acquisition, events/design,
  preprocessing, analysis parameters, outputs/limits
- `branch_workflow` and `branch_completeness` payloads for the active analysis
  branch
- `figure_atlas` entries with figure type, status, branch, channel/ROI,
  latency/frequency window, tool source, official anchor, interpretation scope,
  and figure path when available
- tool coverage: called tools, expected tools, missing tools, and missing reasons
- reference coverage: skill references read, official docs read, and any missing files
- branch workflow coverage: `branch_id`, `branch_label`, `branch_mode`,
  `analysis_type`, `branch_variant`, `universal_preamble_steps`,
  `ordered_branch_steps`, `completed_steps`, `missing_required_steps`,
  `blocked_steps`, `required_figures`, `required_figure_families`,
  `conditional_figures`, `conditional_figure_families`,
  `guidance_only_figure_families`, `figure_atlas`, `figure_paths`,
  `required_outputs`, `output_paths`, and branch completeness status

If no `gate_results` are available, say gate coverage is not provided. Do not
pretend all official claim IDs apply to a protocol; list only explicit
`source_claim_ids` or those derived from the supplied gate results.

## Limitations

State that outputs are EEG signal-processing results, not clinical conclusions. Mention missing metadata, plugin limitations, incomplete montage/event semantics, and any override.

## Final Report Generation

Use `eeglab_generate_report` as the preferred final reporting tool when the MCP is available. Use bundled `scripts/generate_eeg_report.py` as a deterministic fallback:

```bash
python scripts/generate_eeg_report.py --input results.json --output report.md
python scripts/generate_eeg_report.py --input results.json --output report.html --format html
```

The input JSON should follow `scripts/report_template.json` and include `tool_coverage`, `reference_coverage`, `official_document_coverage`, `method_preflights`, `report_field_coverage`, and `source_claim_ids` in addition to recording, preprocessing, analysis, figures, results, limitations, plugins, and generated files.
