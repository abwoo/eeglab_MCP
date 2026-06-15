# ICA And ICLabel Policy

ICA and ICLabel are high-risk because they can change artifact interpretation and downstream data.

## Before ICA

Run `eeglab_method_preflight` with method `run_ica`. The context should include:

- `data_shape` or `has_continuous_raw`
- `rank_reference_reviewed`
- `bad_channel_policy_defined`
- planned derivative output

Do not run ICA casually on epoched-only data or after unresolved rank/reference changes.

## Before ICLabel Or Removal

Run `eeglab_plugin_check` for ICLabel, then `eeglab_method_preflight` for `iclabel` or `remove_components`.

Required context:

- `has_ica`
- `plugin_iclabel_available` or `plugins_available`
- `component_reviewed` for removal
- `derivative_output_planned` for removal

Use ICLabel as decision support. Never present probabilities as automatic proof, and never hide component removal thresholds or rationale.
