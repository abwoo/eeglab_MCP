# EEG Figure Atlas

This document defines the strict figure policy for EEG/EEGLAB branch workflows.
Static figures are the default executable baseline. Movie and animation outputs are guidance-only unless a dedicated workflow and report path are added.

## Figure Metadata

Every figure record should carry these fields:

- `figure_type`
- `branch_id`
- `branch_mode`
- `branch_variant`
- `figure_status`
- `channel_or_roi`
- `latency_window`
- `frequency_window`
- `tool_source`
- `official_anchor`
- `official_url`
- `interpretation_scope`
- `figure_path`

## Branch Figure Atlas

### ERP

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| ERP waveform | required | `eeglab_plot_erp` | `EEGLAB-ERP-001`, `Data_Averaging.html` | Mean amplitude and latency comparison across conditions |
| ERP image heatmap | conditional | `eeglab_plot_erp` / `erpimage` | `EEGLAB-ERP-001`, `EEGLAB-EVENT-001`, `Plotting_ERP_images.html` | Single-trial sorting, RT/phase review, variance diagnostics |
| 2-D / 3-D scalp map series | required | `eeglab_topoplot` | `EEGLAB-TOPO-001`, `Data_Averaging.html`, `Using_EEGLAB_history.html` | Latency-specific scalp distribution |
| Difference-wave review | conditional | `eeglab_plot_erp` + `eeglab_topoplot` | `EEGLAB-ERP-001`, `EEGLAB-TOPO-001` | Polarity and latency sanity check |
| PSD review | required | `eeglab_plot_psd` | `EEGLAB-SPECTRAL-001`, `Plotting_Channel_Spectra_and_Maps.html` | Broad spectral sanity check |

### Resting-State Spectral / Connectivity

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| Channel spectra + maps | required | `eeglab_plot_psd` | `EEGLAB-SPECTRAL-001`, `Plotting_Channel_Spectra_and_Maps.html` | Channel/ROI power profile |
| Band-power topomaps | conditional | `eeglab_topoplot` | `EEGLAB-TOPO-001`, `Plotting_Channel_Spectra_and_Maps.html` | Frequency-band scalp distribution |
| Connectivity matrix / network | conditional | `eeglab_plot_connectivity` | `EEGLAB-SPECTRAL-001`, `EEGLAB-ROICONNECT-001`, `EEGLAB-SIFT-001` | Sensor/ROI summary, not anatomical connectivity |

### Connectivity

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| Connectivity matrix / network | required | `eeglab_plot_connectivity` | `EEGLAB-SPECTRAL-001`, `EEGLAB-ROICONNECT-001`, `EEGLAB-SIFT-001` | Sensor/ROI summary, not anatomical connectivity |
| Connectivity threshold sweep | conditional | `eeglab_plot_connectivity` | `EEGLAB-SPECTRAL-001`, `EEGLAB-ROICONNECT-001` | Stability check for reported network structure |
| Channel spectra + maps | required | `eeglab_plot_psd` | `EEGLAB-SPECTRAL-001`, `Plotting_Channel_Spectra_and_Maps.html` | Channel/ROI power profile |
| Band-power topomaps | conditional | `eeglab_topoplot` | `EEGLAB-TOPO-001`, `Plotting_Channel_Spectra_and_Maps.html` | Frequency-band scalp distribution |

### Time-Frequency

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| ERSP / ITC heatmap | required | `eeglab_plot_timefreq` | `EEGLAB-TF-001`, `Time-Frequency_decomposition.html` | Event-locked power and phase dynamics |
| Time-frequency curves | conditional | `eeglab_plot_timefreq` | `EEGLAB-TF-001`, `Time-Frequency_decomposition.html` | Frequency-specific time courses |
| All-electrode `tftopo` summary | guidance_only | `tftopo` | `EEGLAB-TF-001`, `EEG_scalp_measures.html` | Multi-electrode summary, static only |
| `metaplottopo` summary | guidance_only | `metaplottopo` | `EEGLAB-TF-001`, `EEG_scalp_measures.html` | Channel-grid summary, static only |

### ICA

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| Component spectra | required | `eeglab_plot_components` | `EEGLAB-ICA-001`, `Plotting_ICA_components.html` | Component spectral contribution |
| Component ERP envelopes | conditional | `eeglab_plot_components` | `EEGLAB-ICA-001`, `Plotting_ICA_components.html` | Component contribution to ERP morphology |
| Component ERP-image | conditional | `eeglab_plot_components` / `erpimage` | `EEGLAB-ICA-001`, `Plotting_ICA_components.html` | Single-component trial sorting |
| Component time-frequency | conditional | `eeglab_plot_timefreq` | `EEGLAB-ICA-001`, `EEGLAB-TF-001`, `Plotting_ICA_components.html`, `Time-Frequency_decomposition.html` | Component ERSP / ITC dynamics |
| Component head plots | required | `eeglab_plot_components` | `EEGLAB-ICA-001`, `EEGLAB-TOPO-001`, `Plotting_ICA_components.html` | Component scalp projection review |

### Source / Connectivity

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| Source / dipole review | required | `eeglab_source_localization` | `EEGLAB-DIPFIT-001`, `eeglab.org/plugins/dipfit/` | Model fit quality and residual variance review |
| ROI connectivity matrix | conditional | `eeglab_plot_connectivity` | `EEGLAB-ROICONNECT-001`, `eeglab.org/plugins/roiconnect/` | ROI-level functional connectivity summary |
| ROI 2-D / 3-D review | guidance_only | `ROIconnect` | `EEGLAB-ROICONNECT-001`, `eeglab.org/plugins/roiconnect/` | Source-space review aid only |
| SIFT time-frequency grids | guidance_only | `SIFT` | `EEGLAB-SIFT-001`, `eeglab.org/plugins/SIFT/` | Model-based connectivity summary only |

### STUDY / Group Analysis

| Figure family | Status | Tool source | Official anchors | Interpretation scope |
| --- | --- | --- | --- | --- |
| Grand-average ERP | required | `eeglab_plot_erp` | `EEGLAB-STUDY-001`, `study_data_visualization_tools.html` | Group-level ERP summary |
| All-channel ERP | conditional | `eeglab_plot_erp` | `EEGLAB-STUDY-001`, `study_data_visualization_tools.html` | Channel-wide ERP review |
| Spectra / scalp maps | conditional | `eeglab_plot_psd`, `eeglab_topoplot` | `EEGLAB-STUDY-001`, `EEGLAB-STUDY-PRECOMP-001`, `study_data_visualization_tools.html` | Group spectral summary |
| ERP-image | conditional | `eeglab_plot_erp` / `erpimage` | `EEGLAB-STUDY-001`, `study_data_visualization_tools.html`, `Plotting_ERP_images.html` | Trial-level or subject-level sorting review |
| ERSP / ITC | conditional | `eeglab_plot_timefreq` | `EEGLAB-STUDY-001`, `EEGLAB-STUDY-PRECOMP-001`, `study_data_visualization_tools.html`, `Time-Frequency_decomposition.html` | Group time-frequency summary |
| CI / contrast plots | conditional | `eeglab_study_statistics` | `EEGLAB-STUDY-001`, `study_statistics.html` | Statistical contrast review |
| Cluster / edge visuals | guidance_only | `eeglab_study_statistics` / `eeglab_protocol_export` | `EEGLAB-ICCLUSTER-001`, `EEGLAB-LIMO-001`, `component_clustering_tools.html` | Cluster review or edge visualization only |

## Output Rules

- Use real loaded EEG data and real project metadata only.
- Never fabricate figure paths, figure families, or interpretation scope.
- Keep static figures as the default executable output.
- Keep ERP waveform and ERP-image as separate but companion figure families: the waveform summarizes condition-average morphology, while the ERP-image inspects single-trial structure and latency ordering.
- Treat movie and animation outputs as guidance-only unless a dedicated workflow is added.
- Record the exact `figure_type`, `branch_id`, channel or ROI set, latency or frequency window, tool source, interpretation scope, and absolute file path for every generated figure.

## Cross-References

- `docs/official-report-field-matrix.md`
- `docs/canonical-session-checklist.md`
- `docs/homepage-session-order.md`
- `scripts/advanced_figures/`
- `skills/eeglab-analysis/references/branch-workflow-matrix.md`
