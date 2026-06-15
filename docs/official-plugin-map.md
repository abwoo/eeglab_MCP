# Official Plugin Map

This map defines plugin-sensitive EEGLAB workflows for MCP preflight and skill routing. It is also the MCP plugin matrix: every entry has a `support_level`, function probes, claim IDs, dependent method profiles, official URL, and next step when missing.

Support levels:

- `executable`: a dedicated MCP tool exists, but official gates still apply.
- `gated_guidance`: the MCP can guide or partially execute only with prerequisites.
- `indexed_only`: indexed and checkable, but no dedicated execution workflow is promised.

## clean_rawdata

- Official source: https://eeglab.org/plugins/clean_rawdata/
- Support level: `executable`
- MCP tools: `eeglab_clean_rawdata`, `eeglab_pipeline`
- Function probes: `pop_clean_rawdata`, `clean_rawdata`, `clean_artifacts`
- Gate: plugin available, continuous-data suitability, thresholds recorded, derivative output planned.

## ICLabel

- Official source: https://github.com/sccn/ICLabel
- Support level: `executable`
- MCP tools: `eeglab_classify_ica`, `eeglab_flag_components`, `eeglab_remove_components`
- Function probes: `pop_iclabel`, `iclabel`, `pop_icflag`
- Gate: ICA weights exist, plugin available, component review policy recorded.

## DIPFIT

- Official source: https://eeglab.org/plugins/dipfit/
- Support level: `executable`
- MCP tools: `eeglab_source_settings`, `eeglab_source_localization`
- Function probes: `pop_dipfit_settings`, `pop_multifit`, `dipfitdefs`
- Gate: ICA/source model, channel locations, DIPFIT resources, head model/template assumptions.

## EEG-BIDS / STUDY

- Official source: https://eeglab.org/plugins/EEG-BIDS/
- Support level: `executable`
- MCP tools: `eeglab_import_bids`, `eeglab_study_create`, `eeglab_study_design`, `eeglab_study_statistics`
- Function probes: `pop_importbids`, `pop_exportbids`, `bids_export`
- Gate: BIDS/multi-subject structure, sidecar/event metadata, single-subject preprocessing protocol, design variables, measure precompute state, alpha/correction policy.
- BIDS export profile: `bids_export` is indexed/guidance-only unless a dedicated export execution tool is added; it requires EEG-BIDS export support, complete sidecars, event metadata, derivative output, and software/plugin provenance.
- STUDY precompute and ICA clustering profiles: `study_precompute` and `ica_clustering` are indexed/guidance-only until dedicated execution tools exist; they require locked single-subject protocol, measure records, clustering policy, and review criteria.

## Import / Export / Event-Metadata Plugins

- `BIOSIG`: `gated_guidance`; probes `pop_biosig`, `sopen`, `biosig`; profile `import_plugins`; requires source format, plugin availability, event/channel mapping, and raw preservation for EDF/BDF/GDF-style imports.
- `File-IO`: `indexed_only`; probes `pop_fileio`, `ft_read_header`, `ft_read_data`, `ft_read_event`; profile `import_plugins`; use as guidance until File-IO availability and mapping policy are explicit.
- `MFF-matlab-io`: `indexed_only`; probes `mff_import`, `mff_export`, `pop_mffimport`; profiles `import_plugins` and `data_export`; requires MFF metadata mapping and derivative output policy.
- `NWB-io`: `indexed_only`; probes `nwb_import`, `nwb_export`, `nwbio`; profiles `import_plugins` and `data_export`; requires NWB metadata mapping and exporter provenance before exchange claims.
- `BVA-io`: `gated_guidance`; probes `pop_loadbv`, `pop_writebva`, `eegplugin_bva_io`; profiles `import_plugins` and `data_export`; preserve BrainVision header, marker, and channel provenance.
- `HEDTools`: `indexed_only`; probes `eegplugin_hed`, `pop_hedtags`, `hedtools`; profile `hed_event_annotation`; requires HED schema/version or equivalent event-codebook provenance before condition-level claims.

## Filtering And Line-Noise Plugins

- `firfilt`: `gated_guidance`; probes `pop_eegfiltnew`, `eegfiltnew`, `firfilt`; claim `EEGLAB-FILT-001`.
- `CleanLine`: `gated_guidance`; probes `pop_cleanline`, `cleanline`; claim `EEGLAB-LINE-001`.
- `Zapline-Plus`: `indexed_only`; probes `clean_data_with_zapline_plus`, `zapline_plus`; indexed as optional line-noise guidance.

## ICA And Advanced Compute Plugins

- `AMICA`: `indexed_only`; probes `runamica15`, `pop_runamica`; profile `amica_ica`; requires plugin availability, rank/PCA/reference review, compute strategy, and derivative output; no default execution promise.
- `Picard`: `gated_guidance`; probes `picard`, `runica_nsg`; fallback must record the actual ICA algorithm used.
- `NSGportal`: `indexed_only`; probes `pop_nsg`, `nsgportal`; profile `nsg_remote`; remote NSG execution is outside the local-first MCP surface unless a dedicated secure integration is added.

## LIMO / SIFT / NFT

- `LIMO`: `indexed_only`; probes `pop_limo`, `limo_eeg`, `limo_random_select`; requires model/design/correction policy before claims.
- `SIFT`: `indexed_only`; probes `eegplugin_sift`, `pop_est_fitMVAR`, `pop_est_mvarConnectivity`; requires MVAR/source model validation and statistics policy.
- `groupSIFT`: `indexed_only`; probes `eegplugin_groupSIFT`; group connectivity remains guidance-only.
- `NFT`: `indexed_only`; probes `eegplugin_nft`, `NFT`; custom head-model generation remains guidance-only unless installed and documented.

`eeglab_plugin_check` returns this matrix as `outputs.plugin_matrix` with availability, `support_level`, claim IDs, dependent profiles, functions checked, found functions, and next steps.
