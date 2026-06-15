# Official EEGLAB Topic Index

This index is the project-local map of official EEGLAB/SCCN content to MCP support. It does not copy official documentation; it records the topic, official anchor, support level, claim IDs, and expected MCP route.

Support levels:

- `executable`: the MCP exposes a tool/workflow that can run after gates pass.
- `gated_guidance`: the MCP can guide or partially execute, but scientific interpretation is gated by prerequisites.
- `indexed_only`: the topic is indexed and checked, but no dedicated execution workflow is promised.
- `out_of_scope`: the topic is relevant context but outside MCP execution.

| Topic | Support level | Official anchor | Claim IDs | MCP route |
| --- | --- | --- | --- | --- |
| EEGLAB function model | `executable` | EEGLAB function guide | `EEGLAB-FUNC-001` | tool descriptions, registry metadata, protocols |
| Data structures and provenance | `executable` | Concepts guide data structures | `EEGLAB-STRUCT-001` | `eeglab_info`, `eeglab_get_events`, `eeglab_history`, `eeglab_qc_report` |
| Import and BIDS | `executable` | Import tutorials, BIDS scripting tutorial, and BIDS EEG/events metadata | `EEGLAB-IMPORT-001`, `EEGLAB-BIDS-001`, `BIDS-EEG-001`, `BIDS-EVENTS-001` | `eeglab_load_data`, `eeglab_import_bids`, BIDS/STUDY gates |
| Plugin-dependent import formats | `gated_guidance` | Import tutorial plus MFF/NWB/BVA plugin pages | `EEGLAB-IMPORT-PLUGINS-001`, `EEGLAB-MFF-001`, `EEGLAB-NWB-001`, `EEGLAB-BVA-001` | `eeglab_plugin_check`, `eeglab_method_preflight`, planning/reporting; no blanket import guarantee |
| BIDS export and derivatives | `indexed_only` | EEG-BIDS export plugin and BIDS EEG/events metadata | `EEGLAB-BIDSEXPORT-001`, `EEGLAB-BIDS-001`, `BIDS-EEG-001`, `BIDS-EVENTS-001` | planning, plugin check, protocol export; no default export execution tool |
| External data export formats | `indexed_only` | Exporting data tutorial plus MFF/NWB/BVA plugin pages | `EEGLAB-EXPORT-001`, `EEGLAB-MFF-001`, `EEGLAB-NWB-001`, `EEGLAB-BVA-001` | `.set` save is executable; BIDS/MFF/NWB/BrainVision export remains guidance-only until dedicated tools exist |
| HED event annotation | `gated_guidance` | HEDTools and BIDS events metadata | `EEGLAB-HED-001`, `BIDS-EVENTS-001` | event metadata evidence through HED/events.json/codebook; still requires condition-trigger validation for ERP/ERSP |
| History and batch scripting | `gated_guidance` | EEGLAB history scripting tutorial | `EEGLAB-HISTORY-001`, `EEGLAB-FUNC-001`, `EEGLAB-PIPELINE-001` | `eeglab_history`, preflight, protocol export; history-derived scripts must be reviewed before batch use |
| Event-script modification | `indexed_only` | EEGLAB event-processing command-line tutorial | `EEGLAB-EVENTSCRIPT-001`, `EEGLAB-STRUCT-001`, `EEGLAB-EVENT-001` | plan/gate/report event recoding or latency changes; no generic event-mutation execution tool |
| Channel locations | `gated_guidance` | Channel locations tutorial | `EEGLAB-CHANLOC-001` | `eeglab_edit_channels`, `eeglab_interpolate_channels`, topography/source gates |
| Filtering, resampling, rereferencing | `executable` | Preprocess tutorials | `EEGLAB-FILT-001`, `EEGLAB-RESAMPLE-001`, `EEGLAB-REREF-001` | derivative-processing gate plus low-level tools |
| Line-noise cleanup | `gated_guidance` | CleanLine/Zapline plugin anchors | `EEGLAB-LINE-001` | `eeglab_clean_line_noise`, plugin check, report limits |
| clean_rawdata and ASR | `executable` | clean_rawdata plugin | `EEGLAB-ASR-001` | `eeglab_clean_rawdata`, `eeglab_pipeline` |
| Artifact and epoch rejection | `gated_guidance` | artifact rejection tutorials | `EEGLAB-REJECT-001` | channel selection, interpolation, epoch rejection |
| ICA and ICLabel | `executable` | RunICA tutorial and ICLabel repo | `EEGLAB-ICA-001`, `EEGLAB-ICLABEL-001` | `eeglab_run_ica`, `eeglab_classify_ica`, `eeglab_flag_components`, `eeglab_remove_components` |
| Epochs and ERP | `executable` | epoch extraction and data averaging tutorials | `EEGLAB-EVENT-001`, `EEGLAB-EPOCH-001`, `EEGLAB-ERP-001` | event audit, epoch gate, ERP tools |
| Spectra, ERSP/ITC, connectivity | `gated_guidance` | spectra/maps and time-frequency tutorials | `EEGLAB-SPECTRAL-001`, `EEGLAB-TF-001` | spectral/timefreq/connectivity tools with parameter and artifact-policy gates |
| Visualization and topography | `gated_guidance` | spectra/maps/topoplot tutorials | `EEGLAB-TOPO-001`, `EEGLAB-CHANLOC-001` | plot tools, channel-location gate |
| Source localization and DIPFIT | `gated_guidance` | source tutorial and DIPFIT plugin | `EEGLAB-DIPFIT-001`, `EEGLAB-CHANLOC-001` | `eeglab_source_settings`, `eeglab_source_localization` |
| STUDY and group analysis | `gated_guidance` | group-analysis tutorials | `EEGLAB-STUDY-001`, `EEGLAB-BIDS-001` | STUDY create/design/statistics after protocol gates |
| STUDY precompute and ICA clustering | `indexed_only` | STUDY visualization and component clustering tutorials | `EEGLAB-STUDY-PRECOMP-001`, `EEGLAB-ICCLUSTER-001`, `EEGLAB-STUDY-001` | preflight/planning/report guidance only until dedicated execution tools exist |
| LIMO statistics | `indexed_only` | LIMO plugin | `EEGLAB-LIMO-001`, `EEGLAB-STUDY-001` | planning, plugin check, report guidance only |
| SIFT and groupSIFT | `indexed_only` | SIFT/groupSIFT plugin pages | `EEGLAB-SIFT-001` | planning, plugin check, model-validation guidance only |
| NFT, NSGportal, AMICA, Picard, advanced plugins | `indexed_only` | EEGLAB plugin index and course | `EEGLAB-PLUGIN-001`, `EEGLAB-COURSE-001`, `EEGLAB-AMICA-001`, `EEGLAB-NSG-001` | plugin matrix, no default execution promise |
| BIDS/HED reporting | `gated_guidance` | BIDS import/tutorial material plus BIDS EEG/events metadata | `EEGLAB-BIDS-001`, `EEGLAB-COURSE-001`, `BIDS-EEG-001`, `BIDS-EVENTS-001` | report field matrix, sidecar/event-code gates |
| Acquisition hardware and lab notebook facts | `out_of_scope` | EEGLAB tutorial context plus BIDS EEG metadata | `BIDS-EEG-001` for documentation only | audit imported metadata only; use `acquisition_metadata` preflight for analysis-ready provenance |

Default rule: unsupported official plugins are still indexed. They must be explained as `indexed_only` or `gated_guidance`, not silently treated as executable.
