# Connectivity Advanced Figure Gallery

This default module keeps the connectivity figure families visible and aligned to the official spectral, topography, source, and SIFT guidance.

## Default Status

- Default enabled: yes
- Python module: `scripts/advanced_figures/connectivity_gallery.py`
- Markdown guide: `scripts/advanced_figures/connectivity.md`
- Default MCP route: `eeglab_plot_connectivity / eeglab_plot_psd / eeglab_topoplot`

## Figure Families

| Figure family | Status | Official anchor | Official URL | MCP tool | Official scope |
| --- | --- | --- | --- | --- | --- |
| Connectivity matrix / network | required | `EEGLAB-SPECTRAL-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_plot_connectivity` | Sensor-level connectivity summary, not anatomical connectivity. |
| Band-power topomaps | conditional | `EEGLAB-TOPO-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_topoplot` | Frequency-band scalp distribution. |
| Channel spectra + maps | required | `EEGLAB-SPECTRAL-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_plot_psd` | Channel and ROI power profile used to contextualize connectivity. |
| ROI connectivity matrix | conditional | `EEGLAB-ROICONNECT-001` | `https://eeglab.org/plugins/roiconnect/` | `eeglab_plot_connectivity` | ROI-level functional connectivity summary. |
| SIFT connectivity summary | guidance_only | `EEGLAB-SIFT-001` | `https://eeglab.org/plugins/SIFT/` | `SIFT` | Model-based connectivity summary only. |

