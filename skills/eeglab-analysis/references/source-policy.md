# Source Localization Policy

Source localization is high-risk and must be treated as model-dependent signal processing, not anatomical certainty.

## Required Gate

Run `eeglab_method_preflight` with method `source` before `eeglab_source_settings` or `eeglab_source_localization`.

Required context:

- `has_ica` or an explicitly justified source model
- `has_channel_locations` or complete `channel_location_coverage`
- `plugin_dipfit_available` or `plugins_available`
- `head_model` and `template`

Run `eeglab_plugin_check` for DIPFIT when plugin state is unknown. If any critical requirement is missing, stop or require explicit override. Reports must include model/template settings, component list, residual variance if available, `source_claim_ids`, and limitations.
