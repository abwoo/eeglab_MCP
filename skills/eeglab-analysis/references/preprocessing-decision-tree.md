# Preprocessing Decision Tree

Choose the smallest justified preprocessing sequence. Preserve raw inputs and write derivatives to a new path.

## Conservative Order

1. `quick_qc`: `eeglab_init`, `eeglab_load_data`, `eeglab_qc_report`, `eeglab_info`, `eeglab_get_events`, `eeglab_history`.
2. Decide branch with `eeglab_project_plan` or `eeglab_workflow_recommend`.
3. For filtering/resampling/rereference/rejection, run `eeglab_method_preflight` with `derivative_processing` context: raw preserved, derivative output planned, parameters recorded.
4. For ASR, run `eeglab_plugin_check` and `eeglab_method_preflight` for `clean_rawdata`.
5. For ICA/ICLabel/component removal, follow `ica-iclabel-policy.md`.
6. Save named intermediate datasets before major destructive decisions.

## Required Parameter Records

Record filter cutoffs, line-noise frequency, sample rate, reference, ASR thresholds, bad-channel strategy, ICA algorithm/PCA rank, rejected components/epochs, output files, gate status, and `source_claim_ids`.
