# Official EEGLAB Method Map

This map connects MCP methods to official EEGLAB/SCCN references. It is a local index for agent routing and `eeglab_method_preflight`. For the full official topic index and support_level taxonomy, read `eeglab://official/topic-index.md` and `eeglab://official/support-matrix.md`.

## Function Model

- Claim `EEGLAB-FUNC-001`: EEGLAB distinguishes user-facing `pop_` functions, lower-level processing functions, and dataset consistency checks.
- MCP rule: tool descriptions and protocols must name the relevant EEGLAB function family when possible and avoid pretending custom defaults are official defaults.

## Method Profiles

| Method profile | MCP tools | Official claim IDs | Required gate theme |
| --- | --- | --- | --- |
| `epoch` | `eeglab_epoch`, `eeglab_erp_light_workflow` | `EEGLAB-EVENT-001`, `EEGLAB-STRUCT-001` | confirmed condition triggers, no boundary/QC/segment epoching |
| `timefreq` | `eeglab_timefreq`, `eeglab_plot_timefreq` | `EEGLAB-TF-001`, `EEGLAB-EVENT-001` | event locking, baseline, cycles/frequency settings |
| `clean_rawdata` | `eeglab_clean_rawdata` | `EEGLAB-ASR-001` | continuous data, plugin availability, thresholds, derivative output |
| `run_ica` | `eeglab_run_ica` | `EEGLAB-ICA-001` | continuous data suitability, rank/reference review, bad-channel policy |
| `iclabel` | `eeglab_classify_ica`, `eeglab_flag_components` | `EEGLAB-ICLABEL-001` | ICA exists, ICLabel available |
| `remove_components` | `eeglab_remove_components` | `EEGLAB-ICLABEL-001` | ICA exists, component review, derivative output |
| `source` | `eeglab_source_settings`, `eeglab_source_localization` | `EEGLAB-DIPFIT-001` | ICA/source model, channel locations, DIPFIT, head model/template |
| `bids_import` | `eeglab_import_bids` | `EEGLAB-BIDS-001`, `EEGLAB-IMPORT-001`, `BIDS-EEG-001`, `BIDS-EVENTS-001` | BIDS root/sidecars, EEG-BIDS plugin, event timing metadata |
| `bids_export` | guidance-only | `EEGLAB-BIDSEXPORT-001`, `EEGLAB-BIDS-001`, `BIDS-EEG-001`, `BIDS-EVENTS-001` | EEG-BIDS export functions, complete sidecars, events metadata, derivative output |
| `import_plugins` | guidance-only/import-readiness | `EEGLAB-IMPORT-PLUGINS-001`, `EEGLAB-IMPORT-001`, `EEGLAB-MFF-001`, `EEGLAB-NWB-001`, `EEGLAB-BVA-001` | source format, importer/plugin availability, event/channel mapping, raw preservation |
| `data_export` | guidance-only except EEGLAB `.set` save | `EEGLAB-EXPORT-001`, `EEGLAB-MFF-001`, `EEGLAB-NWB-001`, `EEGLAB-BVA-001` | target format support, derivative output, export metadata completeness, software/plugin provenance |
| `hed_event_annotation` | guidance-only/event-metadata evidence | `EEGLAB-HED-001`, `BIDS-EVENTS-001` | event descriptions, HED schema/version, validated condition-code map before event-locked interpretation |
| `history_scripting` | guidance-only/protocol recovery | `EEGLAB-HISTORY-001`, `EEGLAB-FUNC-001`, `EEGLAB-PIPELINE-001` | EEG.history availability, script review, parameters, derivative outputs |
| `event_script_modification` | guidance-only | `EEGLAB-EVENTSCRIPT-001`, `EEGLAB-STRUCT-001`, `EEGLAB-EVENT-001` | event recode/deletion/latency rules, latency units, urevent preservation/relinking, semantic validation |
| `study_create` | `eeglab_study_create` | `EEGLAB-BIDS-001`, `EEGLAB-STUDY-001`, `EEGLAB-COURSE-001` | BIDS or multi-subject layout; protocol lock is advisory until statistics |
| `study_design` | `eeglab_study_design` | `EEGLAB-STUDY-001`, `EEGLAB-COURSE-001` | BIDS/multi-subject layout, design variables and levels |
| `study_statistics` | `eeglab_study_statistics` | `EEGLAB-STUDY-001`, `EEGLAB-COURSE-001` | locked single-subject protocol, design variables, measure, alpha/correction |
| `study_precompute` | guidance-only | `EEGLAB-STUDY-PRECOMP-001`, `EEGLAB-STUDY-001` | STUDY design, locked protocol, measure family, derivative precompute output |
| `ica_clustering` | guidance-only | `EEGLAB-ICCLUSTER-001`, `EEGLAB-STUDY-PRECOMP-001`, `EEGLAB-ICA-001` | subject ICA, clustering features/policy, measure records, review criteria |
| `study` | planning/ready-check alias | `EEGLAB-BIDS-001`, `EEGLAB-STUDY-001`, `EEGLAB-COURSE-001` | combined readiness for BIDS/STUDY/group analysis |
| `derivative_processing` | filtering, resampling, rereference, line-noise cleanup, epoch rejection | `EEGLAB-FILT-001`, `EEGLAB-FUNC-001` | raw preservation, derivative output, parameter record |
| `acquisition_provenance` | guidance through planning/QC/reporting | `EEGLAB-IMPORT-001`, `EEGLAB-STRUCT-001`, `BIDS-EEG-001` | raw preservation, derivative output, reference/montage, power-line frequency, acquisition filters |
| `bids_metadata` | guidance through planning/reporting | `EEGLAB-BIDS-001`, `EEGLAB-IMPORT-001`, `BIDS-EEG-001`, `BIDS-EVENTS-001` | BIDS EEG sidecars, events.tsv onset/duration, events.json column descriptions, HED or validated event-code map |
| `channel_locations` | `eeglab_edit_channels`, `eeglab_interpolate_channels` | `EEGLAB-CHANLOC-001` | usable channel locations or concrete repair/interpolation plan |
| `line_noise` | `eeglab_clean_line_noise` | `EEGLAB-LINE-001`, `EEGLAB-FILT-001` | local line frequency, cleanup method, derivative output |
| `spectral` | `eeglab_spectral` | `EEGLAB-SPECTRAL-001` | frequency range, artifact policy, channel/ROI record |
| `connectivity` | `eeglab_connectivity` | `EEGLAB-SPECTRAL-001`, `EEGLAB-SIFT-001` | method/frequency range, artifact policy, sensor/source limits |
| `topography` | `eeglab_topoplot` | `EEGLAB-TOPO-001`, `EEGLAB-CHANLOC-001` | channel locations and plotted time/frequency window |
| `limo_statistics` | guidance-only | `EEGLAB-LIMO-001`, `EEGLAB-STUDY-001` | LIMO plugin, model/design matrix, correction policy |
| `amica_ica` | guidance-only | `EEGLAB-AMICA-001`, `EEGLAB-ICA-001`, `EEGLAB-PLUGIN-001` | AMICA plugin, continuous data, rank/PCA/reference review, compute strategy, derivative output |
| `sift_connectivity` | guidance-only | `EEGLAB-SIFT-001` | SIFT plugin, MVAR/source model validation, correction policy |
| `nsg_remote` | guidance-only/out-of-local-scope | `EEGLAB-NSG-001`, `EEGLAB-PLUGIN-001`, `EEGLAB-COURSE-001` | NSG plugin, remote-compute approval, upload/credential policy, job provenance |
| `pipeline` | `eeglab_pipeline` | `EEGLAB-ASR-001`, `EEGLAB-ICA-001`, `EEGLAB-EVENT-001` | raw preservation, derivative output, explicit default acceptance |

## Agent Rule

Before calling a high-risk tool, call `eeglab_method_preflight` or pass enough `method_context` for automatic gate checks. If gate status is `blocked`, ask for missing facts or require explicit `override_gate=true` with `override_reason`.
