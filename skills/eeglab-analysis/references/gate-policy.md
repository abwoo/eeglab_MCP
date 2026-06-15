# Gate Policy

High-risk EEG methods use hard gates by default. Call `eeglab_method_preflight` before the tool, or pass `method_context` directly to a high-risk tool so the MCP can run the same official gate.

## Status Handling

- `pass`: continue and report `source_claim_ids`.
- `advisory`: continue only after recording the advisory gaps.
- `blocked`: stop; ask for missing facts or prerequisites.
- `override_accepted`: continue only because the user gave an explicit override reason.
- `unknown_method`: do not treat the method as officially aligned until it is mapped.

## Override Requirements

Use override only when the user explicitly accepts the risk:

```json
{
  "override_gate": true,
  "override_reason": "User-approved reason",
  "method_context": {}
}
```

Every override report must include `override_used`, `override_reason`, `blocked_requirements_acknowledged`, `source_claim_ids`, and the limitation that results are exploratory or conditional.

## Provenance And BIDS Gates

- Run `eeglab_method_preflight` with `method="acquisition_metadata"` before treating an imported dataset as analysis-ready when acquisition facts are incomplete.
- Run `eeglab_method_preflight` with `method="bids_metadata"` before relying on BIDS events or sidecars for condition-level interpretation.
- Missing acquisition facts may be documented as unavailable for QC/reporting, but downstream analysis gates still decide whether the missing fact blocks a method.
