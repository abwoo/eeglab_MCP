# Official Method Map

Use this reference to route an EEG request to an official-gated MCP method profile. The canonical executable map is in `eeglab_mcp_server/official_alignment.py`; MCP clients can also read `eeglab://official/method-map.md`, `eeglab://official/topic-index.md`, and `eeglab://official/support-matrix.md`.

| Profile | Tools | Required preflight focus |
| --- | --- | --- |
| `epoch` | `eeglab_epoch`, `eeglab_erp_light_workflow` | confirmed condition triggers; no boundary/QC/segment-only epoching |
| `timefreq` | `eeglab_timefreq`, `eeglab_plot_timefreq` | event locking, baseline, frequency range, cycles |
| `clean_rawdata` | `eeglab_clean_rawdata` | continuous data, clean_rawdata plugin, thresholds, derivative output |
| `run_ica` | `eeglab_run_ica` | continuous-data suitability, rank/reference review, bad-channel policy |
| `iclabel` | `eeglab_classify_ica`, `eeglab_flag_components` | ICA weights, ICLabel plugin |
| `remove_components` | `eeglab_remove_components` | ICA weights, component review, derivative output |
| `source` | `eeglab_source_settings`, `eeglab_source_localization` | ICA/source model, channel locations, DIPFIT, head model/template |
| `bids_import` | `eeglab_import_bids` | BIDS root/sidecars, EEG-BIDS import support, event timing metadata |
| `bids_export` | guidance-only | EEG-BIDS export support, complete sidecars, event descriptions, derivative export directory, software/plugin provenance |
| `import_plugins` | guidance-only/import-readiness | source format, importer/plugin availability, event/channel mapping, raw preservation |
| `data_export` | guidance-only except EEGLAB `.set` save | export format support, derivative output, metadata completeness, software/plugin provenance |
| `hed_event_annotation` | guidance-only/event-metadata evidence | event descriptions, HED schema/version, validated code map before event-locked claims |
| `history_scripting` | guidance-only/protocol recovery | EEG.history availability, history-derived script review, explicit parameters, derivative output policy |
| `event_script_modification` | guidance-only | event modification rules, latency units, urevent preservation/relinking, semantic evidence |
| `study_create` | `eeglab_study_create` | BIDS/multi-subject structure; protocol lock remains advisory until statistics |
| `study_design` | `eeglab_study_design` | BIDS/multi-subject structure, design variables and levels |
| `study_statistics` | `eeglab_study_statistics` | locked protocol, design variables, measure, alpha/correction |
| `study_precompute` | guidance-only | locked single-subject protocol, STUDY measure family, precompute parameters, derivative output |
| `ica_clustering` | guidance-only | subject ICA, STUDY measures, clustering features/algorithm, outlier policy, review criteria |
| `study` | planning/ready-check alias | combined BIDS/STUDY/group-analysis readiness |
| `derivative_processing` | `eeglab_filter`, `eeglab_resample`, `eeglab_reref`, `eeglab_reject_epochs`, `eeglab_clean_line_noise` | raw preservation, derivative output, parameter record |
| `acquisition_provenance` | planning/QC/reporting guidance | raw preservation, derivative output, reference/montage, power-line frequency, acquisition filters |
| `bids_metadata` | planning/reporting guidance | BIDS EEG sidecars, events.tsv onset/duration, events.json trial_type/additional-column descriptions, HED tags, or validated event-code map |
| `channel_locations` | `eeglab_edit_channels`, `eeglab_interpolate_channels` | usable channel locations or concrete repair/interpolation plan |
| `line_noise` | `eeglab_clean_line_noise` | local line frequency, method parameters, derivative output |
| `spectral` | `eeglab_spectral` | frequency range, artifact policy, channels/ROIs |
| `connectivity` | `eeglab_connectivity` | method, frequency range, artifact policy, sensor/source limits |
| `topography` | `eeglab_topoplot` | channel locations and plotted time/frequency window |
| `limo_statistics` | guidance-only | LIMO plugin, first/second-level model, design, contrasts, correction |
| `amica_ica` | guidance-only | AMICA plugin, continuous data, rank/PCA/reference review, compute strategy, derivative output |
| `sift_connectivity` | guidance-only | SIFT plugin, model order, stationarity, validation, correction |
| `nsg_remote` | guidance-only/out-of-local-scope | NSG plugin, user approval, credentials/upload policy, remote job provenance |
| `plugin_development` | guidance-only/contribution planning | plugin goal, EEGLAB function family, GUI/command-line boundary, validation plan |
| `relica_reliability` | guidance-only | RELICA plugin, existing ICA, bootstrap settings, component review |
| `viewprops_review` | guidance-only | Viewprops plugin, existing ICA, reviewed component set and classifier/source evidence |
| `get_chanlocs_digitization` | guidance-only | get_chanlocs plugin, head image/digitization source, fiducials, channel-location repair plan |
| `roiconnect_source_connectivity` | guidance-only | ROIconnect plugin, source model, ROI atlas, connectivity metric and interpretation limits |
| `eegstats_metrics` | guidance-only | EEGstats plugin, band/frequency settings, channels/ROIs or STUDY scope, artifact policy |
| `pipeline` | `eeglab_pipeline` | raw preservation, derivative output, explicit default acceptance |

Always preserve `method_profile_id`, `source_claim_ids`, gate status, and override status in the report/protocol.
