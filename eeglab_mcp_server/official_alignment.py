"""Official EEGLAB/SCCN alignment claims and method gate evaluation."""

from __future__ import annotations

from typing import Any

CITED_ON = "2026-06-25"


OFFICIAL_SOURCE_SNAPSHOT: dict[str, Any] = {
    "retrieved_on": "2026-06-25",
    "support_level_values": [
        "executable",
        "gated_guidance",
        "indexed_only",
        "out_of_scope",
    ],
    "mirrors": {
        "sccn/eeglab": {
            "commit": "4207693",
            "url": "https://github.com/sccn/eeglab",
        },
        "sccn/sccn.github.io": {
            "commit": "f53c85d",
            "url": "https://github.com/sccn/sccn.github.io",
        },
        "sccn/ICLabel": {
            "commit": "644578b",
            "url": "https://github.com/sccn/ICLabel",
        },
        "sccn/clean_rawdata": {
            "commit": "d4b143f",
            "url": "https://github.com/sccn/clean_rawdata",
        },
        "sccn/dipfit": {
            "commit": "b0b660e",
            "url": "https://github.com/sccn/dipfit",
        },
        "sccn/EEG-BIDS": {
            "commit": "8486b1d",
            "url": "https://github.com/sccn/EEG-BIDS",
        },
        "sccn/EEGLAB_course": {
            "commit": "3023c63",
            "url": "https://github.com/sccn/EEGLAB_course",
        },
        "sccn/SIFT": {
            "commit": "57817a0",
            "url": "https://github.com/sccn/SIFT",
        },
        "sccn/cleanline": {
            "commit": "117bffa",
            "url": "https://github.com/sccn/cleanline",
        },
        "sccn/firfilt": {
            "commit": "ff8227f",
            "url": "https://github.com/sccn/firfilt",
        },
        "sccn/zapline-plus": {
            "commit": "18d4eec",
            "url": "https://github.com/sccn/zapline-plus",
        },
        "sccn/nsgportal": {
            "commit": "6ff9541",
            "url": "https://github.com/sccn/nsgportal",
        },
        "sccn/HEDTools": {
            "commit": "95eb757",
            "url": "https://github.com/sccn/HEDTools",
        },
        "sccn/BVA-io": {
            "commit": "d5fe22f",
            "url": "https://github.com/sccn/BVA-io",
        },
        "sccn/relica": {
            "commit": "b3292d0",
            "url": "https://github.com/sccn/relica",
        },
        "sccn/viewprops": {
            "commit": "efafbc1",
            "url": "https://github.com/sccn/viewprops",
        },
        "sccn/get_chanlocs": {
            "commit": "25b2a34",
            "url": "https://github.com/sccn/get_chanlocs",
        },
        "sccn/roiconnect": {
            "commit": "3310ab6",
            "url": "https://github.com/sccn/roiconnect",
        },
        "arnodelorme/eegstats": {
            "commit": "fc0ff47",
            "url": "https://github.com/arnodelorme/eegstats",
        },
    },
}


OFFICIAL_CLAIMS: dict[str, dict[str, Any]] = {
    "EEGLAB-FUNC-001": {
        "title": "EEGLAB exposes user-facing pop_ functions and lower-level signal-processing functions.",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/EEGLAB_functions.html",
        "applies_to": ["all_tools", "tool_descriptions", "protocol"],
        "requirement": "Map MCP tools to EEGLAB-style user operations and record underlying function families when possible.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-STRUCT-001": {
        "title": "EEG datasets carry event, urevent, channel, history, and metadata structures.",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/Data_Structures.html",
        "applies_to": ["qc", "events", "provenance"],
        "requirement": "Inspect and report EEG.event, EEG.urevent, channel locations, and EEG.history before scientific interpretation.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-EVENT-001": {
        "title": "Event semantics must be validated before event-locked analysis.",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/Data_Structures.html",
        "applies_to": ["epoch", "erp", "timefreq"],
        "requirement": "Only confirmed task-condition triggers should drive epoching; boundary/QC/segment markers are not ERP triggers.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-FILT-001": {
        "title": "Filtering changes the data and must be parameterized and reported.",
        "url": "https://eeglab.org/tutorials/05_Preprocess/Filtering.html",
        "applies_to": ["filter", "pipeline"],
        "requirement": "Record cutoffs, rationale, and derivative-output strategy for filtering.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-ASR-001": {
        "title": "clean_rawdata provides ASR and bad-channel/bad-segment cleaning.",
        "url": "https://eeglab.org/plugins/clean_rawdata/",
        "applies_to": ["clean_rawdata", "pipeline"],
        "requirement": "Use clean_rawdata only when the plugin is available and thresholds/data-shape assumptions are recorded.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-ICA-001": {
        "title": "ICA workflows require appropriate data preparation and rank/reference awareness.",
        "url": "https://eeglab.org/tutorials/06_RejectArtifacts/RunICA.html",
        "applies_to": ["run_ica", "pipeline"],
        "requirement": "Check continuous-data suitability, bad-channel policy, and rank/reference decisions before ICA.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-ICLABEL-001": {
        "title": "ICLabel classifies ICA components after ICA decomposition.",
        "url": "https://github.com/sccn/ICLabel",
        "applies_to": ["classify_ica", "flag_components", "remove_components"],
        "requirement": "Require ICA weights and ICLabel availability before automated component classification.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-TF-001": {
        "title": "Time-frequency decomposition depends on event locking, baseline, cycles, and frequency settings.",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
        "applies_to": ["timefreq", "plot_timefreq"],
        "requirement": "Report event-locking, baseline, cycles, frequency range, and output limitations for ERSP/ITC.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-DIPFIT-001": {
        "title": "DIPFIT source localization requires channel locations, model assumptions, and source resources.",
        "url": "https://eeglab.org/plugins/dipfit/",
        "applies_to": ["source", "source_settings"],
        "requirement": "Require ICA/source model, channel locations, DIPFIT resources, and head model/template assumptions.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-BIDS-001": {
        "title": "EEGLAB supports BIDS import and STUDY workflows for group analysis.",
        "url": "https://eeglab.org/tutorials/11_Scripting/Analyzing_EEG_BIDS_data_in_EEGLAB.html",
        "applies_to": ["import_bids", "bids_export", "study"],
        "requirement": "Require BIDS/multi-subject structure, sidecar metadata, design variables, and locked single-subject preprocessing before BIDS/STUDY or group-statistics claims.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-BIDSEXPORT-001": {
        "title": "EEG-BIDS export requires complete metadata and derivative provenance.",
        "url": "https://eeglab.org/plugins/EEG-BIDS/",
        "applies_to": ["bids_export", "derivatives", "bids_metadata"],
        "requirement": "Treat BIDS export as guidance-only unless EEG-BIDS export support, sidecars, channel/electrode metadata, event descriptions, and derivative provenance are complete.",
        "cited_on": CITED_ON,
    },
    "BIDS-EEG-001": {
        "title": "BIDS EEG sidecars preserve acquisition, channel, electrode, and coordinate-system metadata.",
        "url": "https://bids-specification.readthedocs.io/en/stable/modality-specific-files/electroencephalography.html",
        "applies_to": ["acquisition", "bids_metadata", "provenance"],
        "requirement": "Record task, sampling, reference, power-line frequency, recording type, channel status, electrode positions, and coordinate-system metadata when treating data as BIDS-ready.",
        "cited_on": CITED_ON,
    },
    "BIDS-EVENTS-001": {
        "title": "BIDS events.tsv files use onset/duration timing and events.json sidecars for column meanings.",
        "url": "https://bids-specification.readthedocs.io/en/stable/modality-agnostic-files/events.html",
        "applies_to": ["events", "event_semantics", "bids_metadata"],
        "requirement": "Require onset and duration columns, and describe trial_type/additional event columns in events.json before inferring task-condition semantics.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-COURSE-001": {
        "title": "EEGLAB course materials cover advanced BIDS, preprocessing, source/connectivity, ICA clustering, and statistics.",
        "url": "https://github.com/sccn/EEGLAB_course",
        "applies_to": ["advanced_project", "skill"],
        "requirement": "Use staged project planning and explicit reporting for complex research workflows.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-IMPORT-001": {
        "title": "EEGLAB import tutorials cover continuous, epoched, event, channel, and BIDS inputs.",
        "url": "https://eeglab.org/tutorials/04_Import/Import.html",
        "applies_to": ["load_data", "import_bids", "provenance"],
        "requirement": "Preserve source path, file format, sidecar availability, events, and channel-location assumptions after import.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-IMPORT-PLUGINS-001": {
        "title": "EEGLAB imports non-native EEG formats through plugin- or function-dependent paths.",
        "url": "https://eeglab.org/tutorials/04_Import/Importing_Continuous_and_Epoched_Data.html",
        "applies_to": ["import_plugins", "load_data", "provenance"],
        "requirement": "Record source format, importer/plugin path, event/channel mapping, and raw-file preservation before treating imported data as analysis-ready.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-EXPORT-001": {
        "title": "EEGLAB export workflows are format-dependent and must preserve derivative provenance.",
        "url": "https://eeglab.org/tutorials/misc/Exporting_Data.html",
        "applies_to": ["data_export", "derivatives", "provenance"],
        "requirement": "Treat non-.set export as guidance-only unless the target format, plugin/function path, metadata completeness, and derivative output are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-HED-001": {
        "title": "HEDTools supports HED event annotation workflows for EEGLAB data.",
        "url": "https://github.com/sccn/HEDTools",
        "applies_to": ["hed", "event_semantics", "bids_metadata"],
        "requirement": "Use HED as structured event metadata only when tags/schema/version or equivalent event descriptions are recorded.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-HISTORY-001": {
        "title": "EEGLAB history can be used to recover GUI operations into reproducible scripts.",
        "url": "https://eeglab.org/tutorials/11_Scripting/Using_EEGLAB_history.html",
        "applies_to": ["history_scripting", "provenance", "batch"],
        "requirement": "Review EEG.history-derived scripts, parameterize paths/outputs, and record deviations before treating them as batch protocols.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-EVENTSCRIPT-001": {
        "title": "EEGLAB event-processing scripts can modify event labels, latencies, and selections.",
        "url": "https://eeglab.org/tutorials/11_Scripting/Event_Processing_command_line.html",
        "applies_to": ["event_script_modification", "events", "provenance"],
        "requirement": "Record event modification rules, latency units, urevent preservation/relinking, and semantic validation before event-script changes support analysis.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-MFF-001": {
        "title": "MFF-matlab-io is an official EEGLAB plugin path for EGI MFF import/export.",
        "url": "https://eeglab.org/plugins/MFF-matlab-io/",
        "applies_to": ["import_plugins", "data_export", "mff"],
        "requirement": "Treat MFF import/export as plugin-dependent and report event/channel metadata mapping and derivative output status.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-NWB-001": {
        "title": "NWB-io is an official EEGLAB plugin path for NWB import/export guidance.",
        "url": "https://eeglab.org/plugins/NWB-io/",
        "applies_to": ["import_plugins", "data_export", "nwb"],
        "requirement": "Treat NWB exchange as plugin-dependent guidance unless importer/exporter availability and metadata mapping are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-BVA-001": {
        "title": "BVA-io is an official EEGLAB plugin path for BrainVision import/export.",
        "url": "https://eeglab.org/plugins/BVA-io/",
        "applies_to": ["import_plugins", "data_export", "brainvision"],
        "requirement": "Treat BrainVision import/export as plugin-dependent and preserve marker/channel/header provenance.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-CHANLOC-001": {
        "title": "Channel locations are required for topographic and source-level interpretation.",
        "url": "https://eeglab.org/tutorials/04_Import/Channel_Locations.html",
        "applies_to": ["channel_locations", "topoplot", "source", "interpolation"],
        "requirement": "Check channel-location coverage before topography, interpolation, source localization, or montage-dependent claims.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-REREF-001": {
        "title": "Rereferencing changes the signal and affects rank/reference interpretation.",
        "url": "https://eeglab.org/tutorials/05_Preprocess/rereferencing.html",
        "applies_to": ["reref", "ica", "preprocessing"],
        "requirement": "Record reference choice and rank/reference implications before rereferencing or ICA interpretation.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-RESAMPLE-001": {
        "title": "Resampling changes sampling rate and must preserve analysis-relevant frequency content.",
        "url": "https://eeglab.org/tutorials/05_Preprocess/resampling.html",
        "applies_to": ["resample", "preprocessing"],
        "requirement": "Record target sampling rate and justify it relative to the frequency content needed for analysis.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-LINE-001": {
        "title": "Line-noise handling should be explicit and plugin-dependent when CleanLine/Zapline-style tools are used.",
        "url": "https://eeglab.org/plugins/cleanline/",
        "applies_to": ["line_noise", "cleanline", "zapline", "preprocessing"],
        "requirement": "Record power-line frequency, method, parameters, and plugin availability for line-noise cleanup.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-REJECT-001": {
        "title": "Artifact and epoch rejection require explicit thresholds, review policy, and retained-data reporting.",
        "url": "https://eeglab.org/tutorials/06_RejectArtifacts/",
        "applies_to": ["reject_epochs", "artifact_rejection", "qc"],
        "requirement": "Record rejection criteria and retained/rejected data before interpreting cleaned or epoched results.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-EPOCH-001": {
        "title": "Extracting epochs depends on valid event codes, time windows, and baseline assumptions.",
        "url": "https://eeglab.org/tutorials/07_Extract_epochs/Extracting_Data_Epochs.html",
        "applies_to": ["epoch", "erp", "timefreq"],
        "requirement": "Report event labels, epoch windows, baseline windows, and trial counts after epoch extraction.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-ERP-001": {
        "title": "ERP averaging and plotting require validated epochs, channel/ROI choices, and condition definitions.",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
        "applies_to": ["erp", "plot_erp", "average_erp"],
        "requirement": "Report condition definitions, channels/ROIs, time windows, and rejected-trial context for ERP outputs.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-SPECTRAL-001": {
        "title": "Spectral analyses require explicit channels, frequency ranges, and data-shape assumptions.",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "applies_to": ["spectral", "connectivity", "resting"],
        "requirement": "Record channel/ROI set, frequency range, data shape, artifact policy, and interpretation limits for spectra/connectivity.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-TOPO-001": {
        "title": "Topographic maps require channel locations and valid time/frequency selections.",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "applies_to": ["topoplot", "visualization"],
        "requirement": "Require channel-location coverage before topographic plots or scalp-map interpretation.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-STUDY-001": {
        "title": "STUDY creation, design, precomputation, visualization, clustering, and statistics are separate group-analysis stages.",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/",
        "applies_to": ["study", "study_precompute", "study_visualization", "group_statistics", "ica_clustering"],
        "requirement": "Lock single-subject preprocessing, subject/session metadata, design variables, measure type, precomputation state, alpha, and correction before group claims.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-STUDY-PRECOMP-001": {
        "title": "STUDY measures must be precomputed before group visualization, clustering, or statistics.",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "applies_to": ["study_precompute", "study_visualization", "study_statistics"],
        "requirement": "Require a STUDY design, selected measure family, precomputation parameters, and saved derivatives before claiming group-level measures.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-ICCLUSTER-001": {
        "title": "STUDY ICA clustering depends on ICA decompositions, measures, clustering features, and review.",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/component_clustering_tools.html",
        "applies_to": ["ica_clustering", "study", "source"],
        "requirement": "Treat ICA clustering as guidance-only unless ICA, channel/source assumptions, clustering features, outlier policy, and review criteria are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-LIMO-001": {
        "title": "LIMO is an EEGLAB plugin path for GLM/statistical EEG workflows.",
        "url": "https://eeglab.org/plugins/limo/",
        "applies_to": ["limo", "statistics", "study"],
        "requirement": "Treat LIMO as guidance-only unless plugin availability, design matrix, first/second-level model, and correction policy are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-SIFT-001": {
        "title": "SIFT covers source information flow/connectivity workflows with model-fitting and validation requirements.",
        "url": "https://eeglab.org/plugins/SIFT/",
        "applies_to": ["sift", "connectivity", "mvar"],
        "requirement": "Treat SIFT as guidance-only unless plugin availability, stationarity/model order, validation, and statistics are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-PLUGIN-001": {
        "title": "EEGLAB plugin workflows must be checked before plugin-dependent claims or execution.",
        "url": "https://eeglab.org/plugins/",
        "applies_to": ["plugin_check", "plugin_matrix", "advanced_project"],
        "requirement": "Probe plugin/function availability and report support level before plugin-dependent workflows.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-REVISION-001": {
        "title": "EEGLAB revision history and downloads provide versioned release provenance and archive context.",
        "url": "https://eeglab.org/others/EEGLAB_revision_history.html",
        "applies_to": ["revision_history", "release_management", "provenance"],
        "requirement": "Record the release archive or revision-history reference when planning version-sensitive analyses or reproducible setup.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-HARDWARE-001": {
        "title": "EEGLAB hardware and software recommendations define environment prerequisites and setup limits.",
        "url": "https://eeglab.org/others/EEGLAB_hardware_and_software_recommendations.html",
        "applies_to": ["hardware_requirements", "setup", "provenance"],
        "requirement": "Treat hardware/software recommendations as setup guidance and record environment assumptions when they affect reproducibility.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-TUTORIAL-DATA-001": {
        "title": "EEGLAB tutorial data and public examples support reproducible practice and import demonstrations.",
        "url": "https://eeglab.org/tutorials/tutorial_data.html",
        "applies_to": ["tutorial_data", "sample_data", "import"],
        "requirement": "Preserve sample-data provenance and use tutorial datasets as reproducible examples rather than surrogate evidence for user data.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-PLUGIN-DEV-001": {
        "title": "EEGLAB plugin tutorials explain how to write functions, GUIs, and eegplugin_ extensions.",
        "url": "https://eeglab.org/tutorials/contribute/design_plugin.html",
        "applies_to": ["plugin_development", "advanced_project", "skill"],
        "requirement": "Use the plugin tutorial and extension pages to scope new EEGLAB extensions, but do not treat them as executable analysis workflows.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-RELICA-001": {
        "title": "RELICA estimates the reliability of ICA decompositions and can optionally run on NSG.",
        "url": "https://eeglab.org/plugins/relica/",
        "applies_to": ["relica", "ica", "advanced_project"],
        "requirement": "Treat RELICA as an ICA-reliability planning workflow that depends on an existing ICA decomposition and bootstrap settings.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-VIEWPROPS-001": {
        "title": "Viewprops extends pop_prop for component and channel inspection with ICLabel-aware display.",
        "url": "https://eeglab.org/plugins/viewprops/",
        "applies_to": ["viewprops", "ica", "iclabel"],
        "requirement": "Use Viewprops as a review and visualization aid after ICA, not as a substitute for ICA or component review.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-GETCHANLOCS-001": {
        "title": "get_chanlocs digitizes 3-D head images into EEG.chanlocs for plotting and source localization.",
        "url": "https://eeglab.org/plugins/get_chanlocs/",
        "applies_to": ["get_chanlocs", "channel_locations", "source"],
        "requirement": "Use get_chanlocs when 3-D head images and fiducials exist and the goal is to populate or repair channel locations.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-ROICONNECT-001": {
        "title": "ROIconnect performs source-level ROI connectivity analysis with atlas-defined regions.",
        "url": "https://eeglab.org/plugins/roiconnect/",
        "applies_to": ["roiconnect", "connectivity", "source"],
        "requirement": "Use ROIconnect only when a source model, ROI atlas, and connectivity metric are defined.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-EEGSTATS-001": {
        "title": "EEGstats computes band power, alpha peak frequency, and alpha asymmetry for EEGLAB datasets and STUDYs.",
        "url": "https://eeglab.org/plugins/eegstats/",
        "applies_to": ["eegstats", "spectral", "study"],
        "requirement": "Use EEGstats when frequency-band definitions, channel selections, and dataset or STUDY scope are recorded.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-AMICA-001": {
        "title": "AMICA is an advanced ICA plugin path with separate installation and reporting requirements.",
        "url": "https://eeglab.org/plugins/amica/",
        "applies_to": ["amica", "run_ica", "advanced_project"],
        "requirement": "Treat AMICA as indexed guidance unless plugin availability, algorithm choice, rank/PCA settings, compute strategy, and reproducible output paths are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-NSG-001": {
        "title": "NSGportal enables remote/HPC EEGLAB workflows outside local-first execution.",
        "url": "https://eeglab.org/plugins/nsgportal/",
        "applies_to": ["nsgportal", "remote_compute", "advanced_project"],
        "requirement": "Treat NSG remote execution as out of the local MCP execution surface unless credentials, upload policy, remote job provenance, and a dedicated integration are explicit.",
        "cited_on": CITED_ON,
    },
    "EEGLAB-PIPELINE-001": {
        "title": "EEGLAB automated pipelines bundle import, cleaning, ICA/ICLabel, epoching, and reporting choices.",
        "url": "https://eeglab.org/tutorials/11_Scripting/automated_pipeline.html",
        "applies_to": ["pipeline", "protocol", "batch"],
        "requirement": "Use one-click/batch pipelines only after defaults, outputs, events, and plugin prerequisites are accepted and recorded.",
        "cited_on": CITED_ON,
    },
}


OFFICIAL_TOPIC_INDEX: dict[str, dict[str, Any]] = {
    "eeglab_home": {
        "title": "EEGLAB home, installation, quickstart, and ecosystem overview",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-PLUGIN-001", "EEGLAB-COURSE-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_plugin_check"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/",
        "notes": "Top-level EEGLAB entry point for installation, quickstart, tutorials, plugins, workshops, and references; indexed for orientation rather than execution.",
    },
    "eeglab_extensions_catalog": {
        "title": "EEGLAB extensions and plugin catalog",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_plugin_check", "eeglab_project_plan"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/others/EEGLAB_Extensions.html",
        "notes": "The extension manager and plugin catalog are indexed for discovery and planning only; no plugin execution promise is implied.",
    },
    "eeglab_plugin_family_catalog": {
        "title": "Official plugin family catalog",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_plugin_check", "eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/plugin-family-catalog.md",
        "url": "https://eeglab.org/plugins/",
        "notes": "The official plugin catalog page is indexed as a discovery-only family catalog, covering BrainBeats, trimOutlier, fMRIb, IMAT, NIMA, PACTools, ARfitStudio, PowPowCAT, std_dipoleDensity, CTFimport, Neuroscan-io, FirFilt, and the core EEGLAB plugins; no execution promise is implied.",
    },
    "eeglab_revision_history": {
        "title": "EEGLAB revision history and downloads",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-REVISION-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/others/EEGLAB_revision_history.html",
        "notes": "Release and download history is indexed so version/provenance planning can reference the official release archive without implying analysis execution.",
    },
    "eeglab_hardware_requirements": {
        "title": "Hardware and software requirements",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-HARDWARE-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/support-matrix.md",
        "url": "https://eeglab.org/others/EEGLAB_hardware_and_software_recommendations.html",
        "notes": "Environment recommendations are indexed as setup/planning context rather than data-analysis support.",
    },
    "eeglab_tutorial_data": {
        "title": "Tutorial data and publicly available EEG data",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-TUTORIAL-DATA-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_load_data", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/tutorial_data.html",
        "notes": "Public tutorial datasets and example downloads are indexed so sample-data provenance stays visible without promising hosted-data execution.",
    },
    "eeglab_tutorials_index": {
        "title": "EEGLAB tutorials index and conceptual guide",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-FUNC-001", "EEGLAB-STRUCT-001", "EEGLAB-COURSE-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/",
        "notes": "Concepts, import, preprocess, plotting, group analysis, scripting, and contribution entry points are indexed here before branch execution.",
    },
    "eeglab_concepts_guide": {
        "title": "Concepts guide: data structures, functions, and event semantics",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-FUNC-001", "EEGLAB-STRUCT-001", "EEGLAB-EVENT-001"],
        "tool_names": ["eeglab_info", "eeglab_get_events", "eeglab_history", "eeglab_qc_report"],
        "resource_uri": "eeglab://official/references.md",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/",
        "notes": "Concepts guide pages anchor the structural facts used by QC, events, and provenance inspection.",
    },
    "eeglab_installation_quickstart": {
        "title": "Installation, quickstart, and dataset management",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-IMPORT-001", "EEGLAB-COURSE-001"],
        "tool_names": ["eeglab_load_data", "eeglab_project_plan", "eeglab_workflow_recommend"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/",
        "notes": "Installation and quickstart pages guide entry into EEGLAB, but they are not analysis-execution topics themselves.",
    },
    "eeglab_workshops_course": {
        "title": "EEGLAB course, workshops, and training materials",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-COURSE-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://github.com/sccn/EEGLAB_course",
        "notes": "Workshop and course materials are indexed for training context and advanced workflow planning.",
    },
    "eeglab_reference_topics_misc": {
        "title": "Reference topics: EMG, MEG, iEEG, preferences, export, ERP peaks, and legacy rejection",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-EXPORT-001", "EEGLAB-REJECT-001", "EEGLAB-ERP-001", "EEGLAB-IMPORT-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/misc/",
        "notes": "Misc reference topics are indexed as official context for export, ERP peaks, legacy rejection, and non-EEG modality guidance.",
    },
    "eeglab_interoperability": {
        "title": "Interoperability: FieldTrip, HPC, Python, Octave, and commercial software comparison",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-COURSE-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/misc/",
        "notes": "Interoperability topics are indexed as ecosystem context; they do not add analysis execution support on their own.",
    },
    "eeglab_support_topics": {
        "title": "Support topics: FAQ, filtering FAQ, mailing lists, bugs, and test cases",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-COURSE-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/misc/",
        "notes": "Support pages are indexed so that implementation guidance and known issues stay visible in the workflow record.",
    },
    "eeglab_exporting_data": {
        "title": "Exporting data and derivative handoff",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-EXPORT-001", "EEGLAB-BIDSEXPORT-001"],
        "tool_names": ["eeglab_save_data", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/misc/Exporting_Data.html",
        "notes": "Exporting data remains format-dependent; the MCP executes only the EEGLAB derivative save path.",
    },
    "eeglab_find_erp_peaks": {
        "title": "Finding ERP peak latencies",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-ERP-001"],
        "tool_names": ["eeglab_plot_erp", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/misc/find_erp_peaks.html",
        "notes": "Peak-finding is indexed as a reference topic and remains subordinate to the primary ERP waveform report.",
    },
    "eeglab_legacy_rejection": {
        "title": "Legacy artifact rejection methods",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-REJECT-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/06_RejectArtifacts/scrolling_data.html",
        "notes": "Legacy rejection methods are indexed for historical context, while current workflows use explicit gating and reporting.",
    },
    "eeglab_ica_quick_rejection": {
        "title": "Quick tutorial on ICA artifact rejection",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-ICA-001", "EEGLAB-REJECT-001"],
        "tool_names": ["eeglab_plugin_check", "eeglab_method_preflight", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/misc/Quick_Tutorial_on_Rejection.html",
        "notes": "The quick ICA rejection tutorial is guidance for artifact handling, not a substitute for review and preflight.",
    },
    "eeglab_dataset_management": {
        "title": "Dataset management and multi-dataset organization",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-IMPORT-001", "EEGLAB-STRUCT-001"],
        "tool_names": ["eeglab_load_data", "eeglab_project_plan"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/03_Dataset_management/datasets.html",
        "notes": "Dataset management is indexed for organizing multiple datasets and dataset-level provenance before analysis begins.",
    },
    "eeglab_coordinate_systems": {
        "title": "Coordinate systems and montage geometry",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-CHANLOC-001", "BIDS-EEG-001"],
        "tool_names": ["eeglab_edit_channels", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/coordinateSystem.html",
        "notes": "Coordinate-system concepts support channel-location and source modeling but remain indexed unless a channel-repair workflow is invoked.",
    },
    "eeglab_batch_processing_overview": {
        "title": "Batch processing and multiple-subject processing overview",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-PIPELINE-001", "EEGLAB-STUDY-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_method_preflight", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/multiple_subject_proccessing_overview.html",
        "notes": "Batch processing is indexed as a planning topic; group work still requires precompute and design gates.",
    },
    "function_model": {
        "title": "EEGLAB function model",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-FUNC-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/method-map.md",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/EEGLAB_functions.html",
        "notes": "All tools declare EEGLAB function family, read/write effect, and risk metadata.",
    },
    "data_structures": {
        "title": "EEG, ALLEEG, STUDY, event, urevent, chanlocs, history",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-STRUCT-001"],
        "tool_names": ["eeglab_info", "eeglab_get_events", "eeglab_history"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/ConceptsGuide/Data_Structures.html",
        "notes": "Read-only QC resources expose structure and provenance facts before interpretation.",
    },
    "import_and_bids": {
        "title": "Import continuous/epoched/events/channel/BIDS data",
        "support_level": "executable",
        "claim_ids": [
            "EEGLAB-IMPORT-001",
            "EEGLAB-BIDS-001",
            "BIDS-EEG-001",
            "BIDS-EVENTS-001",
        ],
        "tool_names": ["eeglab_load_data", "eeglab_import_bids"],
        "resource_uri": "eeglab://official/support-matrix.md",
        "url": "https://eeglab.org/tutorials/04_Import/Import.html",
        "notes": "BIDS import remains gated by project structure and plugin availability.",
    },
    "preferences_and_support": {
        "title": "Preferences, support resources, and common setup questions",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-COURSE-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/",
        "notes": "Preferences, FAQs, and support pages are indexed as operational context rather than executable analysis topics.",
    },
    "import_plugins_formats": {
        "title": "Plugin-dependent import formats: BIOSIG, File-IO, MFF, NWB, and BrainVision",
        "support_level": "gated_guidance",
        "claim_ids": [
            "EEGLAB-IMPORT-PLUGINS-001",
            "EEGLAB-IMPORT-001",
            "EEGLAB-MFF-001",
            "EEGLAB-NWB-001",
            "EEGLAB-BVA-001",
        ],
        "tool_names": [
            "eeglab_load_data",
            "eeglab_plugin_check",
            "eeglab_method_preflight",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/tutorials/04_Import/Importing_Continuous_and_Epoched_Data.html",
        "notes": "Non-native import formats require source-format, importer/plugin, event mapping, channel mapping, and provenance checks.",
    },
    "bids_export_derivatives": {
        "title": "BIDS export and derivative dataset publication",
        "support_level": "indexed_only",
        "claim_ids": [
            "EEGLAB-BIDSEXPORT-001",
            "EEGLAB-BIDS-001",
            "BIDS-EEG-001",
            "BIDS-EVENTS-001",
        ],
        "tool_names": ["eeglab_project_plan", "eeglab_plugin_check", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/method-map.md",
        "url": "https://eeglab.org/plugins/EEG-BIDS/",
        "notes": "BIDS export is indexed/guidance-only; no dedicated export execution tool is exposed.",
    },
    "data_export_formats": {
        "title": "Data export to EEGLAB, BIDS, MFF, NWB, BrainVision, or other exchange formats",
        "support_level": "indexed_only",
        "claim_ids": [
            "EEGLAB-EXPORT-001",
            "EEGLAB-BIDSEXPORT-001",
            "EEGLAB-MFF-001",
            "EEGLAB-NWB-001",
            "EEGLAB-BVA-001",
        ],
        "tool_names": [
            "eeglab_save_data",
            "eeglab_project_plan",
            "eeglab_plugin_check",
            "eeglab_method_preflight",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://official/method-map.md",
        "url": "https://eeglab.org/tutorials/misc/Exporting_Data.html",
        "notes": "The MCP can save EEGLAB .set derivatives; other exchange/export paths remain guidance-only until a dedicated execution tool exists.",
    },
    "hed_event_annotation": {
        "title": "HED event annotation and event metadata validation",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-HED-001", "BIDS-EVENTS-001", "EEGLAB-EVENTSCRIPT-001"],
        "tool_names": [
            "eeglab_event_semantics_audit",
            "eeglab_method_preflight",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://references/event-semantics.md",
        "url": "https://github.com/sccn/HEDTools",
        "notes": "HED tags are accepted as event-metadata evidence only when schema/version and condition-code meaning are recorded.",
    },
    "history_batch_scripting": {
        "title": "EEGLAB history, scripting, and batch protocol recovery",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-HISTORY-001", "EEGLAB-FUNC-001", "EEGLAB-PIPELINE-001"],
        "tool_names": [
            "eeglab_history",
            "eeglab_project_plan",
            "eeglab_method_preflight",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://official/gate-policy.md",
        "url": "https://eeglab.org/tutorials/11_Scripting/Using_EEGLAB_history.html",
        "notes": "History-derived scripts must be reviewed, parameterized, and reported before being treated as reproducible batch workflows.",
    },
    "scripting_index": {
        "title": "Scripting, automated pipelines, and command-line operations",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-HISTORY-001", "EEGLAB-PIPELINE-001", "EEGLAB-EVENTSCRIPT-001"],
        "tool_names": ["eeglab_history", "eeglab_protocol_export", "eeglab_project_plan"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/11_Scripting/",
        "notes": "Scripting topics are indexed so that GUI histories, batch flows, and command-line workflows stay discoverable without implying extra execution support.",
    },
    "event_script_modification": {
        "title": "Scripted event modification and urevent-aware recovery",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-EVENTSCRIPT-001", "EEGLAB-STRUCT-001", "EEGLAB-EVENT-001"],
        "tool_names": [
            "eeglab_event_semantics_audit",
            "eeglab_method_preflight",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://references/event-semantics.md",
        "url": "https://eeglab.org/tutorials/11_Scripting/Event_Processing_command_line.html",
        "notes": "The MCP can plan and gate event-script changes, but does not expose a generic event-mutation execution tool.",
    },
    "channel_locations": {
        "title": "Channel locations and montage repair",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-CHANLOC-001"],
        "tool_names": [
            "eeglab_edit_channels",
            "eeglab_interpolate_channels",
            "eeglab_topoplot",
        ],
        "resource_uri": "eeglab://official/support-matrix.md",
        "url": "https://eeglab.org/tutorials/04_Import/Channel_Locations.html",
        "notes": "Topography/source claims are blocked when channel locations are missing.",
    },
    "filter_resample_reref": {
        "title": "Filtering, resampling, and rereferencing",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-FILT-001", "EEGLAB-RESAMPLE-001", "EEGLAB-REREF-001"],
        "tool_names": ["eeglab_filter", "eeglab_resample", "eeglab_reref"],
        "resource_uri": "eeglab://references/preprocessing-decision-tree.md",
        "url": "https://eeglab.org/tutorials/05_Preprocess/Filtering.html",
        "notes": "Destructive preprocessing requires raw preservation, derivative output, and parameter reporting.",
    },
    "line_noise": {
        "title": "Line-noise cleanup",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-LINE-001"],
        "tool_names": ["eeglab_clean_line_noise"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/cleanline/",
        "notes": "CleanLine/Zapline/firfilt availability is reported through plugin_doctor.",
    },
    "clean_rawdata_asr": {
        "title": "clean_rawdata and ASR",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-ASR-001"],
        "tool_names": ["eeglab_clean_rawdata"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/clean_rawdata/",
        "notes": "Hard-gated on continuous data, thresholds, plugin availability, and derivative output.",
    },
    "artifact_rejection": {
        "title": "Bad-channel, bad-segment, and epoch rejection",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-REJECT-001"],
        "tool_names": [
            "eeglab_select_channels",
            "eeglab_interpolate_channels",
            "eeglab_reject_epochs",
        ],
        "resource_uri": "eeglab://references/preprocessing-decision-tree.md",
        "url": "https://eeglab.org/tutorials/06_RejectArtifacts/",
        "notes": "Reject/repair choices must be thresholded, counted, and reported.",
    },
    "ica_iclabel": {
        "title": "ICA, ICLabel, and component cleanup",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-ICA-001", "EEGLAB-ICLABEL-001"],
        "tool_names": [
            "eeglab_run_ica",
            "eeglab_classify_ica",
            "eeglab_flag_components",
            "eeglab_remove_components",
        ],
        "resource_uri": "eeglab://references/ica-iclabel-policy.md",
        "url": "https://eeglab.org/tutorials/06_RejectArtifacts/RunICA.html",
        "notes": "ICA/ICLabel/component removal are hard-gated and require review/provenance.",
    },
    "epoch_erp": {
        "title": "Epoch extraction, baseline, ERP averaging, ERP plots",
        "support_level": "executable",
        "claim_ids": ["EEGLAB-EVENT-001", "EEGLAB-EPOCH-001", "EEGLAB-ERP-001"],
        "tool_names": [
            "eeglab_epoch",
            "eeglab_erp_analysis",
            "eeglab_average_erp",
            "eeglab_plot_erp",
        ],
        "resource_uri": "eeglab://references/event-semantics.md",
        "url": "https://eeglab.org/tutorials/07_Extract_epochs/Extracting_Data_Epochs.html",
        "notes": "Epoching is blocked when event semantics are unconfirmed or only non-analysis markers remain.",
    },
    "erp_image": {
        "title": "ERP-image and single-trial dynamics",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-ERP-001", "EEGLAB-STUDY-PRECOMP-001"],
        "tool_names": ["eeglab_plot_erp", "eeglab_topoplot", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/report-field-matrix.md",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ERP_images.html",
        "notes": "EEGLAB documents ERP-image plots and single-trial dynamics, but this MCP does not expose a dedicated ERP-image execution tool. Treat it as a report/planning figure family unless a workflow later adds a dedicated executor.",
    },
    "spectral_timefreq_connectivity": {
        "title": "Spectral, ERSP/ITC, and sensor connectivity workflows",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-SPECTRAL-001", "EEGLAB-TF-001"],
        "tool_names": [
            "eeglab_spectral",
            "eeglab_timefreq",
            "eeglab_connectivity",
            "eeglab_plot_timefreq",
        ],
        "resource_uri": "eeglab://official/risk-matrix.md",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
        "notes": "Time-frequency is hard-gated; spectral/connectivity require frequency, channel, and artifact-policy reporting.",
    },
    "visualization_topography": {
        "title": "ERP, time-frequency, component, and topographic figures",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-TOPO-001", "EEGLAB-CHANLOC-001"],
        "tool_names": [
            "eeglab_topoplot",
            "eeglab_plot_erp",
            "eeglab_plot_timefreq",
            "eeglab_plot_components",
        ],
        "resource_uri": "eeglab://official/risk-matrix.md",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "notes": "Topographic interpretation requires channel-location coverage.",
    },
    "figure_atlas": {
        "title": "Branch figure atlas and visualization metadata",
        "support_level": "gated_guidance",
        "claim_ids": [
            "EEGLAB-ERP-001",
            "EEGLAB-SPECTRAL-001",
            "EEGLAB-TF-001",
            "EEGLAB-ICA-001",
            "EEGLAB-DIPFIT-001",
            "EEGLAB-STUDY-001",
            "EEGLAB-TOPO-001",
            "EEGLAB-ROICONNECT-001",
            "EEGLAB-SIFT-001",
        ],
        "tool_names": [
            "eeglab_plot_erp",
            "eeglab_topoplot",
            "eeglab_plot_psd",
            "eeglab_plot_timefreq",
            "eeglab_plot_components",
            "eeglab_plot_connectivity",
        ],
        "resource_uri": "eeglab://official/figure-atlas.md",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "notes": "Static figure families should carry branch, channel/ROI, latency/frequency, tool source, and interpretation-scope metadata.",
    },
    "advanced_figure_browser": {
        "title": "Default advanced figure browser",
        "support_level": "indexed_only",
        "claim_ids": [
            "EEGLAB-ERP-001",
            "EEGLAB-SPECTRAL-001",
            "EEGLAB-TF-001",
            "EEGLAB-ICA-001",
            "EEGLAB-DIPFIT-001",
            "EEGLAB-STUDY-001",
            "EEGLAB-TOPO-001",
            "EEGLAB-ROICONNECT-001",
            "EEGLAB-SIFT-001",
        ],
        "tool_names": [
            "eeglab_plot_erp",
            "eeglab_plot_psd",
            "eeglab_plot_timefreq",
            "eeglab_plot_components",
            "eeglab_plot_connectivity",
            "eeglab_topoplot",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://scripts/advanced_figures/README.md",
        "url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
        "notes": "The default browsable advanced figure gallery mirrors the official figure atlas across ERP, ERP-image, resting, time-frequency, ICA, connectivity, source, and STUDY families; it is indexed for discovery and browsing only.",
    },
    "study_visualization": {
        "title": "STUDY visualization and group plots",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-STUDY-001", "EEGLAB-STUDY-PRECOMP-001"],
        "tool_names": [
            "eeglab_plot_erp",
            "eeglab_plot_psd",
            "eeglab_plot_timefreq",
            "eeglab_topoplot",
            "eeglab_protocol_export",
        ],
        "resource_uri": "eeglab://official/report-field-matrix.md",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
        "notes": "EEGLAB STUDY tutorials cover grand-average ERP, spectra, ERP-image, and ERSP/ITC plots. Treat group visualizations as report/planning figure families unless the workflow also satisfies the STUDY precompute and design gates.",
    },
    "source_dipfit_nft": {
        "title": "DIPFIT source localization and NFT head-model guidance",
        "support_level": "gated_guidance",
        "claim_ids": ["EEGLAB-DIPFIT-001", "EEGLAB-CHANLOC-001"],
        "tool_names": ["eeglab_source_settings", "eeglab_source_localization"],
        "resource_uri": "eeglab://references/source-policy.md",
        "url": "https://eeglab.org/tutorials/09_source/",
        "notes": "DIPFIT execution is hard-gated; NFT/custom head-model topics remain indexed/guidance.",
    },
    "study_group_limo": {
        "title": "STUDY, group statistics, ICA clustering, and LIMO",
        "support_level": "gated_guidance",
        "claim_ids": [
            "EEGLAB-STUDY-001",
            "EEGLAB-STUDY-PRECOMP-001",
            "EEGLAB-ICCLUSTER-001",
            "EEGLAB-LIMO-001",
        ],
        "tool_names": [
            "eeglab_study_create",
            "eeglab_study_design",
            "eeglab_study_statistics",
        ],
        "resource_uri": "eeglab://references/statistics-reporting.md",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/",
        "notes": "STUDY tools are executable/gated; LIMO remains guidance-only unless a dedicated workflow is added.",
    },
    "study_precompute_clustering": {
        "title": "STUDY measure precompute, visualization, and ICA clustering",
        "support_level": "indexed_only",
        "claim_ids": [
            "EEGLAB-STUDY-001",
            "EEGLAB-STUDY-PRECOMP-001",
            "EEGLAB-ICCLUSTER-001",
        ],
        "tool_names": ["eeglab_project_plan", "eeglab_method_preflight", "eeglab_protocol_export"],
        "resource_uri": "eeglab://references/statistics-reporting.md",
        "url": "https://eeglab.org/tutorials/10_Group_analysis/component_clustering_tools.html",
        "notes": "Precompute and ICA clustering are indexed/guidance-only until dedicated execution tools/evals exist.",
    },
    "sift_connectivity": {
        "title": "SIFT and groupSIFT connectivity workflows",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-SIFT-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_plugin_check"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/SIFT/",
        "notes": "Indexed and preflight-guided only; no dedicated SIFT execution tool is exposed.",
    },
    "nsg_amica_picard_plugins": {
        "title": "NSGportal, AMICA, Picard, RELICA, Viewprops, and advanced plugin ecosystem",
        "support_level": "indexed_only",
        "claim_ids": [
            "EEGLAB-PLUGIN-001",
            "EEGLAB-COURSE-001",
            "EEGLAB-RELICA-001",
            "EEGLAB-VIEWPROPS-001",
            "EEGLAB-AMICA-001",
            "EEGLAB-NSG-001",
        ],
        "tool_names": ["eeglab_plugin_check", "eeglab_project_plan"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/",
        "notes": "Plugin availability is checked and reported, but execution is guidance-only unless an MCP tool exists.",
    },
    "plugin_development": {
        "title": "EEGLAB plugin development and extension authoring",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-PLUGIN-DEV-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/contribute/design_plugin.html",
        "notes": "Plugin authoring is indexed as contributing guidance, not as a data-analysis execution workflow.",
    },
    "relica_reliability": {
        "title": "RELICA ICA reliability and bootstrap review",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-RELICA-001", "EEGLAB-ICA-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_plugin_check", "eeglab_method_preflight", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/relica/",
        "notes": "RELICA is indexed as ICA-reliability guidance; bootstrap compute remains plugin-dependent and outside local execution support.",
    },
    "viewprops_review": {
        "title": "Viewprops component and channel inspection",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-VIEWPROPS-001", "EEGLAB-ICLABEL-001", "EEGLAB-ICA-001"],
        "tool_names": ["eeglab_plugin_check", "eeglab_method_preflight", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/viewprops/",
        "notes": "Viewprops is an ICLabel-aware inspection aid and remains guidance-only without a dedicated MCP execution tool.",
    },
    "get_chanlocs_digitization": {
        "title": "get_chanlocs 3-D electrode digitization",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-GETCHANLOCS-001", "EEGLAB-CHANLOC-001"],
        "tool_names": ["eeglab_edit_channels", "eeglab_plugin_check", "eeglab_method_preflight"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/get_chanlocs/",
        "notes": "get_chanlocs is a channel-location digitization aid; the MCP can only audit prerequisite metadata and channel-location repair plans.",
    },
    "roiconnect_source_connectivity": {
        "title": "ROIconnect source-level ROI connectivity",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-ROICONNECT-001", "EEGLAB-DIPFIT-001", "EEGLAB-SPECTRAL-001"],
        "tool_names": [
            "eeglab_source_localization",
            "eeglab_connectivity",
            "eeglab_plugin_check",
            "eeglab_method_preflight",
        ],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/roiconnect/",
        "notes": "ROIconnect is a source-level ROI connectivity topic; local MCP support is guidance-only and depends on source model and atlas metadata.",
    },
    "eegstats_metrics": {
        "title": "EEGstats band power, alpha peak, and alpha asymmetry",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-EEGSTATS-001", "EEGLAB-SPECTRAL-001", "EEGLAB-STUDY-001"],
        "tool_names": ["eeglab_spectral", "eeglab_project_plan", "eeglab_plugin_check", "eeglab_method_preflight"],
        "resource_uri": "eeglab://official/plugin-matrix.md",
        "url": "https://eeglab.org/plugins/eegstats/",
        "notes": "EEGstats is a spectral/statistics plugin for band power and alpha metrics; the MCP indexes it for planning and reporting only.",
    },
    "bids_hed_reporting": {
        "title": "BIDS/HED metadata and research reporting",
        "support_level": "gated_guidance",
        "claim_ids": [
            "EEGLAB-BIDS-001",
            "EEGLAB-COURSE-001",
            "BIDS-EEG-001",
            "BIDS-EVENTS-001",
        ],
        "tool_names": ["eeglab_import_bids", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/report-field-matrix.md",
        "url": "https://eeglab.org/tutorials/04_Import/BIDS.html",
        "notes": "BIDS/HED-sidecar metadata are treated as provenance evidence, not optional decoration.",
    },
    "contribution_and_plugin_dev": {
        "title": "Contribution workflow and plugin development",
        "support_level": "indexed_only",
        "claim_ids": ["EEGLAB-PLUGIN-DEV-001", "EEGLAB-PLUGIN-001"],
        "tool_names": ["eeglab_project_plan", "eeglab_protocol_export"],
        "resource_uri": "eeglab://official/topic-index.md",
        "url": "https://eeglab.org/tutorials/contribute/design_plugin.html",
        "notes": "Contribution and plugin-development topics are indexed for repository guidance, not analysis execution.",
    },
    "acquisition_hardware": {
        "title": "Acquisition hardware, amplifier setup, consent, and impedance procedure",
        "support_level": "out_of_scope",
        "claim_ids": ["BIDS-EEG-001"],
        "tool_names": ["eeglab_qc_report", "eeglab_protocol_export"],
        "resource_uri": "eeglab://references/acquisition-to-derivatives.md",
        "url": "https://eeglab.org/tutorials/",
        "notes": "The MCP audits imported metadata but does not acquire EEG or replace lab notebooks.",
    },
}


OFFICIAL_PLUGIN_MATRIX: dict[str, dict[str, Any]] = {
    "clean_rawdata": {
        "support_level": "executable",
        "functions": ["pop_clean_rawdata", "clean_rawdata", "clean_artifacts"],
        "claim_ids": ["EEGLAB-ASR-001"],
        "dependent_profiles": ["clean_rawdata", "pipeline"],
        "url": "https://eeglab.org/plugins/clean_rawdata/",
        "next_step_if_missing": "Install clean_rawdata through EEGLAB plugin manager or add it to the EEGLAB path before ASR/bad-channel workflows.",
    },
    "ICLabel": {
        "support_level": "executable",
        "functions": ["pop_iclabel", "iclabel", "pop_icflag"],
        "claim_ids": ["EEGLAB-ICLABEL-001"],
        "dependent_profiles": ["iclabel", "remove_components", "pipeline"],
        "url": "https://github.com/sccn/ICLabel",
        "next_step_if_missing": "Install ICLabel and its dependencies before component classification or automatic flagging.",
    },
    "DIPFIT": {
        "support_level": "executable",
        "functions": ["pop_dipfit_settings", "pop_multifit", "dipfitdefs"],
        "claim_ids": ["EEGLAB-DIPFIT-001"],
        "dependent_profiles": ["source"],
        "url": "https://eeglab.org/plugins/dipfit/",
        "next_step_if_missing": "Install DIPFIT resources and confirm channel/head-model assumptions before source workflows.",
    },
    "EEG-BIDS": {
        "support_level": "executable",
        "functions": ["pop_importbids", "pop_exportbids", "bids_export"],
        "claim_ids": ["EEGLAB-BIDS-001"],
        "dependent_profiles": [
            "bids_import",
            "bids_export",
            "study_create",
            "bids_metadata",
        ],
        "url": "https://eeglab.org/plugins/EEG-BIDS/",
        "next_step_if_missing": "Install EEG-BIDS before BIDS import/export or STUDY creation from BIDS folders.",
    },
    "BIOSIG": {
        "support_level": "gated_guidance",
        "functions": ["pop_biosig", "sopen", "biosig"],
        "claim_ids": ["EEGLAB-IMPORT-PLUGINS-001", "EEGLAB-IMPORT-001"],
        "dependent_profiles": ["import_plugins"],
        "url": "https://eeglab.org/tutorials/04_Import/Importing_Continuous_and_Epoched_Data.html",
        "next_step_if_missing": "Use .set/BIDS import if available or install/check BIOSIG before EDF/BDF/GDF-style import claims.",
    },
    "File-IO": {
        "support_level": "indexed_only",
        "functions": ["pop_fileio", "ft_read_header", "ft_read_data", "ft_read_event"],
        "claim_ids": ["EEGLAB-IMPORT-PLUGINS-001", "EEGLAB-IMPORT-001"],
        "dependent_profiles": ["import_plugins"],
        "url": "https://eeglab.org/tutorials/04_Import/Importing_Continuous_and_Epoched_Data.html",
        "next_step_if_missing": "Treat FieldTrip File-IO import as guidance-only until File-IO functions and event/channel mapping are confirmed.",
    },
    "MFF-matlab-io": {
        "support_level": "indexed_only",
        "functions": ["mff_import", "mff_export", "pop_mffimport"],
        "claim_ids": ["EEGLAB-MFF-001", "EEGLAB-IMPORT-PLUGINS-001", "EEGLAB-EXPORT-001"],
        "dependent_profiles": ["import_plugins", "data_export"],
        "url": "https://eeglab.org/plugins/MFF-matlab-io/",
        "next_step_if_missing": "Keep MFF import/export to planning until the plugin is installed and event/channel mapping plus derivative output are documented.",
    },
    "NWB-io": {
        "support_level": "indexed_only",
        "functions": ["nwb_import", "nwb_export", "nwbio"],
        "claim_ids": ["EEGLAB-NWB-001", "EEGLAB-IMPORT-PLUGINS-001", "EEGLAB-EXPORT-001"],
        "dependent_profiles": ["import_plugins", "data_export"],
        "url": "https://eeglab.org/plugins/NWB-io/",
        "next_step_if_missing": "Keep NWB exchange as indexed guidance until NWB-io availability and metadata mapping are explicit.",
    },
    "BVA-io": {
        "support_level": "gated_guidance",
        "functions": ["pop_loadbv", "pop_writebva", "eegplugin_bva_io"],
        "claim_ids": ["EEGLAB-BVA-001", "EEGLAB-IMPORT-PLUGINS-001", "EEGLAB-EXPORT-001"],
        "dependent_profiles": ["import_plugins", "data_export"],
        "url": "https://eeglab.org/plugins/BVA-io/",
        "next_step_if_missing": "Use BrainVision import/export only after BVA-io or compatible functions are available and marker/header provenance is preserved.",
    },
    "HEDTools": {
        "support_level": "indexed_only",
        "functions": ["eegplugin_hed", "pop_hedtags", "hedtools"],
        "claim_ids": ["EEGLAB-HED-001", "BIDS-EVENTS-001"],
        "dependent_profiles": ["hed_event_annotation", "bids_metadata"],
        "url": "https://github.com/sccn/HEDTools",
        "next_step_if_missing": "Use events.json or a validated lab codebook until HEDTools/HED schema support is available and recorded.",
    },
    "RELICA": {
        "support_level": "indexed_only",
        "functions": ["pop_relica", "relica", "eegplugin_relica"],
        "claim_ids": ["EEGLAB-RELICA-001", "EEGLAB-ICA-001", "EEGLAB-PLUGIN-001"],
        "dependent_profiles": ["relica_reliability", "run_ica", "nsg_remote"],
        "url": "https://eeglab.org/plugins/relica/",
        "next_step_if_missing": "Install RELICA and confirm ICA/bootstrap settings before claiming ICA reliability analysis support.",
    },
    "Viewprops": {
        "support_level": "indexed_only",
        "functions": ["pop_viewprops", "pop_prop_extended", "viewprops"],
        "claim_ids": ["EEGLAB-VIEWPROPS-001", "EEGLAB-ICLABEL-001"],
        "dependent_profiles": ["viewprops_review", "iclabel"],
        "url": "https://eeglab.org/plugins/viewprops/",
        "next_step_if_missing": "Install Viewprops alongside ICLabel before component-review claims.",
    },
    "get_chanlocs": {
        "support_level": "indexed_only",
        "functions": ["eegplugin_getchanlocs", "get_chanlocs"],
        "claim_ids": ["EEGLAB-GETCHANLOCS-001", "EEGLAB-CHANLOC-001"],
        "dependent_profiles": ["get_chanlocs_digitization", "channel_locations"],
        "url": "https://eeglab.org/plugins/get_chanlocs/",
        "next_step_if_missing": "Install get_chanlocs and ensure head images/fiducials exist before channel-digitization claims.",
    },
    "ROIconnect": {
        "support_level": "indexed_only",
        "functions": ["pop_roi_activity", "pop_roi_connect", "roiconnect"],
        "claim_ids": ["EEGLAB-ROICONNECT-001", "EEGLAB-DIPFIT-001", "EEGLAB-SPECTRAL-001"],
        "dependent_profiles": ["roiconnect_source_connectivity", "source", "connectivity"],
        "url": "https://eeglab.org/plugins/roiconnect/",
        "next_step_if_missing": "Install ROIconnect and document source model, atlas, and connectivity metric before ROI connectivity claims.",
    },
    "EEGstats": {
        "support_level": "indexed_only",
        "functions": ["pop_eegstats", "eegstats", "eegplugin_eegstats"],
        "claim_ids": ["EEGLAB-EEGSTATS-001", "EEGLAB-SPECTRAL-001", "EEGLAB-STUDY-001"],
        "dependent_profiles": ["eegstats_metrics", "spectral", "study_precompute"],
        "url": "https://eeglab.org/plugins/eegstats/",
        "next_step_if_missing": "Install EEGstats and record frequency bands, channels, and STUDY scope before spectral-statistics claims.",
    },
    "firfilt": {
        "support_level": "gated_guidance",
        "functions": ["pop_eegfiltnew", "eegfiltnew", "firfilt"],
        "claim_ids": ["EEGLAB-FILT-001"],
        "dependent_profiles": ["derivative_processing"],
        "url": "https://eeglab.org/plugins/firfilt/",
        "next_step_if_missing": "Use available EEGLAB filtering only after recording cutoffs/order/transition assumptions.",
    },
    "CleanLine": {
        "support_level": "gated_guidance",
        "functions": ["pop_cleanline", "cleanline"],
        "claim_ids": ["EEGLAB-LINE-001"],
        "dependent_profiles": ["line_noise"],
        "url": "https://eeglab.org/plugins/cleanline/",
        "next_step_if_missing": "Report missing CleanLine and use another justified line-noise strategy only after method limitations are recorded.",
    },
    "Zapline-Plus": {
        "support_level": "indexed_only",
        "functions": ["clean_data_with_zapline_plus", "zapline_plus"],
        "claim_ids": ["EEGLAB-LINE-001", "EEGLAB-PLUGIN-001"],
        "dependent_profiles": ["line_noise"],
        "url": "https://eeglab.org/plugins/zapline-plus/",
        "next_step_if_missing": "Treat Zapline-Plus as an optional line-noise plugin; do not claim support unless installed and a workflow is documented.",
    },
    "AMICA": {
        "support_level": "indexed_only",
        "functions": ["runamica15", "pop_runamica"],
        "claim_ids": ["EEGLAB-ICA-001", "EEGLAB-PLUGIN-001", "EEGLAB-AMICA-001"],
        "dependent_profiles": ["run_ica", "amica_ica"],
        "url": "https://eeglab.org/plugins/amica/",
        "next_step_if_missing": "Use runica/Picard path unless an AMICA-specific protocol and plugin installation are confirmed.",
    },
    "Picard": {
        "support_level": "gated_guidance",
        "functions": ["picard", "runica_nsg"],
        "claim_ids": ["EEGLAB-ICA-001", "EEGLAB-PLUGIN-001"],
        "dependent_profiles": ["run_ica"],
        "url": "https://eeglab.org/plugins/",
        "next_step_if_missing": "Fall back to runica when Picard is unavailable and record the ICA algorithm actually used.",
    },
    "LIMO": {
        "support_level": "indexed_only",
        "functions": ["pop_limo", "limo_eeg", "limo_random_select"],
        "claim_ids": ["EEGLAB-LIMO-001"],
        "dependent_profiles": ["limo_statistics"],
        "url": "https://eeglab.org/plugins/limo/",
        "next_step_if_missing": "Keep LIMO work to planning/reporting until plugin, STUDY design, model, and correction policy are explicit.",
    },
    "SIFT": {
        "support_level": "indexed_only",
        "functions": ["eegplugin_sift", "pop_est_fitMVAR", "pop_est_mvarConnectivity"],
        "claim_ids": ["EEGLAB-SIFT-001"],
        "dependent_profiles": ["sift_connectivity"],
        "url": "https://eeglab.org/plugins/SIFT/",
        "next_step_if_missing": "Keep SIFT work to guidance until model fitting, validation, stationarity, and statistics are documented.",
    },
    "groupSIFT": {
        "support_level": "indexed_only",
        "functions": ["eegplugin_groupSIFT"],
        "claim_ids": ["EEGLAB-SIFT-001", "EEGLAB-PLUGIN-001"],
        "dependent_profiles": ["sift_connectivity"],
        "url": "https://eeglab.org/plugins/groupSIFT/",
        "next_step_if_missing": "Use only as indexed guidance unless a groupSIFT-specific workflow is added.",
    },
    "NFT": {
        "support_level": "indexed_only",
        "functions": ["eegplugin_nft", "NFT"],
        "claim_ids": ["EEGLAB-DIPFIT-001", "EEGLAB-PLUGIN-001"],
        "dependent_profiles": ["source"],
        "url": "https://eeglab.org/plugins/NFT/",
        "next_step_if_missing": "Use DIPFIT template-model workflows unless NFT head-model generation is explicitly installed and documented.",
    },
    "NSGportal": {
        "support_level": "indexed_only",
        "functions": ["pop_nsg", "nsgportal"],
        "claim_ids": ["EEGLAB-PLUGIN-001", "EEGLAB-COURSE-001", "EEGLAB-NSG-001"],
        "dependent_profiles": ["advanced_project", "nsg_remote"],
        "url": "https://eeglab.org/plugins/nsgportal/",
        "next_step_if_missing": "Treat remote NSG execution as out of this MCP's local-first execution scope unless a dedicated integration is added.",
    },
}


REPORT_FIELD_MATRIX: dict[str, list[str]] = {
    "recording_and_acquisition": [
        "input_path",
        "source_format",
        "setname_filename_filepath",
        "sampling_rate_hz",
        "duration_sec",
        "data_shape",
        "channel_count",
        "reference_or_montage",
        "hardware_or_acquisition_notes_if_available",
        "power_line_frequency_if_available",
        "impedance_or_quality_notes_if_available",
        "importer_plugin_or_function_path",
        "source_format_sidecars_and_header_notes",
    ],
    "events_and_design": [
        "event_labels_counts_latencies",
        "event_roles_and_semantics_source",
        "urevent_link_status",
        "condition_definitions",
        "behavioral_log_or_events_json_source",
        "hed_schema_version_or_event_codebook",
        "event_modification_rules_and_latency_units",
        "epoch_and_baseline_windows",
    ],
    "preprocessing_parameters": [
        "filter_cutoffs_order_transition_if_known",
        "resampling_target_rate",
        "line_noise_method_and_frequency",
        "bad_channel_policy",
        "asr_thresholds",
        "rereference_policy",
        "ica_algorithm_rank_pca",
        "iclabel_thresholds_and_review",
        "epoch_rejection_thresholds",
        "interpolation_policy",
    ],
    "analysis_parameters": [
        "erp_channels_rois_time_windows",
        "required_figure_families",
        "conditional_figure_families",
        "guidance_only_figure_families",
        "figure_paths",
        "figure_descriptions",
        "figure_generation_notes",
        "spectral_frequency_range_band_definitions",
        "timefreq_cycles_baseline_output_measure",
        "connectivity_method_model_validation",
        "source_head_model_template_residual_variance",
        "study_design_variables_levels_alpha_correction",
        "external_export_format_and_metadata_mapping",
        "limo_or_sift_model_if_used",
        "relica_bootstrap_settings_and_ica_reliability",
        "viewprops_component_set_and_classifier",
        "get_chanlocs_scan_fiducials_and_head_image",
        "roiconnect_roi_atlas_source_model_and_connectivity_metric",
        "eegstats_band_power_alpha_peak_and_asymmetry_settings",
    ],
    "visualization_and_figures": [
        "required_figure_families",
        "conditional_figure_families",
        "guidance_only_figure_families",
        "figure_paths",
        "figure_descriptions",
        "figure_generation_notes",
    ],
    "outputs_and_limits": [
        "output_paths",
        "derivative_output_policy",
        "external_export_status_and_exporter_plugin",
        "software_versions_and_plugins",
        "official_gate_status",
        "source_claim_ids",
        "override_status_and_reason",
        "failed_steps_and_recovery",
        "limitations_no_clinical_or_anatomical_certainty_claims",
    ],
    "workflow_branch_coverage": [
        "branch_id",
        "branch_label",
        "branch_mode",
        "branch_completeness_status",
        "universal_preamble_steps",
        "ordered_branch_steps",
        "completed_steps",
        "missing_required_steps",
        "blocked_steps",
        "required_figures",
        "figure_atlas",
        "figure_paths",
        "required_outputs",
        "output_paths",
        "branch_notes",
    ],
}


UNIVERSAL_WORKFLOW_STEPS: list[str] = [
    "project_intake",
    "recording_provenance_audit",
    "load_qc_history",
    "raw_preservation_and_derivative_output_path",
    "plugin_check_if_needed",
    "method_preflight_before_high_risk_steps",
]


BRANCH_WORKFLOW_MATRIX: dict[str, dict[str, Any]] = {
    "erp": {
        "branch_id": "erp",
        "branch_label": "ERP",
        "branch_mode": "event_locked",
        "analysis_type_aliases": ["erp"],
        "figure_atlas": [
            {
                "figure_type": "erp_waveform",
                "figure_status": "required",
                "channel_or_roi": "Task-relevant channels or ROIs",
                "latency_window": "Component-specific ERP window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_erp",
                "official_anchor": "EEGLAB-ERP-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
                "interpretation_scope": "Condition-locked mean waveform comparison.",
            },
            {
                "figure_type": "erp_image_heatmap",
                "figure_status": "conditional",
                "channel_or_roi": "Channel or ROI used for the ERP image",
                "latency_window": "Single-trial sorting window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_erp / ERPimage",
                "official_anchor": "EEGLAB-ERP-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_ERP_images.html",
                "interpretation_scope": "Single-trial variability and sorting review.",
            },
            {
                "figure_type": "scalp_map_series",
                "figure_status": "required",
                "channel_or_roi": "All usable channels with valid locations",
                "latency_window": "Latency-specific scalp series",
                "frequency_window": "N/A",
                "tool_source": "eeglab_topoplot",
                "official_anchor": "EEGLAB-TOPO-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
                "interpretation_scope": "Latency-specific scalp distribution review.",
            },
            {
                "figure_type": "difference_wave_review",
                "figure_status": "conditional",
                "channel_or_roi": "Condition contrast channels or ROIs",
                "latency_window": "Component contrast window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_erp + eeglab_topoplot",
                "official_anchor": "EEGLAB-ERP-001 / EEGLAB-TOPO-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Data_Averaging.html",
                "interpretation_scope": "Polarity and latency sanity check.",
            },
            {
                "figure_type": "psd_review",
                "figure_status": "required",
                "channel_or_roi": "Task-relevant channels or ROIs",
                "latency_window": "N/A",
                "frequency_window": "Broad spectral sanity range",
                "tool_source": "eeglab_plot_psd",
                "official_anchor": "EEGLAB-SPECTRAL-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
                "interpretation_scope": "Broad spectral sanity check.",
            },
        ],
        "ordered_branch_steps": [
            "event_semantics_audit",
            "filter_and_line_noise_cleanup",
            "clean_rawdata_if_justified",
            "rereference",
            "ica_and_iclabel_review_if_justified",
            "component_removal_or_review",
            "epoch_and_baseline",
            "erp_analysis",
            "erp_topoplot_and_psd_figures",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "required_steps": [
            "event_semantics_audit",
            "filter_and_line_noise_cleanup",
            "rereference",
            "epoch_and_baseline",
            "erp_analysis",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "conditional_steps": [
            "clean_rawdata_if_justified",
            "ica_and_iclabel_review_if_justified",
            "component_removal_or_review",
            "eeglab_reject_epochs",
            "eeglab_average_erp",
            "eeglab_interpolate_channels",
        ],
        "forbidden_steps": [
            "epoch_boundary_or_excluded_markers",
            "treat_segment_markers_as_condition_triggers",
            "overwrite_raw_input",
            "skip_event_semantics_audit",
            "claim_resting_state_from_epoched_only_data",
        ],
        "required_figures": [
            "eeglab_plot_erp",
            "eeglab_topoplot",
            "eeglab_plot_psd",
        ],
        "conditional_figures": [
            "eeglab_plot_components",
        ],
        "required_figure_families": [
            "erp_waveform",
            "scalp_topography",
            "psd_spectra",
        ],
        "conditional_figure_families": [
            "trial_erp_image",
            "ica_component_diagnostics",
        ],
        "guidance_only_figure_families": [
            "ersp_itc_heatmap",
            "connectivity_matrix",
            "study_group_figures",
        ],
        "required_outputs": [
            "derivative_set",
            "erp_summary_tables",
            "protocol_export",
            "final_report",
        ],
        "branch_notes": [
            "Event semantics must be confirmed before epoching.",
            "Use only confirmed task-condition triggers for ERP claims.",
        ],
    },
    "resting": {
        "branch_id": "resting",
        "branch_label": "Resting-State Spectral/Connectivity",
        "branch_mode": "continuous",
        "analysis_type_aliases": ["resting", "connectivity"],
        "figure_atlas": [
            {
                "figure_type": "channel_spectra",
                "figure_status": "required",
                "channel_or_roi": "Resting-state channel or ROI set",
                "latency_window": "N/A",
                "frequency_window": "Selected spectral range",
                "tool_source": "eeglab_plot_psd",
                "official_anchor": "EEGLAB-SPECTRAL-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
                "interpretation_scope": "Channel/ROI power profile.",
            },
            {
                "figure_type": "band_power_topomap",
                "figure_status": "conditional",
                "channel_or_roi": "All usable channels with locations",
                "latency_window": "N/A",
                "frequency_window": "Band-specific scalp map",
                "tool_source": "eeglab_topoplot",
                "official_anchor": "EEGLAB-TOPO-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html",
                "interpretation_scope": "Frequency-band scalp distribution.",
            },
            {
                "figure_type": "connectivity_matrix",
                "figure_status": "conditional",
                "channel_or_roi": "Sensor or ROI set",
                "latency_window": "N/A",
                "frequency_window": "Connectivity frequency band",
                "tool_source": "eeglab_plot_connectivity",
                "official_anchor": "EEGLAB-SPECTRAL-001 / EEGLAB-ROICONNECT-001 / EEGLAB-SIFT-001",
                "official_url": "https://eeglab.org/plugins/roiconnect/",
                "interpretation_scope": "Sensor-level or ROI-level functional summary only.",
            },
        ],
        "ordered_branch_steps": [
            "continuous_data_suitability_review",
            "filter_and_line_noise_cleanup",
            "optional_conservative_clean_rawdata",
            "rereference",
            "spectral_analysis",
            "optional_connectivity_analysis",
            "psd_and_connectivity_figures",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "required_steps": [
            "continuous_data_suitability_review",
            "filter_and_line_noise_cleanup",
            "rereference",
            "spectral_analysis",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "conditional_steps": [
            "optional_conservative_clean_rawdata",
            "optional_connectivity_analysis",
            "eeglab_interpolate_channels",
            "eeglab_reject_epochs",
        ],
        "forbidden_steps": [
            "epoching_as_default",
            "baseline_correction_as_event_locked_analysis",
            "event_locked_claims_without_event_semantics",
            "anatomical_connectivity_claims_from_sensor_connectivity",
            "overwrite_raw_input",
        ],
        "required_figures": [
            "eeglab_plot_psd",
        ],
        "conditional_figures": [
            "eeglab_plot_connectivity",
        ],
        "required_figure_families": [
            "psd_spectra",
        ],
        "conditional_figure_families": [
            "connectivity_matrix",
            "scalp_topography",
        ],
        "guidance_only_figure_families": [
            "trial_erp_image",
            "ersp_itc_heatmap",
            "ica_component_diagnostics",
            "study_group_figures",
        ],
        "required_outputs": [
            "derivative_set",
            "spectral_summary",
            "protocol_export",
            "final_report",
        ],
        "branch_notes": [
            "Treat sensor-level connectivity as a functional summary, not anatomical connectivity.",
            "Keep data continuous unless the study design explicitly justifies segmentation.",
        ],
    },
    "timefreq": {
        "branch_id": "timefreq",
        "branch_label": "Time-Frequency",
        "branch_mode": "event_locked",
        "analysis_type_aliases": ["timefreq"],
        "figure_atlas": [
            {
                "figure_type": "ersp_itc_heatmap",
                "figure_status": "required",
                "channel_or_roi": "Event-locked channel or ROI",
                "latency_window": "Epoch window",
                "frequency_window": "Frequency range used for decomposition",
                "tool_source": "eeglab_plot_timefreq",
                "official_anchor": "EEGLAB-TF-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
                "interpretation_scope": "Event-locked power and phase dynamics.",
            },
            {
                "figure_type": "time_frequency_curve",
                "figure_status": "conditional",
                "channel_or_roi": "Event-locked channel or ROI",
                "latency_window": "Epoch window",
                "frequency_window": "Selected band or bands",
                "tool_source": "eeglab_plot_timefreq",
                "official_anchor": "EEGLAB-TF-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
                "interpretation_scope": "Frequency-specific time course review.",
            },
            {
                "figure_type": "tftopo_summary",
                "figure_status": "guidance_only",
                "channel_or_roi": "All electrodes",
                "latency_window": "Epoch window",
                "frequency_window": "Summary display",
                "tool_source": "tftopo",
                "official_anchor": "EEGLAB-TF-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
                "interpretation_scope": "Multi-electrode static summary only.",
            },
            {
                "figure_type": "metaplottopo_summary",
                "figure_status": "guidance_only",
                "channel_or_roi": "Electrode grid",
                "latency_window": "Epoch window",
                "frequency_window": "Summary display",
                "tool_source": "metaplottopo",
                "official_anchor": "EEGLAB-TF-001",
                "official_url": "https://eeglab.org/tutorials/08_Plot_data/Time-Frequency_decomposition.html",
                "interpretation_scope": "Channel-grid summary only.",
            },
        ],
        "ordered_branch_steps": [
            "event_semantics_audit",
            "filter_and_line_noise_cleanup",
            "epoch_and_baseline",
            "time_frequency_analysis",
            "timefreq_figures",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "required_steps": [
            "event_semantics_audit",
            "filter_and_line_noise_cleanup",
            "epoch_and_baseline",
            "time_frequency_analysis",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "conditional_steps": [
            "clean_rawdata_if_justified",
            "rereference",
            "ica_and_iclabel_review_if_justified",
            "component_removal_or_review",
            "eeglab_interpolate_channels",
        ],
        "forbidden_steps": [
            "epoch_boundary_or_excluded_markers",
            "skip_event_semantics_audit",
            "omit_baseline",
            "claim_timefreq_from_continuous_data_without_epochs",
            "overwrite_raw_input",
        ],
        "required_figures": [
            "eeglab_plot_timefreq",
        ],
        "conditional_figures": [
            "eeglab_topoplot",
            "eeglab_plot_psd",
        ],
        "required_figure_families": [
            "ersp_itc_heatmap",
        ],
        "conditional_figure_families": [
            "scalp_topography",
            "psd_spectra",
            "trial_erp_image",
        ],
        "guidance_only_figure_families": [
            "ica_component_diagnostics",
            "connectivity_matrix",
            "study_group_figures",
        ],
        "required_outputs": [
            "derivative_set",
            "timefreq_summary",
            "protocol_export",
            "final_report",
        ],
        "branch_notes": [
            "ERSP/ITC requires validated event locking, epoch length, baseline, and cycle settings.",
        ],
    },
    "source": {
        "branch_id": "source",
        "branch_label": "Source Localization",
        "branch_mode": "model_based",
        "analysis_type_aliases": ["source"],
        "figure_atlas": [
            {
                "figure_type": "source_dipole_review",
                "figure_status": "required",
                "channel_or_roi": "ICA components or source-model ROIs",
                "latency_window": "Model fit window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_source_localization",
                "official_anchor": "EEGLAB-DIPFIT-001",
                "official_url": "https://eeglab.org/plugins/dipfit/",
                "interpretation_scope": "Model fit quality and residual variance review.",
            },
            {
                "figure_type": "component_head_plot",
                "figure_status": "conditional",
                "channel_or_roi": "ICA component or source component",
                "latency_window": "Component review window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_components",
                "official_anchor": "EEGLAB-ICA-001 / EEGLAB-TOPO-001",
                "official_url": "https://eeglab.org/tutorials/06_RejectArtifacts/RunICA.html",
                "interpretation_scope": "Component scalp projection review.",
            },
            {
                "figure_type": "roi_connectivity_matrix",
                "figure_status": "conditional",
                "channel_or_roi": "ROI atlas",
                "latency_window": "Connectivity window",
                "frequency_window": "Connectivity band",
                "tool_source": "eeglab_plot_connectivity",
                "official_anchor": "EEGLAB-ROICONNECT-001",
                "official_url": "https://eeglab.org/plugins/roiconnect/",
                "interpretation_scope": "ROI-level functional connectivity summary.",
            },
            {
                "figure_type": "sift_timefreq_grid",
                "figure_status": "guidance_only",
                "channel_or_roi": "Source or ROI set",
                "latency_window": "Model window",
                "frequency_window": "Time-frequency connectivity grid",
                "tool_source": "SIFT",
                "official_anchor": "EEGLAB-SIFT-001",
                "official_url": "https://eeglab.org/plugins/SIFT/",
                "interpretation_scope": "Model-based connectivity summary only.",
            },
        ],
        "ordered_branch_steps": [
            "channel_location_review_or_repair",
            "plugin_check_dipfit",
            "optional_ica_and_component_review",
            "source_model_settings",
            "source_localization",
            "source_figures",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "required_steps": [
            "channel_location_review_or_repair",
            "plugin_check_dipfit",
            "source_model_settings",
            "source_localization",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "conditional_steps": [
            "optional_ica_and_component_review",
            "event_semantics_audit_if_event_locked_source",
            "eeglab_topoplot",
            "eeglab_plot_components",
        ],
        "forbidden_steps": [
            "source_claims_without_channel_locations",
            "anatomical_certainty_claims",
            "skip_dipfit_resources",
            "overwrite_raw_input",
        ],
        "required_figures": [
            "eeglab_plot_components",
        ],
        "conditional_figures": [
            "eeglab_topoplot",
        ],
        "required_figure_families": [
            "ica_component_diagnostics",
        ],
        "conditional_figure_families": [
            "scalp_topography",
        ],
        "guidance_only_figure_families": [
            "trial_erp_image",
            "psd_spectra",
            "ersp_itc_heatmap",
            "connectivity_matrix",
            "study_group_figures",
        ],
        "required_outputs": [
            "source_results",
            "protocol_export",
            "final_report",
        ],
        "branch_notes": [
            "Source localization requires correct channel locations, ICA or another justified source model, and DIPFIT resources.",
        ],
    },
    "study": {
        "branch_id": "study",
        "branch_label": "STUDY / Group Analysis",
        "branch_mode": "group",
        "analysis_type_aliases": ["study"],
        "figure_atlas": [
            {
                "figure_type": "grand_average_erp",
                "figure_status": "required",
                "channel_or_roi": "Study-level channels or ROIs",
                "latency_window": "Study ERP window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_erp",
                "official_anchor": "EEGLAB-STUDY-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
                "interpretation_scope": "Group-level ERP summary.",
            },
            {
                "figure_type": "all_channel_erp",
                "figure_status": "conditional",
                "channel_or_roi": "All or selected study channels",
                "latency_window": "Study ERP window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_erp",
                "official_anchor": "EEGLAB-STUDY-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
                "interpretation_scope": "Channel-wide group ERP review.",
            },
            {
                "figure_type": "spectra_and_scalp_maps",
                "figure_status": "conditional",
                "channel_or_roi": "Study channels or ROIs",
                "latency_window": "N/A",
                "frequency_window": "Study spectral band",
                "tool_source": "eeglab_plot_psd / eeglab_topoplot",
                "official_anchor": "EEGLAB-STUDY-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
                "interpretation_scope": "Group spectral summary.",
            },
            {
                "figure_type": "erp_image_review",
                "figure_status": "conditional",
                "channel_or_roi": "Study channel or ROI",
                "latency_window": "Study epoch window",
                "frequency_window": "N/A",
                "tool_source": "eeglab_plot_erp / ERPimage",
                "official_anchor": "EEGLAB-STUDY-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
                "interpretation_scope": "Trial-level or subject-level sorting review.",
            },
            {
                "figure_type": "ersp_itc_summary",
                "figure_status": "conditional",
                "channel_or_roi": "Study channel or ROI",
                "latency_window": "Study epoch window",
                "frequency_window": "Study ERSP/ITC frequency range",
                "tool_source": "eeglab_plot_timefreq",
                "official_anchor": "EEGLAB-STUDY-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/study_data_visualization_tools.html",
                "interpretation_scope": "Group-level time-frequency summary.",
            },
            {
                "figure_type": "ci_contrast_plots",
                "figure_status": "conditional",
                "channel_or_roi": "Statistical contrast channel or ROI",
                "latency_window": "Contrast window",
                "frequency_window": "Contrast band when relevant",
                "tool_source": "eeglab_study_statistics",
                "official_anchor": "EEGLAB-STUDY-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/",
                "interpretation_scope": "Group contrast review.",
            },
            {
                "figure_type": "cluster_edge_visuals",
                "figure_status": "guidance_only",
                "channel_or_roi": "Cluster or edge set",
                "latency_window": "Cluster window",
                "frequency_window": "Cluster band",
                "tool_source": "eeglab_study_statistics",
                "official_anchor": "EEGLAB-ICCLUSTER-001 / EEGLAB-LIMO-001",
                "official_url": "https://eeglab.org/tutorials/10_Group_analysis/component_clustering_tools.html",
                "interpretation_scope": "Cluster review or edge visualization only.",
            },
        ],
        "ordered_branch_steps": [
            "project_plan",
            "plugin_check_bids_study",
            "single_subject_protocol_lock",
            "staged_study_preflight",
            "study_create",
            "study_design",
            "study_statistics",
            "study_figures",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "required_steps": [
            "project_plan",
            "plugin_check_bids_study",
            "single_subject_protocol_lock",
            "staged_study_preflight",
            "study_create",
            "study_design",
            "study_statistics",
            "save_derivative",
            "protocol_export",
            "final_report",
        ],
        "conditional_steps": [
            "study_precompute_if_measures_are_claimed",
            "ica_clustering_if_claimed",
            "plugin_check_limo_or_sift_if_needed",
        ],
        "forbidden_steps": [
            "direct_group_statistics_before_single_subject_lock",
            "skip_design_variables",
            "claim_precompute_or_clustering_without_evidence",
            "overwrite_raw_input",
        ],
        "required_figures": [
            "eeglab_plot_erp",
        ],
        "conditional_figures": [
            "eeglab_plot_psd",
            "eeglab_plot_timefreq",
            "eeglab_plot_connectivity",
            "eeglab_plot_components",
        ],
        "required_figure_families": [
            "study_group_figures",
        ],
        "conditional_figure_families": [
            "erp_waveform",
            "scalp_topography",
            "psd_spectra",
            "ersp_itc_heatmap",
            "connectivity_matrix",
            "ica_component_diagnostics",
            "trial_erp_image",
        ],
        "guidance_only_figure_families": [],
        "required_outputs": [
            "study_derivatives",
            "protocol_export",
            "final_report",
        ],
        "branch_notes": [
            "Lock single-subject preprocessing before group claims.",
            "Treat STUDY precompute and ICA clustering as conditional and explicitly reported claims.",
        ],
    },
}


def resolve_branch_workflow_key(analysis_type: str = "") -> str:
    """Map an analysis type to a canonical branch workflow key."""
    key = str(analysis_type).strip().lower()
    if key in BRANCH_WORKFLOW_MATRIX:
        return key
    for branch_key, branch in BRANCH_WORKFLOW_MATRIX.items():
        aliases = {branch_key, *(str(alias).strip().lower() for alias in branch.get("analysis_type_aliases", []))}
        if key in aliases:
            return branch_key
    return key or "erp"


def _unique_strings(values: list[Any]) -> list[str]:
    """Return non-empty strings in first-seen order."""
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def branch_workflow_details(
    analysis_type: str = "",
    *,
    completed_steps: list[str] | None = None,
    figure_paths: list[str] | None = None,
    output_paths: list[str] | None = None,
    blocker_messages: list[str] | None = None,
    required_outputs: list[str] | None = None,
    branch_variant: str | None = None,
) -> dict[str, Any]:
    """Return the canonical branch matrix plus completeness bookkeeping."""
    branch_key = resolve_branch_workflow_key(analysis_type)
    matrix = dict(BRANCH_WORKFLOW_MATRIX.get(branch_key, BRANCH_WORKFLOW_MATRIX["erp"]))
    universal = list(UNIVERSAL_WORKFLOW_STEPS)
    ordered_branch_steps = list(matrix.get("ordered_branch_steps", []))
    required_steps = list(matrix.get("required_steps", []))
    completed_steps = _unique_strings(completed_steps or [])
    figure_paths = _unique_strings(figure_paths or [])
    output_paths = _unique_strings(output_paths or [])
    required_outputs = _unique_strings(required_outputs or list(matrix.get("required_outputs", [])))
    missing_required_steps = [step for step in universal + required_steps if step not in completed_steps]
    blocked_steps = [step for step in matrix.get("forbidden_steps", []) if step in completed_steps]
    required_figures = list(matrix.get("required_figures", []))
    conditional_figures = list(matrix.get("conditional_figures", []))
    required_figure_families = list(matrix.get("required_figure_families", []))
    conditional_figure_families = list(matrix.get("conditional_figure_families", []))
    guidance_only_figure_families = list(matrix.get("guidance_only_figure_families", []))
    figure_atlas = list(matrix.get("figure_atlas", []))
    missing_required_figures = [fig for fig in required_figures if fig not in figure_paths]
    missing_required_outputs = [item for item in required_outputs if item not in output_paths]
    if blocker_messages:
        completeness_status = "blocked"
    elif blocked_steps:
        completeness_status = "blocked"
    elif not completed_steps:
        completeness_status = "planned"
    elif missing_required_steps or missing_required_figures or missing_required_outputs:
        completeness_status = "partial"
    else:
        completeness_status = "complete"

    branch_details = {
        **matrix,
        "analysis_type": analysis_type or branch_key,
        "branch_id": branch_key,
        "branch_variant": branch_variant or ("connectivity" if branch_key == "resting" and str(analysis_type).strip().lower() == "connectivity" else "standard"),
        "universal_preamble_steps": universal,
        "ordered_branch_steps": ordered_branch_steps,
        "required_steps": required_steps,
        "conditional_steps": list(matrix.get("conditional_steps", [])),
        "forbidden_steps": list(matrix.get("forbidden_steps", [])),
        "required_figures": required_figures,
        "conditional_figures": conditional_figures,
        "required_figure_families": required_figure_families,
        "conditional_figure_families": conditional_figure_families,
        "guidance_only_figure_families": guidance_only_figure_families,
        "figure_atlas": figure_atlas,
        "required_outputs": required_outputs,
        "completed_steps": completed_steps,
        "figure_paths": figure_paths,
        "output_paths": output_paths,
        "branch_completeness": {
            "status": completeness_status,
            "missing_required_steps": missing_required_steps,
            "blocked_steps": blocked_steps,
            "missing_required_figures": missing_required_figures,
            "missing_required_outputs": missing_required_outputs,
            "required_figures": required_figures,
            "conditional_figures": conditional_figures,
            "required_figure_families": required_figure_families,
            "conditional_figure_families": conditional_figure_families,
            "guidance_only_figure_families": guidance_only_figure_families,
            "figure_atlas": figure_atlas,
            "required_outputs": required_outputs,
            "completed_steps": completed_steps,
            "figure_paths": figure_paths,
            "output_paths": output_paths,
            "blocker_messages": list(blocker_messages or []),
            "coverage_notes": list(matrix.get("branch_notes", [])),
        },
    }
    return branch_details


METHOD_PROFILES: dict[str, dict[str, Any]] = {
    "epoch": {
        "aliases": ["erp", "epoch", "eeglab_epoch", "eeglab_erp_light_workflow"],
        "tool_names": ["eeglab_epoch", "eeglab_erp_light_workflow"],
        "source_claim_ids": ["EEGLAB-EVENT-001", "EEGLAB-STRUCT-001"],
        "requirements": [
            {
                "id": "confirmed_condition_events",
                "severity": "critical",
                "check": "confirmed_condition_events",
                "text": "Confirmed task-condition/trigger events are required for epoching.",
            },
            {
                "id": "no_boundary_epoching",
                "severity": "critical",
                "check": "no_only_nonanalysis_events",
                "text": "Boundary, impedance, excluded, or segment-only markers must not be used as ERP triggers.",
            },
            {
                "id": "epoch_windows_recorded",
                "severity": "advisory",
                "check": "epoch_windows_recorded",
                "text": "Epoch and baseline windows should be recorded.",
            },
        ],
        "not_recommended": ["Do not epoch around boundary, impedance, excluded, or segment-only markers."],
    },
    "timefreq": {
        "aliases": [
            "timefreq",
            "ersp",
            "itc",
            "eeglab_timefreq",
            "eeglab_plot_timefreq",
        ],
        "tool_names": ["eeglab_timefreq", "eeglab_plot_timefreq"],
        "source_claim_ids": [
            "EEGLAB-TF-001",
            "EEGLAB-EVENT-001",
            "EEGLAB-EPOCH-001",
        ],
        "requirements": [
            {
                "id": "confirmed_condition_events",
                "severity": "critical",
                "check": "confirmed_condition_events",
                "text": "ERSP/ITC needs confirmed event locking or a justified continuous-data design.",
            },
            {
                "id": "baseline_recorded",
                "severity": "critical",
                "check": "baseline_recorded",
                "text": "Baseline settings must be specified and recorded.",
            },
            {
                "id": "frequency_settings_recorded",
                "severity": "advisory",
                "check": "frequency_settings_recorded",
                "text": "Frequency range and cycles/wavelet settings should be recorded.",
            },
        ],
        "not_recommended": ["Do not report ERSP/ITC effects without event/baseline/frequency settings."],
    },
    "clean_rawdata": {
        "aliases": ["clean_rawdata", "asr", "eeglab_clean_rawdata"],
        "tool_names": ["eeglab_clean_rawdata"],
        "source_claim_ids": ["EEGLAB-ASR-001"],
        "requirements": [
            {
                "id": "continuous_data",
                "severity": "critical",
                "check": "continuous_data",
                "text": "clean_rawdata/ASR should operate on continuous data unless a justified exception is recorded.",
            },
            {
                "id": "plugin_clean_rawdata_available",
                "severity": "critical",
                "check": "plugin_clean_rawdata_available",
                "text": "clean_rawdata plugin/function must be available.",
            },
            {
                "id": "thresholds_recorded",
                "severity": "critical",
                "check": "thresholds_recorded",
                "text": "ASR/bad-channel thresholds must be recorded.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Cleaned output must be treated as a derivative, not a raw overwrite.",
            },
        ],
        "not_recommended": ["Do not apply ASR to epoched-only data without explicit override and rationale."],
    },
    "run_ica": {
        "aliases": ["ica", "run_ica", "eeglab_run_ica"],
        "tool_names": ["eeglab_run_ica"],
        "source_claim_ids": ["EEGLAB-ICA-001"],
        "requirements": [
            {
                "id": "continuous_data",
                "severity": "critical",
                "check": "continuous_data",
                "text": "ICA normally requires suitable continuous data or a justified design.",
            },
            {
                "id": "rank_reference_reviewed",
                "severity": "critical",
                "check": "rank_reference_reviewed",
                "text": "Rank/reference decisions must be reviewed before ICA.",
            },
            {
                "id": "bad_channel_policy_defined",
                "severity": "critical",
                "check": "bad_channel_policy_defined",
                "text": "Bad-channel handling policy must be defined before ICA.",
            },
        ],
        "not_recommended": ["Do not run ICA casually on epoched-only data or after unresolved rank/reference changes."],
    },
    "iclabel": {
        "aliases": [
            "iclabel",
            "classify_ica",
            "flag_components",
            "eeglab_classify_ica",
            "eeglab_flag_components",
        ],
        "tool_names": ["eeglab_classify_ica", "eeglab_flag_components"],
        "source_claim_ids": ["EEGLAB-ICLABEL-001"],
        "requirements": [
            {
                "id": "has_ica",
                "severity": "critical",
                "check": "has_ica",
                "text": "ICA weights must exist before ICLabel classification.",
            },
            {
                "id": "plugin_iclabel_available",
                "severity": "critical",
                "check": "plugin_iclabel_available",
                "text": "ICLabel plugin/function must be available.",
            },
        ],
        "not_recommended": ["Do not interpret ICLabel probabilities as automatic removal decisions without review."],
    },
    "remove_components": {
        "aliases": ["remove_components", "subcomp", "eeglab_remove_components"],
        "tool_names": ["eeglab_remove_components"],
        "source_claim_ids": ["EEGLAB-ICLABEL-001"],
        "requirements": [
            {
                "id": "has_ica",
                "severity": "critical",
                "check": "has_ica",
                "text": "ICA weights must exist before component removal.",
            },
            {
                "id": "component_reviewed",
                "severity": "critical",
                "check": "component_reviewed",
                "text": "Components must be reviewed or explicit thresholds recorded before removal.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Component-removed output must be saved as a derivative.",
            },
        ],
        "not_recommended": ["Do not auto-remove components without threshold/rationale reporting."],
    },
    "source": {
        "aliases": [
            "source",
            "dipfit",
            "source_localization",
            "eeglab_source_localization",
            "eeglab_source_settings",
        ],
        "tool_names": ["eeglab_source_localization", "eeglab_source_settings"],
        "source_claim_ids": ["EEGLAB-DIPFIT-001", "EEGLAB-CHANLOC-001"],
        "requirements": [
            {
                "id": "has_ica",
                "severity": "critical",
                "check": "has_ica",
                "text": "ICA/source components or an explicit source model must exist.",
            },
            {
                "id": "has_channel_locations",
                "severity": "critical",
                "check": "has_channel_locations",
                "text": "Channel locations must be complete and appropriate.",
            },
            {
                "id": "plugin_dipfit_available",
                "severity": "critical",
                "check": "plugin_dipfit_available",
                "text": "DIPFIT resources must be available.",
            },
            {
                "id": "head_model_defined",
                "severity": "critical",
                "check": "head_model_defined",
                "text": "Head model/template assumptions must be defined.",
            },
        ],
        "not_recommended": ["Do not make anatomical certainty claims from missing montage/model prerequisites."],
    },
    "bids_import": {
        "aliases": [
            "bids",
            "bids_import",
            "import_bids",
            "eeglab_import_bids",
        ],
        "tool_names": ["eeglab_import_bids"],
        "source_claim_ids": [
            "EEGLAB-BIDS-001",
            "EEGLAB-IMPORT-001",
            "BIDS-EEG-001",
            "BIDS-EVENTS-001",
        ],
        "requirements": [
            {
                "id": "bids_or_sidecars_available",
                "severity": "critical",
                "check": "bids_or_sidecars_available",
                "text": "BIDS import requires a BIDS root, sidecars, or an explicit BIDS metadata path.",
            },
            {
                "id": "plugin_eegbids_available",
                "severity": "critical",
                "check": "plugin_eegbids_available",
                "text": "EEG-BIDS/pop_importbids must be available before BIDS import.",
            },
            {
                "id": "bids_events_have_onset_duration",
                "severity": "advisory",
                "check": "bids_events_have_onset_duration",
                "text": "events.tsv onset and duration columns should be confirmed before treating imported events as BIDS-valid.",
            },
        ],
        "not_recommended": [
            "Do not treat a BIDS import as analysis-ready until acquisition, event, and sidecar metadata gates are also reviewed."
        ],
    },
    "study_create": {
        "aliases": [
            "study_create",
            "eeglab_study_create",
        ],
        "tool_names": ["eeglab_study_create"],
        "source_claim_ids": [
            "EEGLAB-BIDS-001",
            "EEGLAB-STUDY-001",
            "EEGLAB-COURSE-001",
        ],
        "requirements": [
            {
                "id": "multi_subject_or_bids",
                "severity": "critical",
                "check": "multi_subject_or_bids",
                "text": "STUDY creation requires multi-subject datasets or a BIDS/STUDY project structure.",
            },
            {
                "id": "single_subject_protocol_locked",
                "severity": "advisory",
                "check": "single_subject_protocol_locked",
                "text": "Single-subject preprocessing protocol should be locked before treating the STUDY as statistics-ready.",
            },
        ],
        "not_recommended": [
            "Do not treat STUDY creation as approval for group statistics; design and statistics gates remain separate."
        ],
    },
    "study_design": {
        "aliases": [
            "study_design",
            "eeglab_study_design",
        ],
        "tool_names": ["eeglab_study_design"],
        "source_claim_ids": ["EEGLAB-STUDY-001", "EEGLAB-COURSE-001"],
        "requirements": [
            {
                "id": "multi_subject_or_bids",
                "severity": "critical",
                "check": "multi_subject_or_bids",
                "text": "STUDY design requires multi-subject or BIDS/STUDY organization.",
            },
            {
                "id": "design_variables_defined",
                "severity": "critical",
                "check": "design_variables_defined",
                "text": "Design variables and levels must be defined before creating a STUDY design.",
            },
            {
                "id": "single_subject_protocol_locked",
                "severity": "advisory",
                "check": "single_subject_protocol_locked",
                "text": "Single-subject preprocessing protocol should be locked before design-level interpretation.",
            },
        ],
        "not_recommended": [
            "Do not interpret a design until subject/session metadata and preprocessing assumptions are documented."
        ],
    },
    "study_statistics": {
        "aliases": [
            "study_statistics",
            "eeglab_study_statistics",
        ],
        "tool_names": ["eeglab_study_statistics"],
        "source_claim_ids": [
            "EEGLAB-STUDY-001",
            "EEGLAB-COURSE-001",
        ],
        "requirements": [
            {
                "id": "multi_subject_or_bids",
                "severity": "critical",
                "check": "multi_subject_or_bids",
                "text": "STUDY/group analysis needs multi-subject or BIDS/STUDY organization.",
            },
            {
                "id": "single_subject_protocol_locked",
                "severity": "critical",
                "check": "single_subject_protocol_locked",
                "text": "Single-subject preprocessing protocol must be locked before group statistics.",
            },
            {
                "id": "design_variables_defined",
                "severity": "critical",
                "check": "design_variables_defined",
                "text": "Design variables and levels must be defined.",
            },
            {
                "id": "study_measure_recorded",
                "severity": "critical",
                "check": "study_measure_recorded",
                "text": "The STUDY measure/precomputed measure family must be recorded before statistics.",
            },
            {
                "id": "correction_policy_recorded",
                "severity": "critical",
                "check": "correction_policy_recorded",
                "text": "Alpha and multiple-comparison correction policy must be recorded before group statistics.",
            },
        ],
        "not_recommended": [
            "Do not run group statistics before design variables and preprocessing assumptions are locked."
        ],
    },
    "study_precompute": {
        "aliases": [
            "study_precompute",
            "precompute",
            "std_precomp",
            "study_measures",
            "study_visualization",
        ],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-STUDY-001", "EEGLAB-STUDY-PRECOMP-001"],
        "requirements": [
            {
                "id": "multi_subject_or_bids",
                "severity": "critical",
                "check": "multi_subject_or_bids",
                "text": "STUDY precompute requires a multi-subject/BIDS STUDY project.",
            },
            {
                "id": "design_variables_defined",
                "severity": "critical",
                "check": "design_variables_defined",
                "text": "STUDY design variables should be known before precomputing group measures.",
            },
            {
                "id": "single_subject_protocol_locked",
                "severity": "critical",
                "check": "single_subject_protocol_locked",
                "text": "Single-subject preprocessing protocol must be locked before group measure precompute.",
            },
            {
                "id": "study_measure_recorded",
                "severity": "critical",
                "check": "study_measure_recorded",
                "text": "Precomputed STUDY measure family and parameters must be recorded.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Precomputed measure outputs must be stored as derivatives.",
            },
        ],
        "not_recommended": [
            "Do not interpret STUDY plots or statistics until the relevant measures have been precomputed and recorded."
        ],
    },
    "ica_clustering": {
        "aliases": [
            "ica_clustering",
            "component_clustering",
            "study_clustering",
            "cluster_ics",
        ],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-STUDY-001",
            "EEGLAB-STUDY-PRECOMP-001",
            "EEGLAB-ICCLUSTER-001",
            "EEGLAB-ICA-001",
        ],
        "requirements": [
            {
                "id": "multi_subject_or_bids",
                "severity": "critical",
                "check": "multi_subject_or_bids",
                "text": "ICA clustering is a STUDY/group workflow and requires multi-subject organization.",
            },
            {
                "id": "has_ica",
                "severity": "critical",
                "check": "has_ica",
                "text": "Subject-level ICA decompositions must exist before ICA clustering.",
            },
            {
                "id": "study_measure_recorded",
                "severity": "critical",
                "check": "study_measure_recorded",
                "text": "Clustering measure/feature family must be recorded.",
            },
            {
                "id": "clustering_policy_recorded",
                "severity": "critical",
                "check": "clustering_policy_recorded",
                "text": "Clustering features, distance metric, cluster count/algorithm, and outlier policy must be recorded.",
            },
            {
                "id": "component_reviewed",
                "severity": "advisory",
                "check": "component_reviewed",
                "text": "Cluster/component review criteria should be documented before interpretation.",
            },
        ],
        "not_recommended": [
            "Do not treat ICA clusters as anatomical sources without source/head-model assumptions and review."
        ],
    },
    "study": {
        "aliases": ["study", "study_ready_check", "bids_study"],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-BIDS-001",
            "EEGLAB-STUDY-001",
            "EEGLAB-COURSE-001",
        ],
        "requirements": [
            {
                "id": "multi_subject_or_bids",
                "severity": "critical",
                "check": "multi_subject_or_bids",
                "text": "STUDY/group analysis needs multi-subject or BIDS/STUDY organization.",
            },
            {
                "id": "single_subject_protocol_locked",
                "severity": "critical",
                "check": "single_subject_protocol_locked",
                "text": "Single-subject preprocessing protocol must be locked before group statistics.",
            },
            {
                "id": "design_variables_defined",
                "severity": "critical",
                "check": "design_variables_defined",
                "text": "Design variables and levels must be defined.",
            },
        ],
        "not_recommended": [
            "Do not run group statistics before design variables and preprocessing assumptions are locked."
        ],
    },
    "derivative_processing": {
        "aliases": [
            "filter",
            "resample",
            "reref",
            "reject_epochs",
            "line_noise",
            "eeglab_filter",
            "eeglab_resample",
            "eeglab_reref",
            "eeglab_reject_epochs",
            "eeglab_clean_line_noise",
        ],
        "tool_names": [
            "eeglab_filter",
            "eeglab_resample",
            "eeglab_reref",
            "eeglab_reject_epochs",
            "eeglab_clean_line_noise",
        ],
        "source_claim_ids": [
            "EEGLAB-FILT-001",
            "EEGLAB-RESAMPLE-001",
            "EEGLAB-REREF-001",
            "EEGLAB-REJECT-001",
            "EEGLAB-FUNC-001",
        ],
        "requirements": [
            {
                "id": "raw_input_preserved",
                "severity": "critical",
                "check": "raw_input_preserved",
                "text": "Raw input must be preserved before destructive preprocessing.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Derivative output path/strategy must be planned.",
            },
            {
                "id": "parameters_recorded",
                "severity": "advisory",
                "check": "parameters_recorded",
                "text": "Processing parameters should be recorded in the report/protocol.",
            },
        ],
        "not_recommended": ["Do not overwrite raw data after filtering/resampling/rereferencing/rejection."],
    },
    "acquisition_provenance": {
        "aliases": [
            "acquisition",
            "acquisition_metadata",
            "recording_metadata",
            "provenance",
            "raw_preservation",
        ],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-IMPORT-001",
            "EEGLAB-STRUCT-001",
            "BIDS-EEG-001",
        ],
        "requirements": [
            {
                "id": "raw_input_preserved",
                "severity": "critical",
                "check": "raw_input_preserved",
                "text": "Original EEG recordings and source sidecars must be preserved read-only.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Destructive processing must write to a derivative output path.",
            },
            {
                "id": "reference_or_montage_recorded",
                "severity": "critical",
                "check": "reference_or_montage_recorded",
                "text": "Reference, ground, montage, or cap layout must be recorded or explicitly marked missing.",
            },
            {
                "id": "power_line_frequency_recorded",
                "severity": "critical",
                "check": "power_line_frequency_recorded",
                "text": "Power-line frequency must be recorded before line-noise, filtering, or analysis-ready claims.",
            },
            {
                "id": "acquisition_filters_recorded",
                "severity": "critical",
                "check": "acquisition_filters_recorded",
                "text": "Hardware/software acquisition filter notes must be recorded or explicitly marked unavailable.",
            },
            {
                "id": "task_or_acquisition_system_recorded",
                "severity": "advisory",
                "check": "task_or_acquisition_system_recorded",
                "text": "Task description and acquisition system should be recorded for reproducibility.",
            },
            {
                "id": "impedance_or_quality_recorded",
                "severity": "advisory",
                "check": "impedance_or_quality_recorded",
                "text": "Impedance or channel-quality notes should be recorded when available.",
            },
        ],
        "not_recommended": [
            "Do not claim a dataset is analysis-ready when acquisition reference, line frequency, acquisition filters, or raw/derivative policy are unknown."
        ],
    },
    "bids_metadata": {
        "aliases": [
            "bids_metadata",
            "bids_sidecars",
            "hed",
            "events_json",
            "eeglab_import_bids",
        ],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-BIDS-001",
            "EEGLAB-IMPORT-001",
            "BIDS-EEG-001",
            "BIDS-EVENTS-001",
        ],
        "requirements": [
            {
                "id": "bids_or_sidecars_available",
                "severity": "critical",
                "check": "bids_or_sidecars_available",
                "text": "BIDS/HED metadata work requires a BIDS path, events sidecars, HED tags, or an explicit event-code map.",
            },
            {
                "id": "bids_eeg_sidecar_complete",
                "severity": "critical",
                "check": "bids_eeg_sidecar_complete",
                "text": "BIDS EEG metadata should include *_eeg.json, *_channels.tsv, *_electrodes.tsv, and *_coordsystem.json or equivalent explicit provenance.",
            },
            {
                "id": "bids_events_have_onset_duration",
                "severity": "critical",
                "check": "bids_events_have_onset_duration",
                "text": "BIDS events.tsv must include onset and duration columns for event timing.",
            },
            {
                "id": "event_metadata_described",
                "severity": "critical",
                "check": "event_metadata_described",
                "text": "Condition/event semantics must be described by events.json, HED, or a validated lab codebook.",
            },
            {
                "id": "bids_event_columns_described",
                "severity": "critical",
                "check": "bids_event_columns_described",
                "text": "trial_type and additional events.tsv columns must have events.json descriptions before condition-level interpretation.",
            },
        ],
        "not_recommended": [
            "Do not infer condition semantics from events.tsv labels alone when sidecar descriptions are missing."
        ],
    },
    "bids_export": {
        "aliases": [
            "bids_export",
            "export_bids",
            "pop_exportbids",
            "bids_derivative",
            "bids_publication",
        ],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-BIDSEXPORT-001",
            "EEGLAB-BIDS-001",
            "BIDS-EEG-001",
            "BIDS-EVENTS-001",
        ],
        "requirements": [
            {
                "id": "plugin_eegbids_available",
                "severity": "critical",
                "check": "plugin_eegbids_available",
                "text": "EEG-BIDS export functions must be available before BIDS export claims.",
            },
            {
                "id": "bids_eeg_sidecar_complete",
                "severity": "critical",
                "check": "bids_eeg_sidecar_complete",
                "text": "BIDS export needs complete EEG/channel/electrode/coordinate metadata or documented equivalents.",
            },
            {
                "id": "bids_events_have_onset_duration",
                "severity": "critical",
                "check": "bids_events_have_onset_duration",
                "text": "Exported events must have onset and duration timing.",
            },
            {
                "id": "event_metadata_described",
                "severity": "critical",
                "check": "event_metadata_described",
                "text": "Event columns need events.json, HED, or codebook descriptions before BIDS export claims.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "BIDS export output must be a separate derivative/export directory.",
            },
            {
                "id": "software_versions_recorded",
                "severity": "advisory",
                "check": "software_versions_recorded",
                "text": "EEGLAB, plugin, and processing version/provenance should be recorded for exported derivatives.",
            },
        ],
        "not_recommended": [
            "Do not claim BIDS export support through this MCP without a dedicated export tool; keep it to planning/reporting unless implemented."
        ],
    },
    "import_plugins": {
        "aliases": [
            "import_plugins",
            "foreign_format_import",
            "biosig",
            "file_io",
            "file-io",
            "mff_import",
            "nwb_import",
            "brainvision_import",
            "bva_import",
        ],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-IMPORT-PLUGINS-001",
            "EEGLAB-IMPORT-001",
            "EEGLAB-MFF-001",
            "EEGLAB-NWB-001",
            "EEGLAB-BVA-001",
        ],
        "requirements": [
            {
                "id": "source_format_recorded",
                "severity": "critical",
                "check": "source_format_recorded",
                "text": "The source file format and importer path must be recorded before import-readiness claims.",
            },
            {
                "id": "plugin_import_available",
                "severity": "critical",
                "check": "plugin_import_available",
                "text": "The plugin/function needed for the requested non-native import format must be available.",
            },
            {
                "id": "import_event_channel_mapping_recorded",
                "severity": "critical",
                "check": "import_event_channel_mapping_recorded",
                "text": "Event and channel/header mapping assumptions must be recorded after plugin-dependent import.",
            },
            {
                "id": "raw_input_preserved",
                "severity": "critical",
                "check": "raw_input_preserved",
                "text": "Original files and sidecars must be preserved before import conversion or cleanup.",
            },
        ],
        "not_recommended": [
            "Do not treat plugin-imported event/channel metadata as validated until the mapping is reviewed."
        ],
    },
    "data_export": {
        "aliases": [
            "data_export",
            "export_data",
            "external_export",
            "brainvision_export",
            "bva_export",
            "mff_export",
            "nwb_export",
        ],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-EXPORT-001",
            "EEGLAB-MFF-001",
            "EEGLAB-NWB-001",
            "EEGLAB-BVA-001",
        ],
        "requirements": [
            {
                "id": "export_format_supported",
                "severity": "critical",
                "check": "export_format_supported",
                "text": "The requested export format must be supported by built-in EEGLAB save or an available plugin/function.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Exported data must be written as a derivative, not over raw inputs.",
            },
            {
                "id": "export_metadata_complete",
                "severity": "critical",
                "check": "export_metadata_complete",
                "text": "Channel, event, header, and sidecar metadata needed by the target format must be complete or explicitly limited.",
            },
            {
                "id": "software_versions_recorded",
                "severity": "advisory",
                "check": "software_versions_recorded",
                "text": "EEGLAB, exporter/plugin, and processing version/provenance should be recorded for exported derivatives.",
            },
        ],
        "not_recommended": [
            "Do not claim non-.set export support through this MCP unless a dedicated export workflow and validation are added."
        ],
    },
    "hed_event_annotation": {
        "aliases": [
            "hed",
            "hed_tags",
            "hed_event_annotation",
            "hedtools",
            "event_annotation",
        ],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-HED-001", "BIDS-EVENTS-001"],
        "requirements": [
            {
                "id": "event_metadata_described",
                "severity": "critical",
                "check": "event_metadata_described",
                "text": "Event labels/columns must be described by HED, events.json, or a validated codebook.",
            },
            {
                "id": "hed_schema_recorded",
                "severity": "critical",
                "check": "hed_schema_recorded",
                "text": "HED schema/version or equivalent event-codebook provenance must be recorded.",
            },
            {
                "id": "event_code_map_validated",
                "severity": "advisory",
                "check": "event_code_map_validated",
                "text": "Condition-code mapping should be validated before event-locked interpretation.",
            },
        ],
        "not_recommended": ["Do not treat HED tags as confirmed ERP triggers until condition semantics are validated."],
    },
    "history_scripting": {
        "aliases": [
            "history_scripting",
            "eeglab_history_script",
            "batch_script",
            "script_from_history",
        ],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-HISTORY-001", "EEGLAB-FUNC-001", "EEGLAB-PIPELINE-001"],
        "requirements": [
            {
                "id": "processing_history_recorded",
                "severity": "critical",
                "check": "processing_history_recorded",
                "text": "EEG.history or equivalent current-session processing history must be available.",
            },
            {
                "id": "script_from_history_reviewed",
                "severity": "critical",
                "check": "script_from_history_reviewed",
                "text": "History-derived scripts must be reviewed for paths, dataset state, parameters, and outputs.",
            },
            {
                "id": "parameters_recorded",
                "severity": "advisory",
                "check": "parameters_recorded",
                "text": "Script parameters should be explicit rather than hidden in GUI defaults.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "advisory",
                "check": "derivative_output_planned",
                "text": "Batch scripts should write derivative outputs rather than overwrite raw inputs.",
            },
        ],
        "not_recommended": [
            "Do not run copied GUI history as a batch protocol before reviewing paths, defaults, and output policy."
        ],
    },
    "event_script_modification": {
        "aliases": [
            "event_script_modification",
            "event_recode",
            "modify_events",
            "event_latency_shift",
            "urevent_repair",
        ],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-EVENTSCRIPT-001", "EEGLAB-STRUCT-001", "EEGLAB-EVENT-001"],
        "requirements": [
            {
                "id": "event_modification_rule_recorded",
                "severity": "critical",
                "check": "event_modification_rule_recorded",
                "text": "Event recoding, deletion, or latency-shift rules must be recorded before scripted event changes.",
            },
            {
                "id": "event_latency_units_recorded",
                "severity": "critical",
                "check": "event_latency_units_recorded",
                "text": "Event latency units and sampling-rate assumptions must be recorded before scripted latency edits.",
            },
            {
                "id": "urevent_preserved_or_relinked",
                "severity": "critical",
                "check": "urevent_preserved_or_relinked",
                "text": "urevent links must be preserved, relinked, or explicitly reported as a limitation.",
            },
            {
                "id": "event_metadata_described",
                "severity": "advisory",
                "check": "event_metadata_described",
                "text": "Modified event meanings should be documented by HED, events.json, behavioral logs, or a lab codebook.",
            },
        ],
        "not_recommended": [
            "Do not use scripted event modifications to create condition triggers without a validated codebook or behavioral log."
        ],
    },
    "channel_locations": {
        "aliases": [
            "channel_locations",
            "chanlocs",
            "montage",
            "interpolate_channels",
            "edit_channels",
            "eeglab_interpolate_channels",
            "eeglab_edit_channels",
        ],
        "tool_names": ["eeglab_interpolate_channels", "eeglab_edit_channels"],
        "source_claim_ids": ["EEGLAB-CHANLOC-001"],
        "requirements": [
            {
                "id": "has_channel_locations_or_repair_plan",
                "severity": "critical",
                "check": "has_channel_locations_or_repair_plan",
                "text": "Channel-location metadata must be available or a concrete montage repair/interpolation plan must be supplied.",
            },
            {
                "id": "parameters_recorded",
                "severity": "advisory",
                "check": "parameters_recorded",
                "text": "Channel-location file, rename map, interpolation method, and excluded channels should be recorded.",
            },
        ],
        "not_recommended": [
            "Do not interpret scalp maps, interpolation quality, or source locations without usable channel coordinates."
        ],
    },
    "line_noise": {
        "aliases": [
            "line_noise",
            "cleanline",
            "zapline",
            "eeglab_clean_line_noise",
        ],
        "tool_names": ["eeglab_clean_line_noise"],
        "source_claim_ids": ["EEGLAB-LINE-001", "EEGLAB-FILT-001"],
        "requirements": [
            {
                "id": "line_noise_parameters_recorded",
                "severity": "critical",
                "check": "line_noise_parameters_recorded",
                "text": "Line-noise frequency, method, and affected harmonics/windows must be recorded.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Line-noise-cleaned output must be treated as a derivative.",
            },
        ],
        "not_recommended": [
            "Do not apply 50/60 Hz cleanup without confirming the local mains frequency and reporting the method."
        ],
    },
    "spectral": {
        "aliases": ["spectral", "spectrum", "spectra", "resting", "eeglab_spectral"],
        "tool_names": ["eeglab_spectral"],
        "source_claim_ids": ["EEGLAB-SPECTRAL-001"],
        "requirements": [
            {
                "id": "frequency_settings_recorded",
                "severity": "critical",
                "check": "frequency_settings_recorded",
                "text": "Spectral analysis requires an explicit frequency range or band definition.",
            },
            {
                "id": "artifact_policy_recorded",
                "severity": "critical",
                "check": "artifact_policy_recorded",
                "text": "Artifact handling and data-shape suitability must be documented before spectral interpretation.",
            },
            {
                "id": "channels_recorded",
                "severity": "advisory",
                "check": "channels_recorded",
                "text": "Channels or ROIs should be recorded for spectra/band-power summaries.",
            },
        ],
        "not_recommended": [
            "Do not make resting-state claims from epoched-only derivatives unless the design explicitly supports it."
        ],
    },
    "connectivity": {
        "aliases": ["connectivity", "coherence", "plv", "eeglab_connectivity"],
        "tool_names": ["eeglab_connectivity"],
        "source_claim_ids": ["EEGLAB-SPECTRAL-001", "EEGLAB-SIFT-001"],
        "requirements": [
            {
                "id": "frequency_settings_recorded",
                "severity": "critical",
                "check": "frequency_settings_recorded",
                "text": "Connectivity requires an explicit frequency range and method.",
            },
            {
                "id": "artifact_policy_recorded",
                "severity": "critical",
                "check": "artifact_policy_recorded",
                "text": "Artifact policy and channel/ROI selection must be documented before connectivity interpretation.",
            },
            {
                "id": "connectivity_limits_recorded",
                "severity": "advisory",
                "check": "connectivity_limits_recorded",
                "text": "Sensor/source space, causality limits, and model assumptions should be reported.",
            },
        ],
        "not_recommended": [
            "Do not interpret sensor-level connectivity as anatomical connectivity without source/model validation."
        ],
    },
    "topography": {
        "aliases": ["topography", "topoplot", "scalp_map", "eeglab_topoplot"],
        "tool_names": ["eeglab_topoplot"],
        "source_claim_ids": ["EEGLAB-TOPO-001", "EEGLAB-CHANLOC-001"],
        "requirements": [
            {
                "id": "has_channel_locations",
                "severity": "critical",
                "check": "has_channel_locations",
                "text": "Topographic maps require usable channel locations.",
            },
            {
                "id": "parameters_recorded",
                "severity": "advisory",
                "check": "parameters_recorded",
                "text": "Topographic time/frequency window and plotting parameters should be recorded.",
            },
        ],
        "not_recommended": ["Do not produce or interpret scalp maps when channel locations are missing or incomplete."],
    },
    "limo_statistics": {
        "aliases": ["limo", "limo_statistics", "glm", "single_trial_model"],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-LIMO-001", "EEGLAB-STUDY-001"],
        "requirements": [
            {
                "id": "plugin_limo_available",
                "severity": "critical",
                "check": "plugin_limo_available",
                "text": "LIMO workflows require LIMO plugin availability.",
            },
            {
                "id": "statistical_design_defined",
                "severity": "critical",
                "check": "statistical_design_defined",
                "text": "First-level/second-level model, design variables, and contrasts must be defined.",
            },
            {
                "id": "correction_policy_recorded",
                "severity": "critical",
                "check": "correction_policy_recorded",
                "text": "Correction and alpha policy must be recorded before LIMO statistical claims.",
            },
        ],
        "not_recommended": [
            "Do not claim LIMO support from the MCP unless plugin availability and a dedicated model/reporting protocol are confirmed."
        ],
    },
    "amica_ica": {
        "aliases": ["amica", "runamica", "runamica15", "pop_runamica"],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-AMICA-001",
            "EEGLAB-ICA-001",
            "EEGLAB-PLUGIN-001",
        ],
        "requirements": [
            {
                "id": "plugin_amica_available",
                "severity": "critical",
                "check": "plugin_amica_available",
                "text": "AMICA plugin/functions must be available before AMICA-specific ICA claims.",
            },
            {
                "id": "continuous_data",
                "severity": "critical",
                "check": "continuous_data",
                "text": "AMICA should be planned on suitable continuous data unless a justified design is recorded.",
            },
            {
                "id": "rank_reference_reviewed",
                "severity": "critical",
                "check": "rank_reference_reviewed",
                "text": "Rank, PCA, and reference choices must be reviewed before AMICA.",
            },
            {
                "id": "compute_strategy_recorded",
                "severity": "critical",
                "check": "compute_strategy_recorded",
                "text": "AMICA compute strategy, output directory, and reproducibility settings must be recorded.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "AMICA outputs must be written to a derivative directory.",
            },
        ],
        "not_recommended": [
            "Do not route AMICA execution through generic ICA tools unless an AMICA-specific workflow and eval coverage are added."
        ],
    },
    "sift_connectivity": {
        "aliases": ["sift", "groupsift", "mvar", "granger", "source_connectivity"],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-SIFT-001"],
        "requirements": [
            {
                "id": "plugin_sift_available",
                "severity": "critical",
                "check": "plugin_sift_available",
                "text": "SIFT workflows require SIFT/groupSIFT plugin availability.",
            },
            {
                "id": "model_validation_recorded",
                "severity": "critical",
                "check": "model_validation_recorded",
                "text": "MVAR/source connectivity requires model order, stationarity, and validation reporting.",
            },
            {
                "id": "correction_policy_recorded",
                "severity": "advisory",
                "check": "correction_policy_recorded",
                "text": "SIFT statistics and multiple-comparison policy should be recorded.",
            },
        ],
        "not_recommended": [
            "Do not run or claim SIFT connectivity support through this MCP without a dedicated SIFT execution workflow."
        ],
    },
    "nsg_remote": {
        "aliases": ["nsg", "nsgportal", "pop_nsg", "remote_compute", "hpc"],
        "tool_names": [],
        "source_claim_ids": [
            "EEGLAB-NSG-001",
            "EEGLAB-PLUGIN-001",
            "EEGLAB-COURSE-001",
        ],
        "requirements": [
            {
                "id": "plugin_nsg_available",
                "severity": "critical",
                "check": "plugin_nsg_available",
                "text": "NSGportal plugin/functions must be available for NSG planning.",
            },
            {
                "id": "remote_compute_approved",
                "severity": "critical",
                "check": "remote_compute_approved",
                "text": "User approval, credentials policy, and data-upload policy must be explicit before remote compute.",
            },
            {
                "id": "job_provenance_recorded",
                "severity": "critical",
                "check": "job_provenance_recorded",
                "text": "Remote job parameters, upload/download paths, and reproducibility records must be planned.",
            },
        ],
        "not_recommended": [
            "Do not execute remote NSG jobs through this local MCP unless a dedicated secure integration is implemented."
        ],
    },
    "plugin_development": {
        "aliases": [
            "plugin_development",
            "design_plugin",
            "eegplugin",
            "eegplugin_authoring",
            "extension_authoring",
        ],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-PLUGIN-DEV-001", "EEGLAB-PLUGIN-001"],
        "requirements": [
            {
                "id": "plugin_goal_defined",
                "severity": "critical",
                "check": "plugin_goal_defined",
                "text": "The plugin goal, target user operation, and intended EEGLAB integration point must be defined.",
            },
            {
                "id": "eeglab_function_family_recorded",
                "severity": "critical",
                "check": "eeglab_function_family_recorded",
                "text": "The intended pop_/eeg_/low-level function family and GUI/command-line boundary must be recorded.",
            },
            {
                "id": "validation_plan_recorded",
                "severity": "advisory",
                "check": "validation_plan_recorded",
                "text": "A plugin validation, sample-data, and documentation plan should be recorded before claiming research support.",
            },
        ],
        "not_recommended": [
            "Do not treat plugin authoring guidance as support for executing a new analysis plugin through this MCP."
        ],
    },
    "relica_reliability": {
        "aliases": ["relica", "relica_reliability", "ica_reliability", "bootstrap_ica"],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-RELICA-001", "EEGLAB-ICA-001", "EEGLAB-PLUGIN-001"],
        "requirements": [
            {
                "id": "plugin_relica_available",
                "severity": "critical",
                "check": "plugin_relica_available",
                "text": "RELICA plugin/functions must be available before ICA reliability claims.",
            },
            {
                "id": "has_ica",
                "severity": "critical",
                "check": "has_ica",
                "text": "A subject-level ICA decomposition must exist before RELICA reliability review.",
            },
            {
                "id": "bootstrap_settings_recorded",
                "severity": "critical",
                "check": "bootstrap_settings_recorded",
                "text": "Bootstrap/resampling settings, number of decompositions, and compute strategy must be recorded.",
            },
            {
                "id": "component_reviewed",
                "severity": "advisory",
                "check": "component_reviewed",
                "text": "Components and reliability summaries should be reviewed before interpretation.",
            },
        ],
        "not_recommended": [
            "Do not claim RELICA reliability support unless plugin availability, ICA state, and bootstrap settings are explicit."
        ],
    },
    "viewprops_review": {
        "aliases": ["viewprops", "pop_viewprops", "component_properties", "component_review_view"],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-VIEWPROPS-001", "EEGLAB-ICLABEL-001", "EEGLAB-ICA-001"],
        "requirements": [
            {
                "id": "plugin_viewprops_available",
                "severity": "critical",
                "check": "plugin_viewprops_available",
                "text": "Viewprops plugin/functions must be available for Viewprops-specific review claims.",
            },
            {
                "id": "has_ica",
                "severity": "critical",
                "check": "has_ica",
                "text": "ICA weights must exist before component-property review.",
            },
            {
                "id": "component_reviewed",
                "severity": "advisory",
                "check": "component_reviewed",
                "text": "The reviewed component set and classifier/source evidence should be documented.",
            },
        ],
        "not_recommended": [
            "Do not substitute Viewprops availability for an ICA/ICLabel/component-removal review policy."
        ],
    },
    "get_chanlocs_digitization": {
        "aliases": [
            "get_chanlocs",
            "get_chanlocs_digitization",
            "electrode_digitization",
            "head_image_chanlocs",
        ],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-GETCHANLOCS-001", "EEGLAB-CHANLOC-001"],
        "requirements": [
            {
                "id": "plugin_get_chanlocs_available",
                "severity": "critical",
                "check": "plugin_get_chanlocs_available",
                "text": "get_chanlocs plugin/functions must be available before digitization claims.",
            },
            {
                "id": "head_image_or_digitization_source_recorded",
                "severity": "critical",
                "check": "head_image_or_digitization_source_recorded",
                "text": "3-D head images, electrode photos, or digitization source files must be recorded.",
            },
            {
                "id": "fiducials_recorded",
                "severity": "critical",
                "check": "fiducials_recorded",
                "text": "Fiducials and coordinate/reference assumptions must be recorded before channel-location repair claims.",
            },
            {
                "id": "channel_location_repair_planned",
                "severity": "advisory",
                "check": "channel_location_repair_planned",
                "text": "A plan for writing/reviewing EEG.chanlocs should be documented.",
            },
        ],
        "not_recommended": [
            "Do not claim source/topography readiness from get_chanlocs until channel coordinates are reviewed in EEG.chanlocs."
        ],
    },
    "roiconnect_source_connectivity": {
        "aliases": ["roiconnect", "roi_connectivity", "source_roi_connectivity", "roi_connect"],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-ROICONNECT-001", "EEGLAB-DIPFIT-001", "EEGLAB-SPECTRAL-001"],
        "requirements": [
            {
                "id": "plugin_roiconnect_available",
                "severity": "critical",
                "check": "plugin_roiconnect_available",
                "text": "ROIconnect plugin/functions must be available before ROIconnect-specific claims.",
            },
            {
                "id": "source_model_available",
                "severity": "critical",
                "check": "source_model_available",
                "text": "A source model or source-level ROI activity representation must be available.",
            },
            {
                "id": "roi_atlas_recorded",
                "severity": "critical",
                "check": "roi_atlas_recorded",
                "text": "ROI atlas/parcellation and region selection must be recorded.",
            },
            {
                "id": "connectivity_metric_recorded",
                "severity": "critical",
                "check": "connectivity_metric_recorded",
                "text": "Connectivity metric, frequency/time window, and statistical interpretation limits must be recorded.",
            },
        ],
        "not_recommended": [
            "Do not interpret ROIconnect outputs as anatomical connectivity without source-model, atlas, and statistics validation."
        ],
    },
    "eegstats_metrics": {
        "aliases": ["eegstats", "eegstats_metrics", "band_power_stats", "alpha_peak", "alpha_asymmetry"],
        "tool_names": [],
        "source_claim_ids": ["EEGLAB-EEGSTATS-001", "EEGLAB-SPECTRAL-001", "EEGLAB-STUDY-001"],
        "requirements": [
            {
                "id": "plugin_eegstats_available",
                "severity": "critical",
                "check": "plugin_eegstats_available",
                "text": "EEGstats plugin/functions must be available before EEGstats-specific claims.",
            },
            {
                "id": "frequency_settings_recorded",
                "severity": "critical",
                "check": "frequency_settings_recorded",
                "text": "Band definitions, alpha-peak search range, or frequency settings must be recorded.",
            },
            {
                "id": "channels_recorded",
                "severity": "critical",
                "check": "channels_recorded",
                "text": "Channels, ROIs, or STUDY component sets must be recorded for band-power/asymmetry metrics.",
            },
            {
                "id": "artifact_policy_recorded",
                "severity": "advisory",
                "check": "artifact_policy_recorded",
                "text": "Artifact policy and cleaned-data scope should be recorded before interpreting summary metrics.",
            },
        ],
        "not_recommended": [
            "Do not claim EEGstats results through this MCP unless plugin availability and metric settings are documented."
        ],
    },
    "pipeline": {
        "aliases": ["pipeline", "eeglab_pipeline"],
        "tool_names": ["eeglab_pipeline"],
        "source_claim_ids": [
            "EEGLAB-PIPELINE-001",
            "EEGLAB-ASR-001",
            "EEGLAB-ICA-001",
            "EEGLAB-EVENT-001",
        ],
        "requirements": [
            {
                "id": "raw_input_preserved",
                "severity": "critical",
                "check": "raw_input_preserved",
                "text": "Raw input must be preserved before pipeline execution.",
            },
            {
                "id": "derivative_output_planned",
                "severity": "critical",
                "check": "derivative_output_planned",
                "text": "Pipeline output must go to a derivative directory.",
            },
            {
                "id": "pipeline_defaults_accepted",
                "severity": "critical",
                "check": "pipeline_defaults_accepted",
                "text": "The user must accept bundled defaults before one-click pipeline execution.",
            },
        ],
        "not_recommended": [
            "Do not use one-click pipelines when the user needs transparent parameter-by-parameter control."
        ],
    },
}


TOOL_TO_PROFILE: dict[str, str] = {
    tool_name: profile_id for profile_id, profile in METHOD_PROFILES.items() for tool_name in profile["tool_names"]
}


HIGH_RISK_TOOL_NAMES = set(TOOL_TO_PROFILE)


def _ctx_truthy(context: dict[str, Any], *names: str) -> bool:
    for name in names:
        value = context.get(name)
        if isinstance(value, str):
            if value.strip():
                return True
        elif isinstance(value, (list, dict, tuple, set)):
            if len(value) > 0:
                return True
        elif value:
            return True
    return False


def _ctx_any_present(context: dict[str, Any], *names: str) -> bool:
    """Return true when a field was explicitly supplied, including false/0 values."""
    return any(name in context and context.get(name) is not None for name in names)


def _plugins_include(context: dict[str, Any], *names: str) -> bool:
    plugin_values = context.get("plugins_available") or context.get("available_plugins") or []
    normalized = {str(item).lower() for item in plugin_values} if isinstance(plugin_values, list) else set()
    return any(_ctx_truthy(context, f"plugin_{name.lower()}_available") or name.lower() in normalized for name in names)


def _field_recorded_or_documented_missing(context: dict[str, Any], field_name: str, *aliases: str) -> bool:
    """Return true when metadata exists or its absence was explicitly recorded."""
    documented_missing = context.get("documented_missing_fields") or context.get("missing_metadata_documented") or []
    if isinstance(documented_missing, str):
        raw_missing = documented_missing.replace(";", ",").split(",")
    elif isinstance(documented_missing, dict):
        raw_missing = [key for key, value in documented_missing.items() if value]
    elif isinstance(documented_missing, (list, tuple, set)):
        raw_missing = list(documented_missing)
    else:
        raw_missing = [documented_missing]
    missing_keys = {str(item).strip().lower() for item in raw_missing if str(item).strip()}
    normalized = {field_name.lower(), *(alias.lower() for alias in aliases)}
    if missing_keys & normalized:
        return True
    return _ctx_truthy(context, field_name, *aliases)


def _sidecars_include(context: dict[str, Any], *names: str) -> bool:
    sidecars = context.get("sidecars") or context.get("sidecar_paths") or []
    if isinstance(sidecars, dict):
        haystack = {str(key).lower() for key, value in sidecars.items() if value}
        haystack.update(str(value).lower() for value in sidecars.values() if value)
    elif isinstance(sidecars, list):
        haystack = {str(item).lower() for item in sidecars}
    else:
        haystack = set()
    normalized_names = [name.lower() for name in names]
    return any(item == name or item.endswith(name) or name in item for item in haystack for name in normalized_names)


def _event_roles(context: dict[str, Any]) -> set[str]:
    roles = context.get("event_roles") or context.get("marker_roles") or []
    if isinstance(roles, dict):
        roles = list(roles.values())
    return {str(role).strip().lower() for role in roles if str(role).strip()}


def _check_requirement(check: str, context: dict[str, Any]) -> bool:
    if check == "confirmed_condition_events":
        roles = _event_roles(context)
        return _ctx_truthy(
            context,
            "confirmed_condition_events",
            "condition_markers",
            "analysis_event_types",
        ) or bool(roles & {"condition", "trigger", "task_condition", "stimulus"})
    if check == "no_only_nonanalysis_events":
        roles = _event_roles(context)
        if not roles:
            return True
        nonanalysis = {
            "boundary",
            "impedance",
            "segment_marker",
            "excluded",
            "qc_annotation",
        }
        return not roles.issubset(nonanalysis)
    if check == "epoch_windows_recorded":
        return _ctx_truthy(context, "epoch_window", "baseline_window", "epoch_windows_recorded")
    if check == "baseline_recorded":
        return _ctx_truthy(context, "baseline", "baseline_window", "baseline_recorded")
    if check == "frequency_settings_recorded":
        return _ctx_truthy(context, "freq_range", "cycles", "frequency_settings_recorded")
    if check == "continuous_data":
        data_shape = str(context.get("data_shape", "")).lower()
        return (
            data_shape in {"continuous", "continuous_or_single_trial", "single_trial"}
            or context.get("has_continuous_raw") is True
        )
    if check == "plugin_clean_rawdata_available":
        return _plugins_include(context, "clean_rawdata", "pop_clean_rawdata")
    if check == "plugin_iclabel_available":
        return _plugins_include(context, "iclabel", "pop_iclabel")
    if check == "plugin_dipfit_available":
        return _plugins_include(context, "dipfit", "pop_dipfit_settings")
    if check == "plugin_eegbids_available":
        return _plugins_include(context, "eeg-bids", "eegbids", "pop_importbids")
    if check == "thresholds_recorded":
        return _ctx_truthy(context, "thresholds_recorded", "asr_thresholds", "burst_criterion")
    if check == "derivative_output_planned":
        return _ctx_truthy(
            context,
            "derivative_output_planned",
            "output_path_separate",
            "output_dir",
            "output_path",
        )
    if check == "rank_reference_reviewed":
        return _ctx_truthy(context, "rank_reference_reviewed", "rank_reviewed", "reference_reviewed")
    if check == "bad_channel_policy_defined":
        return _ctx_truthy(
            context,
            "bad_channel_policy_defined",
            "bad_channels_reviewed",
            "bad_channel_policy",
        )
    if check == "has_ica":
        return _ctx_truthy(context, "has_ica", "ica_computed", "ica_weights_present")
    if check == "component_reviewed":
        return _ctx_truthy(
            context,
            "component_reviewed",
            "iclabel_reviewed",
            "component_review_policy",
            "component_indices",
        )
    if check == "has_channel_locations":
        return context.get("has_channel_locations") is True or context.get("channel_location_coverage") in {
            1,
            1.0,
            "complete",
        }
    if check == "has_channel_locations_or_repair_plan":
        return _check_requirement("has_channel_locations", context) or _ctx_truthy(
            context,
            "channel_location_repair_planned",
            "loc_file",
            "ref_chanlocs",
            "rename_map",
        )
    if check == "head_model_defined":
        return _ctx_truthy(context, "head_model", "template", "head_model_defined")
    if check == "multi_subject_or_bids":
        scale = str(context.get("project_scale", "")).lower()
        return scale in {"multi_subject", "bids_study", "bids"} or _ctx_truthy(context, "bids_path", "dataset_paths")
    if check == "single_subject_protocol_locked":
        return _ctx_truthy(context, "single_subject_protocol_locked", "preprocessing_protocol_locked")
    if check == "design_variables_defined":
        return _ctx_truthy(
            context,
            "design_variables_defined",
            "design_variables",
            "variable_name",
            "variable_values",
        )
    if check == "study_measure_recorded":
        return _ctx_truthy(
            context,
            "study_measure_recorded",
            "measure",
            "measure_type",
            "precomputed_measure",
            "erp_measure",
            "ersp_measure",
        )
    if check == "raw_input_preserved":
        return context.get("raw_input_preserved") is True or context.get("input_preserved") is True
    if check == "parameters_recorded":
        return context.get("parameters_recorded") is True or _ctx_truthy(
            context, "parameters", "filter_cutoffs", "ref_type"
        )
    if check == "pipeline_defaults_accepted":
        return context.get("pipeline_defaults_accepted") is True
    if check == "reference_or_montage_recorded":
        return _field_recorded_or_documented_missing(
            context,
            "reference",
            "reference_or_montage",
            "montage",
            "ground",
            "cap_layout",
            "eeg_reference",
            "eeg_ground",
            "eeg_placement_scheme",
        )
    if check == "power_line_frequency_recorded":
        return _field_recorded_or_documented_missing(
            context,
            "power_line_frequency",
            "powerlinefrequency",
            "line_freq",
            "line_frequency",
        )
    if check == "acquisition_filters_recorded":
        return _field_recorded_or_documented_missing(
            context,
            "acquisition_filters",
            "hardware_filters",
            "software_filters",
            "hardware_filter",
            "software_filter",
        )
    if check == "task_or_acquisition_system_recorded":
        return _field_recorded_or_documented_missing(
            context,
            "task_name",
            "task_description",
            "acquisition_system",
            "manufacturer",
            "recording_system",
        )
    if check == "impedance_or_quality_recorded":
        return _field_recorded_or_documented_missing(
            context,
            "impedance",
            "impedance_notes",
            "channel_quality_notes",
            "quality_notes",
            "channels_status",
        )
    if check == "bids_or_sidecars_available":
        return _ctx_truthy(
            context,
            "bids_path",
            "events_json",
            "events_sidecar",
            "hed_tags",
            "event_code_map",
            "sidecar_paths",
        )
    if check == "bids_eeg_sidecar_complete":
        return context.get("bids_eeg_sidecar_complete") is True or (
            (_ctx_truthy(context, "eeg_json") or _sidecars_include(context, "eeg.json", "_eeg.json"))
            and (_ctx_truthy(context, "channels_tsv") or _sidecars_include(context, "channels.tsv", "_channels.tsv"))
            and (
                _ctx_truthy(context, "electrodes_tsv")
                or _sidecars_include(context, "electrodes.tsv", "_electrodes.tsv")
            )
            and (
                _ctx_truthy(context, "coordsystem_json")
                or _sidecars_include(context, "coordsystem.json", "_coordsystem.json")
            )
        )
    if check == "bids_events_have_onset_duration":
        columns = context.get("events_tsv_columns") or context.get("event_columns") or []
        column_set = {str(item).strip().lower() for item in columns}
        return context.get("events_have_onset_duration") is True or {
            "onset",
            "duration",
        }.issubset(column_set)
    if check == "event_metadata_described":
        return _ctx_truthy(
            context,
            "event_metadata_described",
            "events_json",
            "hed_tags",
            "event_code_map",
            "behavioral_log",
        )
    if check == "bids_event_columns_described":
        return (
            context.get("bids_event_columns_described") is True
            or context.get("trial_type_described") is True
            or _ctx_truthy(context, "events_json", "event_code_map", "hed_tags")
        )
    if check == "source_format_recorded":
        return _ctx_truthy(context, "source_format", "data_format", "input_format", "file_format", "input_path")
    if check == "plugin_import_available":
        source_format = (
            str(
                context.get("source_format")
                or context.get("data_format")
                or context.get("input_format")
                or context.get("file_format")
                or ""
            )
            .strip()
            .lower()
        )
        if source_format in {"", "set", ".set", "eeglab", "eeglab_set"} or source_format.endswith(".set"):
            return True
        if _ctx_truthy(context, "plugin_import_available", "import_plugin_available", "import_function_available"):
            return True
        format_plugins = {
            "edf": ("biosig", "pop_biosig"),
            "bdf": ("biosig", "pop_biosig"),
            "gdf": ("biosig", "pop_biosig"),
            "biosig": ("biosig", "pop_biosig"),
            "fieldtrip": ("file-io", "fileio", "pop_fileio"),
            "file-io": ("file-io", "fileio", "pop_fileio"),
            "fileio": ("file-io", "fileio", "pop_fileio"),
            "mff": ("mff-matlab-io", "mff", "mff_import"),
            "egi": ("mff-matlab-io", "mff", "mff_import"),
            "nwb": ("nwb-io", "nwbio", "nwb_import"),
            "brainvision": ("bva-io", "bva", "pop_loadbv"),
            "vhdr": ("bva-io", "bva", "pop_loadbv"),
            "vmrk": ("bva-io", "bva", "pop_loadbv"),
            "bva": ("bva-io", "bva", "pop_loadbv"),
            "bids": ("eeg-bids", "eegbids", "pop_importbids"),
        }
        for marker, plugins in format_plugins.items():
            if marker in source_format:
                return _plugins_include(context, *plugins)
        return False
    if check == "import_event_channel_mapping_recorded":
        return _ctx_truthy(
            context,
            "import_event_channel_mapping_recorded",
            "event_import_policy",
            "event_mapping",
            "channel_mapping",
            "header_mapping",
            "sidecar_paths",
            "events_json",
        )
    if check == "export_format_supported":
        output_format = (
            str(
                context.get("export_format")
                or context.get("target_format")
                or context.get("output_format")
                or context.get("file_format")
                or ""
            )
            .strip()
            .lower()
        )
        if output_format in {"set", ".set", "eeglab", "eeglab_set"} or output_format.endswith(".set"):
            return True
        if _ctx_truthy(context, "export_format_supported", "export_plugin_available", "export_function_available"):
            return True
        format_plugins = {
            "mff": ("mff-matlab-io", "mff", "mff_export"),
            "nwb": ("nwb-io", "nwbio", "nwb_export"),
            "brainvision": ("bva-io", "bva", "pop_writebva"),
            "vhdr": ("bva-io", "bva", "pop_writebva"),
            "bva": ("bva-io", "bva", "pop_writebva"),
            "bids": ("eeg-bids", "eegbids", "pop_exportbids"),
        }
        for marker, plugins in format_plugins.items():
            if marker in output_format:
                return _plugins_include(context, *plugins)
        return False
    if check == "export_metadata_complete":
        return (
            context.get("export_metadata_complete") is True
            or context.get("channel_event_metadata_complete") is True
            or context.get("header_metadata_complete") is True
            or (
                _check_requirement("bids_eeg_sidecar_complete", context)
                and _check_requirement("event_metadata_described", context)
            )
        )
    if check == "hed_schema_recorded":
        return _ctx_truthy(
            context,
            "hed_schema_recorded",
            "hed_schema_version",
            "hed_version",
            "hed_schema",
            "hed_library",
            "event_codebook_version",
        )
    if check == "event_code_map_validated":
        return _ctx_truthy(
            context,
            "event_code_map_validated",
            "validated_event_code_map",
            "codebook_validated",
            "behavioral_log",
            "events_json",
        )
    if check == "processing_history_recorded":
        return _ctx_truthy(
            context,
            "processing_history_recorded",
            "processing_history",
            "eeglab_history",
            "history_script",
            "EEG.history",
        )
    if check == "script_from_history_reviewed":
        return _ctx_truthy(
            context,
            "script_from_history_reviewed",
            "history_script_reviewed",
            "batch_script_reviewed",
            "script_parameters_reviewed",
        )
    if check == "event_modification_rule_recorded":
        return _ctx_truthy(
            context,
            "event_modification_rule_recorded",
            "event_modification_rule",
            "event_recode_table",
            "latency_shift_rule",
            "deleted_event_policy",
        )
    if check == "event_latency_units_recorded":
        return _ctx_truthy(
            context,
            "event_latency_units_recorded",
            "event_latency_units",
            "latency_units",
            "sampling_rate_hz",
            "srate",
        )
    if check == "urevent_preserved_or_relinked":
        urevent_status = str(context.get("urevent_link_status", "")).strip().lower()
        return (
            context.get("urevent_preserved") is True
            or context.get("urevent_relinked") is True
            or urevent_status in {"preserved", "relinked", "valid", "consistent"}
        )
    if check == "line_noise_parameters_recorded":
        return _ctx_truthy(context, "line_noise_parameters_recorded", "line_freq", "line_frequency") and _ctx_truthy(
            context, "line_noise_method", "method", "bandwidth"
        )
    if check == "artifact_policy_recorded":
        return _ctx_truthy(
            context,
            "artifact_policy_recorded",
            "artifact_policy",
            "rejection_policy",
            "cleaning_summary",
        )
    if check == "channels_recorded":
        return _ctx_truthy(context, "channels", "channel_set", "roi", "rois")
    if check == "connectivity_limits_recorded":
        return _ctx_truthy(
            context,
            "connectivity_limits_recorded",
            "connectivity_limits",
            "sensor_space_limit",
            "source_space",
            "model_assumptions",
        )
    if check == "plugin_limo_available":
        return _plugins_include(context, "limo", "pop_limo", "limo_eeg")
    if check == "plugin_sift_available":
        return _plugins_include(context, "sift", "groupsift", "eegplugin_sift")
    if check == "plugin_amica_available":
        return _plugins_include(context, "amica", "runamica15", "pop_runamica")
    if check == "plugin_nsg_available":
        return _plugins_include(context, "nsgportal", "pop_nsg", "nsgportal")
    if check == "plugin_relica_available":
        return _plugins_include(context, "relica", "pop_relica", "eegplugin_relica")
    if check == "plugin_viewprops_available":
        return _plugins_include(context, "viewprops", "pop_viewprops", "pop_prop_extended")
    if check == "plugin_get_chanlocs_available":
        return _plugins_include(context, "get_chanlocs", "eegplugin_getchanlocs")
    if check == "plugin_roiconnect_available":
        return _plugins_include(context, "roiconnect", "pop_roi_connect", "pop_roi_activity")
    if check == "plugin_eegstats_available":
        return _plugins_include(context, "eegstats", "pop_eegstats", "eegplugin_eegstats")
    if check == "statistical_design_defined":
        return _ctx_truthy(
            context,
            "statistical_design_defined",
            "design_matrix",
            "contrasts",
            "first_level_model",
            "second_level_model",
            "design_variables",
        )
    if check == "correction_policy_recorded":
        return _ctx_truthy(context, "correction_policy_recorded", "correction", "alpha", "mcc")
    if check == "model_validation_recorded":
        return _ctx_truthy(
            context,
            "model_validation_recorded",
            "model_order",
            "stationarity",
            "validation",
            "whiteness_test",
            "stability_test",
        )
    if check == "bootstrap_settings_recorded":
        return _ctx_truthy(
            context,
            "bootstrap_settings_recorded",
            "bootstrap",
            "bootstrap_samples",
            "n_bootstrap",
            "reliability_settings",
        )
    if check == "plugin_goal_defined":
        return _ctx_truthy(context, "plugin_goal_defined", "plugin_goal", "extension_goal", "user_story")
    if check == "eeglab_function_family_recorded":
        return _ctx_truthy(
            context,
            "eeglab_function_family_recorded",
            "function_family",
            "gui_boundary",
            "command_line_boundary",
            "pop_function",
        )
    if check == "validation_plan_recorded":
        return _ctx_truthy(
            context,
            "validation_plan_recorded",
            "validation_plan",
            "sample_data_plan",
            "documentation_plan",
            "test_plan",
        )
    if check == "head_image_or_digitization_source_recorded":
        return _ctx_truthy(
            context,
            "head_image_or_digitization_source_recorded",
            "head_image",
            "digitization_file",
            "fiducial_file",
            "electrode_photo",
        )
    if check == "fiducials_recorded":
        return _ctx_truthy(context, "fiducials_recorded", "fiducials", "nasion", "lpa", "rpa")
    if check == "source_model_available":
        return _ctx_truthy(context, "source_model_available", "source_model", "dipfit", "source_solution")
    if check == "roi_atlas_recorded":
        return _ctx_truthy(context, "roi_atlas_recorded", "roi_atlas", "atlas", "parcellation")
    if check == "connectivity_metric_recorded":
        return _ctx_truthy(
            context,
            "connectivity_metric_recorded",
            "connectivity_metric",
            "roi_connectivity_metric",
            "roi_metric",
            "method",
        )
    if check == "software_versions_recorded":
        return _ctx_truthy(
            context,
            "software_versions_recorded",
            "software_versions",
            "eeglab_version",
            "plugin_versions",
            "processing_history",
        )
    if check == "clustering_policy_recorded":
        return _ctx_truthy(
            context,
            "clustering_policy_recorded",
            "cluster_algorithm",
            "cluster_count",
            "n_clusters",
            "cluster_features",
            "distance_metric",
            "outlier_policy",
        )
    if check == "compute_strategy_recorded":
        return _ctx_truthy(
            context,
            "compute_strategy_recorded",
            "compute_strategy",
            "compute_plan",
            "amica_settings",
            "max_threads",
            "num_models",
        )
    if check == "remote_compute_approved":
        return (
            context.get("remote_compute_approved") is True
            or context.get("nsg_remote_approved") is True
            or context.get("data_upload_approved") is True
        )
    if check == "job_provenance_recorded":
        return _ctx_truthy(
            context,
            "job_provenance_recorded",
            "remote_job_parameters",
            "nsg_job_id",
            "upload_manifest",
            "download_plan",
            "credential_policy",
            "data_transfer_policy",
        )
    return False


def resolve_method_profile(method: str = "", tool_name: str = "") -> tuple[str, dict[str, Any] | None]:
    """Resolve a method/tool name to a gate profile."""
    if tool_name in TOOL_TO_PROFILE:
        profile_id = TOOL_TO_PROFILE[tool_name]
        return profile_id, METHOD_PROFILES[profile_id]
    method_key = str(method or tool_name).strip().lower()
    for profile_id, profile in METHOD_PROFILES.items():
        if method_key == profile_id or method_key in {alias.lower() for alias in profile["aliases"]}:
            return profile_id, profile
    return "", None


def evaluate_method_preflight(args: dict[str, Any]) -> dict[str, Any]:
    """Evaluate official-method gates without running MATLAB."""
    method = str(args.get("method", "") or "")
    tool_name = str(args.get("tool_name", "") or "")
    context = args.get("context") if isinstance(args.get("context"), dict) else {}
    strictness = str(args.get("strictness", "hard")).lower()
    override_reason = str(args.get("override_reason", "") or "").strip()

    profile_id, profile = resolve_method_profile(method, tool_name)
    if not profile:
        return {
            "method_profile_id": "",
            "gate_status": "unknown_method",
            "official_requirements": [],
            "missing_requirements": [],
            "not_recommended": [
                "Do not treat an unmapped method as officially aligned until it is added to the claim map."
            ],
            "safe_next_step": "Use a mapped method/tool name or update the official claim map before treating this workflow as supported.",
            "source_claim_ids": [],
            "override_used": False,
            "official_alignment": {
                "strictness": strictness,
                "source": "local_official_claim_map",
            },
        }

    official_requirements = profile["requirements"]
    missing = [req for req in official_requirements if not _check_requirement(req["check"], context)]
    critical_missing = [req for req in missing if req.get("severity") == "critical"]
    advisory_missing = [req for req in missing if req.get("severity") != "critical"]
    override_used = bool(critical_missing and override_reason)

    if critical_missing and not override_used:
        gate_status = "blocked" if strictness in {"hard", "strict", "default"} else "advisory"
        safe_next_step = "Resolve missing critical requirements before execution, or rerun with override_reason when the user explicitly accepts the risk."
    elif override_used:
        gate_status = "override_accepted"
        safe_next_step = "Proceed only with the override rationale recorded in provenance/protocol outputs."
    elif advisory_missing:
        gate_status = "advisory"
        safe_next_step = "Proceed after recording advisory gaps in the report/protocol."
    else:
        gate_status = "pass"
        safe_next_step = "Proceed with the mapped EEGLAB method and preserve parameters/provenance."

    return {
        "method_profile_id": profile_id,
        "gate_status": gate_status,
        "official_requirements": official_requirements,
        "missing_requirements": missing,
        "critical_missing_requirements": critical_missing,
        "advisory_missing_requirements": advisory_missing,
        "not_recommended": profile.get("not_recommended", []),
        "safe_next_step": safe_next_step,
        "source_claim_ids": profile.get("source_claim_ids", []),
        "override_used": override_used,
        "override_reason": override_reason if override_used else "",
        "blocked_requirements_acknowledged": ([req["id"] for req in critical_missing] if override_used else []),
        "official_alignment": {
            "strictness": strictness,
            "source": "local_official_claim_map",
            "claim_count": len(profile.get("source_claim_ids", [])),
        },
    }
