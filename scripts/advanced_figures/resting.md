# Resting-State Advanced Figure Gallery

This default module keeps the continuous-data figure families visible and
aligned to the official spectra and connectivity tutorials.

## Default Status

- Default enabled: yes
- Python module: `scripts/advanced_figures/resting_gallery.py`
- Markdown guide: `scripts/advanced_figures/resting.md`
- Default MCP route: `eeglab_plot_psd / eeglab_topoplot / eeglab_plot_connectivity`

## Figure Families

| Figure family | Status | Official anchor | Official URL | MCP tool | Official scope |
| --- | --- | --- | --- | --- | --- |
| Channel spectra + maps | required | `EEGLAB-SPECTRAL-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_plot_psd` | Channel and ROI power profile. |
| Band-power topomaps | conditional | `EEGLAB-TOPO-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_topoplot` | Frequency-band scalp distribution. |
| Connectivity matrix / network | conditional | `EEGLAB-SPECTRAL-001` | `https://eeglab.org/tutorials/08_Plot_data/Plotting_Channel_Spectra_and_Maps.html` | `eeglab_plot_connectivity` | Sensor-level summary, not anatomical connectivity. |
