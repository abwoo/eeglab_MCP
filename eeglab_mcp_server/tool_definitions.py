"""MCP Tool schema surface for the EEGLAB MCP server."""

from __future__ import annotations

from mcp.types import Tool

try:
    from .schemas import annotate_tools, workflow_tools
    from .tool_registry import validate_tool_definitions
except ImportError:  # pragma: no cover - direct script execution support
    from schemas import annotate_tools, workflow_tools
    from tool_registry import validate_tool_definitions


def build_tool_definitions() -> list[Tool]:
    """Build raw tool definitions with complete schemas for internal validation."""
    tools = [
        # ===== Category 1: data management =====
        Tool(
            name="eeglab_init",
            description="Initialize the EEGLAB environment. Must be called before any other EEGLAB operation."
            "Starts MATLAB and loads EEGLAB without the GUI."
            "Optionally pass the EEGLAB installation path; otherwise the EEGLAB_PATH environment variable is used.",
            input_schema={
                "type": "object",
                "properties": {
                    "eeglab_path": {
                        "type": "string",
                        "description": "Absolute path of the EEGLAB installation directory, for example C:/eeglab2024.0 or /home/user/eeglab",
                    }
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_load_data",
            description="Load an EEG data file. Supports the native EEGLAB formats (.set/.fdt), BrainVision (.vhdr),"
            "EDF/EDF+ (.edf), BioSemi (.bdf), Neuroscan (.cnt) and similar formats."
            "After loading, the data is stored in the EEG variable of the MATLAB workspace and is available to later analysis tools.",
            input_schema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Absolute path of the EEG data file, for example C:/data/subject01.set",
                    },
                    "filename": {
                        "type": "string",
                        "description": "File name, needed when filepath points at a directory only, for example subject01.set",
                    },
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="eeglab_save_data",
            description="Save the current EEG data to a .set file."
            "Saving after a destructive operation such as filtering or ICA artifact removal is recommended.",
            input_schema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Absolute path of the file to save, for example C:/data/subject01_filtered.set",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Name of the file to save, for example subject01_filtered.set",
                    },
                },
                "required": ["filepath"],
            },
        ),
        Tool(
            name="eeglab_import_bids",
            description="Import a BIDS dataset. BIDS (Brain Imaging Data Structure) is the standard for organizing neuroscience data."
            "A STUDY and ALLEEG are created on import so that group-level analysis is possible.",
            input_schema={
                "type": "object",
                "properties": {
                    "bids_path": {
                        "type": "string",
                        "description": "Absolute path of the BIDS dataset root directory",
                    },
                    "study_name": {
                        "type": "string",
                        "default": "MyStudy",
                        "description": "STUDY name",
                    },
                },
                "required": ["bids_path"],
            },
        ),
        Tool(
            name="eeglab_info",
            description="Return details of the current EEG dataset, including channel count, sampling rate, data points, trial count,"
            "time window, channel labels, event types and ICA status. Use it to survey the data and to verify processing results.",
            input_schema={
                "type": "object",
                "properties": {
                    "include_channels": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include the list of channel labels",
                    },
                    "include_events": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include the list of event types",
                    },
                    "include_ica": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include ICA information",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_history",
            description="Return the operation history of the current EEG dataset, recording every EEGLAB operation since the data was loaded."
            "Use it to trace the analysis flow, to verify processing steps and to reproduce an analysis.",
            input_schema={"type": "object", "properties": {}, "required": []},
        ),
        # ===== Category 2: preprocessing =====
        Tool(
            name="eeglab_filter",
            description="Filter the EEG data. Supports bandpass, highpass, lowpass and notch filtering."
            "It uses the EEGLAB-recommended pop_eegfiltnew (FIR, Hamming window) and pop_cleanline (notch)."
            "Guidance: use a 0.1-40 Hz bandpass for ERP work and a 0.5-80 Hz bandpass for time-frequency work; "
            "notch out line noise at 50 Hz (China/Europe) or 60 Hz (US); a 1 Hz highpass before ICA is recommended.",
            input_schema={
                "type": "object",
                "properties": {
                    "filter_type": {
                        "type": "string",
                        "enum": ["bandpass", "highpass", "lowpass", "notch"],
                        "description": "Filter type: bandpass, highpass, lowpass or notch",
                    },
                    "low_cutoff": {
                        "type": "number",
                        "description": "Low cutoff in Hz, required for bandpass and highpass. Common values: 0.1 to remove drift, 0.5, 1 (recommended before ICA)",
                    },
                    "high_cutoff": {
                        "type": "number",
                        "description": "High cutoff in Hz, required for bandpass and lowpass. Common values: 30, 40, 80, 100",
                    },
                    "notch_freq": {
                        "type": "number",
                        "description": "Notch frequency in Hz, required when the type is notch. 50 (China/Europe) or 60 (US)",
                    },
                    "notch_harmonics": {
                        "type": "boolean",
                        "default": True,
                        "description": "Also remove the harmonics of the notch frequency, for example 100 Hz and 150 Hz",
                    },
                },
                "required": ["filter_type"],
            },
        ),
        Tool(
            name="eeglab_resample",
            description="Resample the EEG data. Lowering the sampling rate reduces both the data size and the computation time."
            "Guidance: apply a lowpass anti-aliasing filter before downsampling; common target rates are 250 Hz for ERP and 500 Hz for time-frequency work.",
            input_schema={
                "type": "object",
                "properties": {
                    "new_srate": {
                        "type": "number",
                        "description": "Target sampling rate in Hz, for example 250 or 500",
                    }
                },
                "required": ["new_srate"],
            },
        ),
        Tool(
            name="eeglab_reref",
            description="Re-reference the EEG data. Supports average reference (the mean of all channels), a single-channel reference such as Cz or a mastoid electrode, and REST reference."
            "Guidance: average reference is the most common choice and suits most research settings; "
            "average reference reduces the data rank by 1, so set pca=nchan-1 for ICA; "
            "ICA is usually run before re-referencing, or with average reference.",
            input_schema={
                "type": "object",
                "properties": {
                    "ref_type": {
                        "type": "string",
                        "enum": ["average", "channel", "rest"],
                        "description": "Reference type: average, channel or rest",
                    },
                    "ref_channel": {
                        "type": "string",
                        "description": "Reference channel label, required when ref_type is channel, for example 'Cz', 'M1', 'A1'",
                    },
                },
                "required": ["ref_type"],
            },
        ),
        Tool(
            name="eeglab_select_channels",
            description="Select or exclude specific channels, either to drop bad channels or to keep only a region of interest."
            "Guidance: drop clearly bad channels before ICA while keeping enough channels; "
            "removing channels before ICA lowers the number of components.",
            input_schema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channel labels to keep, for example ['Fz','Cz','Pz']. Mutually exclusive with exclude_channels",
                    },
                    "exclude_channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channel labels to exclude, for example ['EOG1','EOG2','EMG']. Mutually exclusive with channels",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_interpolate_channels",
            description="Interpolate channels, estimating the signal of a bad channel from its neighbours with spherical splines."
            "Guidance: run this after ICA artifact removal rather than before; "
            "urchanlocs can restore channels that were removed earlier.",
            input_schema={
                "type": "object",
                "properties": {
                    "ref_chanlocs": {
                        "type": "string",
                        "description": "Channel locations to reference: 'urchanlocs' restores the original channels, or give the path of a .loc file. Leave empty to use the current channel locations",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["spherical", "v4"],
                        "default": "spherical",
                        "description": "Interpolation method: spherical (spherical splines, recommended) or v4 (biharmonic splines)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_edit_channels",
            description="Edit channel information, for example loading a .loc location file or renaming channels."
            "Guidance: check the channel locations after loading, otherwise topomaps and source results will be wrong.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["load_loc", "rename"],
                        "description": "Action: load_loc to load a location file, or rename to rename channels",
                    },
                    "loc_file": {
                        "type": "string",
                        "description": "Path of the channel location file (.loc/.ced), required when action is load_loc",
                    },
                    "rename_map": {
                        "type": "object",
                        "description": 'Rename map keyed by the old name with the new name as the value, required when action is rename, for example {"Fp1":"E1", "Fp2":"E2"}',
                    },
                },
                "required": ["action"],
            },
        ),
        Tool(
            name="eeglab_clean_line_noise",
            description="Dedicated line-noise removal, using pop_cleanline from the clean_rawdata plugin."
            "It is more accurate than plain notch filtering because it estimates the line noise and its harmonics adaptively."
            "It needs the clean_rawdata plugin. Guidance: prefer this tool when the data has clear 50/60 Hz line noise.",
            input_schema={
                "type": "object",
                "properties": {
                    "line_freq": {
                        "type": "number",
                        "default": 50,
                        "description": "Line noise frequency in Hz: 50 (China/Europe) or 60 (US)",
                    },
                    "bandwidth": {
                        "type": "number",
                        "default": 2,
                        "description": "Notch bandwidth in Hz",
                    },
                    "tau": {
                        "type": "number",
                        "default": 100,
                        "description": "Smoothing parameter tau",
                    },
                    "winsize": {
                        "type": "number",
                        "default": 4,
                        "description": "Window size in seconds",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_clean_rawdata",
            description="ASR (Artifact Subspace Reconstruction) artifact removal, using the clean_rawdata plugin."
            "It detects and repairs bad channels and removes high-amplitude artifacts automatically."
            "Guidance: run it on continuous data before epoching; using it before ICA improves ICA quality; "
            "burst_criterion: 5 is aggressive, 20 conservative, 40 mild. It needs the clean_rawdata plugin.",
            input_schema={
                "type": "object",
                "properties": {
                    "flatline_criterion": {
                        "type": "number",
                        "default": 5,
                        "description": "Flatline detection threshold in seconds. A channel whose signal standard deviation stays near zero for this long is marked as bad",
                    },
                    "channel_criterion": {
                        "type": "number",
                        "default": 0.8,
                        "description": "Bad-channel detection threshold as a correlation coefficient. Channels below this value are marked as bad",
                    },
                    "line_noise_criterion": {
                        "type": "number",
                        "default": 4,
                        "description": "Line-noise detection threshold in Z units",
                    },
                    "burst_criterion": {
                        "type": "number",
                        "default": 20,
                        "description": "Burst artifact detection threshold in Z units: 5 is aggressive, 20 conservative, 40 mild",
                    },
                    "window_criterion": {
                        "type": "number",
                        "default": 0.25,
                        "description": "Bad-segment detection threshold as a proportion. Windows above this proportion are marked as bad segments",
                    },
                },
                "required": [],
            },
        ),
        # ===== Category 3: ICA and artifact handling =====
        Tool(
            name="eeglab_run_ica",
            description="Run an ICA (independent component analysis) decomposition on the EEG data. ICA separates brain sources from artifact components such as ocular, muscle and cardiac activity."
            "Guidance: a 1 Hz highpass before ICA is recommended; do not baseline-correct before ICA; "
            "average reference reduces the rank by 1, so set pca=nchan-1; "
            "runica and picard ship with EEGLAB, while fastica needs a separate plugin.",
            input_schema={
                "type": "object",
                "properties": {
                    "algorithm": {
                        "type": "string",
                        "enum": ["runica", "picard"],
                        "default": "runica",
                        "description": "ICA algorithm: runica (Infomax, stable by default) or picard (a balance of speed and accuracy, recommended)",
                    },
                    "pca_components": {
                        "type": "integer",
                        "description": "Number of components after PCA reduction. Leave empty to use the channel count. After average reference, nchan-1 is recommended",
                    },
                    "extended": {
                        "type": "boolean",
                        "default": True,
                        "description": "Use extended Infomax, which can separate super- and sub-Gaussian sources. Enabling it improves muscle artifact separation",
                    },
                    "max_steps": {
                        "type": "integer",
                        "default": 512,
                        "description": "Maximum number of iterations. Defaults to 512; 1000 to 2000 is reasonable for large datasets",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_classify_ica",
            description="Classify ICA components automatically with ICLabel. ICLabel is a deep-learning based classifier that "
            "assigns each component to one of seven classes: Brain, Muscle, Eye, Heart, "
            "Line_Noise, Channel_Noise and Other."
            "The result carries the probability of each class for every component. Run the ICA decomposition first. It needs the ICLabel plugin.",
            input_schema={"type": "object", "properties": {}, "required": []},
        ),
        Tool(
            name="eeglab_flag_components",
            description="Mark ICA components from the ICLabel probabilities. Set a probability threshold per class to decide which components count as artifacts."
            "Guidance: a common strategy marks components whose Brain probability is below 0.2, or whose Muscle or Eye probability is above 0.8.",
            input_schema={
                "type": "object",
                "properties": {
                    "brain_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Brain class probability range [min, max]; components outside it are marked, for example [0, 0.2] marks Brain below 20%",
                    },
                    "muscle_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Muscle class probability range [min, max]; components inside it are marked, for example [0.8, 1] marks Muscle above 80%",
                    },
                    "eye_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Eye class probability range [min, max], for example [0.8, 1]",
                    },
                    "heart_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Heart class probability range [min, max], for example [0.8, 1]",
                    },
                    "line_noise_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Line_Noise class probability range [min, max]",
                    },
                    "channel_noise_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Channel_Noise class probability range [min, max]",
                    },
                    "other_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Other class probability range [min, max]",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_remove_components",
            description="Remove selected ICA artifact components and rebuild the EEG data, either from the ICLabel classification or from a manual selection, dropping "
            "non-brain components such as ocular, muscle, cardiac and line noise."
            "This is the core step of ICA artifact removal. Run eeglab_classify_ica first to see the classification before deciding what to remove.",
            input_schema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Indices of the IC components to remove, counted from 1, for example [2, 5, 7, 10]",
                    },
                    "auto_remove_brain_threshold": {
                        "type": "number",
                        "description": "Automatic removal mode: components whose Brain probability is below this threshold are removed. For example 0.3 keeps the components with a Brain probability of 30 percent or more. Leave empty to use the manual component_indices",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_reject_epochs",
            description="Reject trials. Reject artifact-contaminated trials by threshold or by joint probability."
            "Guidance: use it after epoching; set the threshold from the data amplitude, usually plus or minus 100 microvolts; "
            "the joint probability method detects abnormalities that are only visible across channels.",
            input_schema={
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["threshold", "joint_probability"],
                        "default": "threshold",
                        "description": "Rejection method: threshold or joint_probability",
                    },
                    "threshold": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-100, 100],
                        "description": "Threshold range [lower microvolts, upper microvolts], used when method is threshold",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to inspect. Leave empty to use all channels",
                    },
                    "jp_threshold": {
                        "type": "number",
                        "default": 3,
                        "description": "Z threshold for joint probability, used when method is joint_probability",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_get_events",
            description="Return event information for the current EEG dataset, listing the available event types and their counts."
            "Use it to find out which markers the data contains before epoching and analysis.",
            input_schema={"type": "object", "properties": {}, "required": []},
        ),
        # ===== Category 4: epoching and ERP =====
        Tool(
            name="eeglab_epoch",
            description="Epoch the continuous EEG data and apply baseline correction, cutting the data into trials by event type."
            "Epoching is required for ERP analysis. Guidance: common windows are [-200, 800] ms for P300 and "
            "[-200, 500] ms for N170; baseline correction removes the DC offset over the pre-stimulus period; "
            "the baseline window is usually the same as the pre-stimulus window.",
            input_schema={
                "type": "object",
                "properties": {
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event types to epoch on, for example ['target', 'standard']. Leave empty to use all events",
                    },
                    "pre_stimulus": {
                        "type": "number",
                        "default": -0.2,
                        "description": "Pre-stimulus time window in seconds, for example -0.2 for the 200 ms before the stimulus",
                    },
                    "post_stimulus": {
                        "type": "number",
                        "default": 0.8,
                        "description": "Post-stimulus time window in seconds, for example 0.8 for the 800 ms after the stimulus",
                    },
                    "baseline_start": {
                        "type": "number",
                        "default": -0.2,
                        "description": "Baseline correction start in seconds, usually the same as pre_stimulus",
                    },
                    "baseline_end": {
                        "type": "number",
                        "default": 0,
                        "description": "Baseline correction end in seconds, usually 0 at stimulus onset",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_erp_analysis",
            description="ERP (event-related potential) analysis. Computes the average ERP waveform per condition, with grouping by condition, "
            "channel selection and a configurable time window. It reports the mean, the peak and the latency for each condition and channel."
            "Guidance: common ERP components are N1 at 80-150 ms, P2 at 150-280 ms, "
            "N170 at 140-200 ms over temporo-occipital sites, P300 at 250-500 ms over centro-parietal sites and N400 at 300-500 ms over central sites.",
            input_schema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to analyse, for example ['Fz', 'Cz', 'Pz']. Leave empty to analyse all channels",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Analysis time window [start ms, end ms], for example [250, 500] to analyse the P300 component",
                    },
                    "peak_detection": {
                        "type": "boolean",
                        "default": True,
                        "description": "Detect the peak, that is the largest positive and the largest negative wave, inside the given time window",
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Analyse grouped by condition. Leave empty to average across all trials",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_sort_epochs",
            description="Sort trials by condition, grouping and ordering the trials by event type so that the grouped analysis can follow."
            "Guidance: use it after epoching; once the trials are sorted, eeglab_erp_analysis can analyse them by condition.",
            input_schema={
                "type": "object",
                "properties": {
                    "sort_by": {
                        "type": "string",
                        "description": "Event type field name to sort on, for example 'type'",
                    }
                },
                "required": ["sort_by"],
            },
        ),
        Tool(
            name="eeglab_average_erp",
            description="Average the ERP, computing the average ERP waveform per condition."
            "Guidance: usually run after epoching and baseline correction; "
            "it can group by event type to average the ERP per condition.",
            input_schema={
                "type": "object",
                "properties": {
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Group by condition. Leave empty to average across all trials",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to average. Leave empty to average all channels",
                    },
                },
                "required": [],
            },
        ),
        # ===== Category 5: frequency domain and time-frequency =====
        Tool(
            name="eeglab_spectral",
            description="Spectral or power spectral density (PSD) analysis, computing the power spectral density of each channel with the Welch method."
            "It reports the absolute and the relative power of the Delta, Theta, Alpha, Beta and Gamma bands."
            "Guidance: the bands are Delta 0.5-4 Hz, Theta 4-8 Hz, Alpha 8-13 Hz, "
            "Beta 13-30 Hz and Gamma 30-80 Hz; this tool is the usual choice for resting-state analysis.",
            input_schema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to analyse, for example ['Oz', 'Pz']. Leave empty to analyse all channels",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [0.5, 100],
                        "description": "Frequency range [lowest Hz, highest Hz]. Defaults to [0.5, 100]",
                    },
                    "band_power": {
                        "type": "boolean",
                        "default": True,
                        "description": "Compute the band power of the Delta, Theta, Alpha, Beta and Gamma bands",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_timefreq",
            description="Time-frequency analysis. Computes the event-related spectral perturbation (ERSP) and the inter-trial coherence (ITC) of the EEG signal."
            "It supports the Morlet wavelet transform."
            "ERSP reflects how the energy of each band varies over time, while ITC reflects how strongly the phase is locked in each band."
            "Guidance: a frequency range of 3-80 Hz with 3-10 cycles growing linearly from low to high frequency; "
            "it needs epoched data.",
            input_schema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to analyse, for example ['Cz', 'Pz']. Leave empty to analyse all channels",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [3, 80],
                        "description": "Frequency range [lowest Hz, highest Hz], for example [3, 80]",
                    },
                    "cycles": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 3,
                        "default": [3, 10],
                        "description": "Number of wavelet cycles. Two values: [start, end]; three values: [start, step, end]. Defaults to [3, 10]",
                    },
                    "baseline": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-200, 0],
                        "description": "Baseline window [start ms, end ms]. Defaults to [-200, 0], the 200 ms before the stimulus",
                    },
                    "output_type": {
                        "type": "string",
                        "enum": ["ersp", "itc", "both"],
                        "default": "both",
                        "description": "Output type: ersp for power only, itc for phase consistency only, or both",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_connectivity",
            description="Functional connectivity analysis, computing the coherence and the phase locking value (PLV) between channels."
            "Guidance: coherence reflects the linear relationship between two signals at a given frequency; "
            "PLV reflects phase synchronisation; both are common in resting-state brain network analysis.",
            input_schema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to analyse. Leave empty to analyse all channels",
                    },
                    "method": {
                        "type": "string",
                        "enum": ["coherence", "plv"],
                        "default": "coherence",
                        "description": "Connectivity measure: coherence or plv",
                    },
                    "freq_range": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [8, 13],
                        "description": "Frequency range [lowest Hz, highest Hz]. Defaults to [8, 13], the Alpha band",
                    },
                },
                "required": [],
            },
        ),
        # ===== Category 6: visualization =====
        Tool(
            name="eeglab_topoplot",
            description="Plot a scalp topomap, showing the distribution of the EEG signal over the scalp as contour lines."
            "It can plot the average potential at a given time point or across a time window. The figure is saved as a PNG file.",
            input_schema={
                "type": "object",
                "properties": {
                    "time_point": {
                        "type": "number",
                        "description": "Time point to plot in ms, for example 300 for the 300 ms after the stimulus. Mutually exclusive with time_window",
                    },
                    "time_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "description": "Average over the plotted time window [start ms, end ms], for example [250, 350] for the P300 window. Mutually exclusive with time_point",
                    },
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to plot. Leave empty to use all channels",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Absolute path of the output image, for example C:/results/topo_300ms.png",
                    },
                    "title": {"type": "string", "description": "Figure title"},
                },
                "required": ["output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_erp",
            description="Plot ERP waveforms, showing the average ERP waveform of the given channels."
            "It can plot per condition and can add confidence intervals. The figure is saved as a PNG file.",
            input_schema={
                "type": "object",
                "properties": {
                    "channels": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Channels to plot, for example ['Fz', 'Cz', 'Pz']",
                    },
                    "conditions": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Plot per condition. Leave empty to plot the average across all trials",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Absolute path of the output image",
                    },
                    "title": {"type": "string", "description": "Figure title"},
                },
                "required": ["channels", "output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_timefreq",
            description="Plot time-frequency figures, showing the ERSP and/or ITC of the given channel."
            "Run eeglab_timefreq first to obtain the time-frequency data. The figure is saved as a PNG file.",
            input_schema={
                "type": "object",
                "properties": {
                    "channel": {
                        "type": "string",
                        "description": "Channel label to plot, for example 'Cz'",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Absolute path of the output image",
                    },
                    "plot_ersp": {
                        "type": "boolean",
                        "default": True,
                        "description": "Plot the ERSP figure",
                    },
                    "plot_itc": {
                        "type": "boolean",
                        "default": True,
                        "description": "Plot the ITC figure",
                    },
                    "title": {"type": "string", "description": "Figure title"},
                },
                "required": ["channel", "output_path"],
            },
        ),
        Tool(
            name="eeglab_plot_components",
            description="Plot ICA component figures, showing the scalp topomap and the power spectrum of each component."
            "Use them to inspect the components and to judge their nature by hand. The figures are saved as PNG files."
            "Guidance: run the ICA decomposition first, and combine the figures with the ICLabel classification to judge the components.",
            input_schema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Indices of the IC components to plot, counted from 1. Leave empty to plot the first 10",
                    },
                    "output_path": {
                        "type": "string",
                        "description": "Absolute path of the output image",
                    },
                    "title": {"type": "string", "description": "Figure title"},
                },
                "required": ["output_path"],
            },
        ),
        # ===== Category 7: source localization =====
        Tool(
            name="eeglab_source_localization",
            description="Source localization by dipole fitting, using the Dipfit tool built into EEGLAB to fit dipoles to the ICA components "
            "and estimate where the intracranial sources sit. Run the ICA decomposition first."
            "It reports the MNI coordinates of the dipoles, the residual variance and more. Guidance: the channel locations must be correct before fitting; "
            "a residual variance below 15 percent means a good fit. It needs the Dipfit plugin, which ships with EEGLAB.",
            input_schema={
                "type": "object",
                "properties": {
                    "component_indices": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Indices of the IC components to fit. Leave empty to fit every component",
                    },
                    "head_model": {
                        "type": "string",
                        "enum": ["bem", "spherical"],
                        "default": "bem",
                        "description": "Head model type: bem (boundary element model, recommended) or spherical (spherical model, fast)",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["mni", "colin27"],
                        "default": "mni",
                        "description": "Template brain: mni (MNI305, default) or colin27 (the high-resolution Colin27)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_source_settings",
            description="Dipfit model settings, configuring the head model, the template brain and the channel location file."
            "Guidance: set the correct parameters before running source localization; "
            "the BEM model is more accurate but slower, while the spherical model is fast but less accurate.",
            input_schema={
                "type": "object",
                "properties": {
                    "head_model": {
                        "type": "string",
                        "enum": ["bem", "spherical"],
                        "default": "bem",
                        "description": "Head model type: bem (boundary element model) or spherical (spherical model)",
                    },
                    "template": {
                        "type": "string",
                        "enum": ["mni", "colin27"],
                        "default": "mni",
                        "description": "Template brain: mni (MNI305) or colin27 (Colin27)",
                    },
                    "chanfile": {
                        "type": "string",
                        "description": "Channel location file path. Leave empty to use the default",
                    },
                    "mrifile": {
                        "type": "string",
                        "description": "MRI template file path. Leave empty to use the default",
                    },
                },
                "required": [],
            },
        ),
        # ===== Category 8: group analysis and pipelines =====
        Tool(
            name="eeglab_study_create",
            description="Create an EEGLAB STUDY for group-level analysis, either from a BIDS directory or from several .set files."
            "Guidance: the STUDY is the basis for group-level analysis in EEGLAB; "
            "the experimental design must be defined before any statistical test.",
            input_schema={
                "type": "object",
                "properties": {
                    "bids_path": {
                        "type": "string",
                        "description": "Path of the BIDS dataset root. Mutually exclusive with dataset_paths",
                    },
                    "study_name": {
                        "type": "string",
                        "default": "MyStudy",
                        "description": "STUDY name",
                    },
                    "dataset_paths": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of EEG data file paths. Mutually exclusive with bids_path",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_study_design",
            description="Define the STUDY experimental design, setting the independent variables and their levels for the later statistical test."
            "Guidance: the design must be defined before the statistical test; "
            "several independent variables can be defined, for example group by condition.",
            input_schema={
                "type": "object",
                "properties": {
                    "design_name": {
                        "type": "string",
                        "default": "Design1",
                        "description": "Design name",
                    },
                    "variable_name": {
                        "type": "string",
                        "default": "condition",
                        "description": "Independent variable name, for example 'condition' or 'group'",
                    },
                    "variable_values": {
                        "type": "array",
                        "items": {"type": "string"},
                        "default": ["target", "standard"],
                        "description": "Levels of the independent variable, for example ['control', 'patient'] or ['target', 'standard']",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_study_statistics",
            description="STUDY statistical test, using a cluster permutation test for group-level statistical inference."
            "Guidance: a cluster permutation test controls multiple comparisons effectively; "
            "the usual thresholds are p below 0.05 with FDR or FWE correction at the cluster level.",
            input_schema={
                "type": "object",
                "properties": {
                    "measure": {
                        "type": "string",
                        "enum": ["erp", "spectrum", "ersp"],
                        "default": "erp",
                        "description": "Measurement type for the test: erp for the ERP waveform, spectrum, or ersp for time-frequency",
                    },
                    "alpha": {
                        "type": "number",
                        "default": 0.05,
                        "description": "Significance level. Defaults to 0.05",
                    },
                    "correction": {
                        "type": "string",
                        "enum": ["fdr", "bonferroni", "cluster", "none"],
                        "default": "fdr",
                        "description": "Multiple comparison correction: fdr, bonferroni, cluster or none",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="eeglab_pipeline",
            description="Generate a complete pipeline. It builds the full preprocessing and analysis pipeline for the chosen analysis type."
            "It supports the ERP, resting-state and time-frequency pipelines."
            "Guidance: the ERP pipeline is filter, ASR, re-reference, ICA, ICLabel, artifact removal, interpolation, epoch, baseline, save; "
            "the resting-state pipeline is filter, ASR, re-reference, ICA, ICLabel, artifact removal, spectral analysis, save.",
            input_schema={
                "type": "object",
                "properties": {
                    "pipeline_type": {
                        "type": "string",
                        "enum": ["erp", "resting", "timefreq"],
                        "description": "Pipeline type: erp, resting or timefreq",
                    },
                    "data_path": {"type": "string", "description": "Path of the input data file"},
                    "output_dir": {
                        "type": "string",
                        "description": "Output directory. Leave empty to use the working directory",
                    },
                    "highpass": {
                        "type": "number",
                        "default": 1.0,
                        "description": "Highpass cutoff in Hz. Defaults to 1.0, which is recommended before ICA",
                    },
                    "lowpass": {
                        "type": "number",
                        "default": 40.0,
                        "description": "Lowpass cutoff in Hz. Defaults to 40.0",
                    },
                    "event_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Event types used for epoching, when pipeline_type is erp or timefreq",
                    },
                    "epoch_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-0.2, 0.8],
                        "description": "Epoching window [start seconds, end seconds]. Defaults to [-0.2, 0.8]",
                    },
                    "baseline_window": {
                        "type": "array",
                        "items": {"type": "number"},
                        "minItems": 2,
                        "maxItems": 2,
                        "default": [-200, 0],
                        "description": "Baseline correction window [start ms, end ms]. Defaults to [-200, 0]",
                    },
                    "ica_algorithm": {
                        "type": "string",
                        "enum": ["runica", "picard"],
                        "default": "picard",
                        "description": "ICA algorithm. Defaults to picard",
                    },
                    "burst_criterion": {
                        "type": "number",
                        "default": 20,
                        "description": "ASR burst artifact detection threshold: 5 is aggressive, 20 conservative, 40 mild",
                    },
                },
                "required": ["pipeline_type", "data_path"],
            },
        ),
    ]
    all_tools = annotate_tools(tools + workflow_tools())
    registry_errors = validate_tool_definitions(all_tools)
    if registry_errors:
        raise RuntimeError("Tool registry mismatch: " + "; ".join(registry_errors))
    return all_tools
